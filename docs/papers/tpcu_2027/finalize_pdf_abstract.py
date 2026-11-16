#!/usr/bin/env python3
"""Apply the DOCX abstract's italic style when LO omits CJK font synthesis.

Preserves embedded fonts, searchable text, baselines and all other pages.
This is a vector shear of the existing glyphs, not a replacement font.
"""
import argparse
import math
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import FloatObject

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('output')
args = parser.parse_args()
with pdfplumber.open(args.input) as pdf:
    page = pdf.pages[0]
    lines = page.extract_text_lines()
    abstract = next(line for line in lines if line['text'] == '摘要')
    keywords = next(line for line in lines if line['text'] == '關鍵詞')
    top, bottom = abstract['bottom'], keywords['top']
    original_text = [''.join(c['text'] for c in p.chars) for p in pdf.pages]
    expected = [c for c in page.chars if top < c['top'] < bottom
                and 'BiauKaiTC' in c['fontname']]
    assert expected and all(abs(c['matrix'][2]) < 1e-8 for c in expected)
    low, high = page.height - bottom, page.height - top

reader = PdfReader(args.input)
writer = PdfWriter()
writer.clone_document_from_reader(reader)
writer.pdf_header = reader.pdf_header
page = writer.pages[0]
fonts = page['/Resources']['/Font']
stream = page.get_contents()
operations = stream.operations
changed = 0
start = None
for index, (operands, operator) in enumerate(operations):
    if operator == b'BT':
        start = index
    elif operator == b'ET' and start is not None:
        block = operations[start:index]
        font_ids = {str(a[0]) for a, op in block if op == b'Tf'}
        # Fail closed if the export structure changes to mixed-font objects.
        positions = [(i, a, op) for i, (a, op) in enumerate(block, start)
                     if op in (b'Td', b'Tm')]
        in_abstract = any(low < float(a[-1]) < high for _, a, _ in positions)
        cjk = [key for key in font_ids
               if 'BiauKaiTC' in str(fonts[key].get_object()['/BaseFont'])]
        if in_abstract and cjk:
            assert len(font_ids) == 1 and len(positions) == 1
            i, a, op = positions[0]
            x, y = a[-2:]
            if op == b'Tm':
                assert [float(v) for v in a[:4]] == [1, 0, 0, 1]
            operations[i] = ([FloatObject(v) for v in
                              (1, 0, math.tan(math.radians(12)), 1, x, y)], b'Tm')
            changed += 1
        start = None
assert changed > 0
stream.operations = operations
page.replace_contents(stream)
writer.write(args.output)
with pdfplumber.open(args.output) as pdf:
    assert original_text == [''.join(c['text'] for c in p.chars) for p in pdf.pages]
    actual = [c for c in pdf.pages[0].chars if top < c['top'] < bottom
              and 'BiauKaiTC' in c['fontname']]
    assert len(actual) == len(expected)
    assert all(abs(c['matrix'][2] - math.tan(math.radians(12))) < 1e-6 for c in actual)
print(f'Applied abstract CJK italics: {changed} text objects, {len(actual)} glyphs; text unchanged.')
