#!/usr/bin/env python3
"""Typeset the reviewed Markdown in the 2027 TPCU Word layout."""
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
LINES = (HERE / "manuscript_zh.md").read_text().splitlines()
OUT = HERE / "manuscript_zh.docx"


def font(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    rpr = run._element.get_or_add_rPr()
    rf = rpr.rFonts
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    rf.set(qn("w:eastAsia"), "BiauKaiTC")
    rf.set(qn("w:hint"), "eastAsia")
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), "en-US")
    lang.set(qn("w:eastAsia"), "zh-TW")


def para(doc, text, size=12, bold=False, italic=False, align=None,
         before=0, after=3, first_indent=0, keep_next=False):
    p = doc.add_paragraph()
    p.alignment = align or WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.0
    pf.first_line_indent = Pt(first_indent)
    pf.keep_with_next = keep_next
    pf.widow_control = True
    font(p.add_run(text), size, bold, italic)
    return p


def heading(doc, text):
    para(doc, text, 14, True, align=WD_ALIGN_PARAGRAPH.LEFT,
         before=7, after=3, keep_next=True)


def caption(doc, text, before=3, after=3):
    para(doc, text, 10, True, align=WD_ALIGN_PARAGRAPH.CENTER,
         before=before, after=after, keep_next=True)


def set_cell_text(cell, text, is_header=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_header else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    font(p.add_run(text), 10, is_header)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    tcpr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for side in ("top", "bottom", "left", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), "35" if side in ("top", "bottom") else "45")
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcpr.append(mar)


def add_table(doc, rows):
    n = len(rows[0])
    table = doc.add_table(rows=0, cols=n)
    table.autofit = False
    table.style = "Table Grid"
    widths = {2: [1.15, 6.38],
              3: [1.35, 1.35, 4.83],
              4: [1.05, 2.16, 2.16, 2.16],
              5: [1.12, 1.12, 1.25, 2.05, 1.99]}[n]
    for i, width in enumerate(widths):
        table.columns[i].width = Cm(width)
    tblw = table._tbl.tblPr.xpath("./w:tblW")[0]
    tblw.set(qn("w:w"), str(round(7.53 / 2.54 * 1440)))
    tblw.set(qn("w:type"), "dxa")
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(values):
            cells[i].width = Cm(widths[i])
            if n == 4 and row_index > 0 and i > 0:
                value = value.replace("–", "–\n")
            set_cell_text(cells[i], value, row_index == 0)
        if row_index == 0:
            trpr = table.rows[-1]._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:tblHeader"))
    para(doc, "", 1, after=1)


doc = Document()
for section in doc.sections:
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.54)
    section.left_margin = section.right_margin = Cm(2.54)
    section.header_distance = section.footer_distance = Cm(1.0)
normal = doc.styles["Normal"]
normal.paragraph_format.space_after = Pt(3)
normal.paragraph_format.line_spacing = 1.0
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)

para(doc, LINES[0][2:], 16, True, align=WD_ALIGN_PARAGRAPH.CENTER,
     after=8, keep_next=True)
para(doc, "林昀佑¹、易昶霈¹、沈慧宇²", 12, True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=4, keep_next=True)
para(doc, "¹ 國立彰化師範大學資訊工程學系；² 建國科技大學電機工程系",
     10, align=WD_ALIGN_PARAGRAPH.CENTER, after=7, keep_next=True)

abstract_start = LINES.index("## 摘要")
abstract = LINES[abstract_start + 2]
keywords = LINES[abstract_start + 4]
para(doc, "摘要", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER, after=3,
     keep_next=True)
para(doc, abstract, 12, italic=True, first_indent=24, after=5)
para(doc, "關鍵詞", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER,
     after=2, keep_next=True)
para(doc, keywords.split("：", 1)[1], 12, after=7)

section = doc.add_section(WD_SECTION_START.CONTINUOUS)
section.page_width, section.page_height = Cm(21), Cm(29.7)
section.top_margin = section.bottom_margin = Cm(2.54)
section.left_margin = section.right_margin = Cm(2.54)
cols = section._sectPr.xpath("./w:cols")[0]
cols.set(qn("w:num"), "2")
cols.set(qn("w:space"), "476")

body = LINES.index("## 一、前言")
i = body
while i < len(LINES):
    line = LINES[i].strip()
    if not line:
        i += 1
        continue
    if line == "$$":
        i += 1
        while i < len(LINES) and LINES[i].strip() != "$$":
            i += 1
        assert i < len(LINES), "Unclosed display equation"
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(4)
        p.add_run().add_picture(str(HERE / "figures/model_equation.png"), width=Cm(7.4))
        i += 1
        continue
    if line.startswith("## "):
        heading(doc, line[3:])
        i += 1
        continue
    if line.startswith("**表"):
        caption(doc, line.strip("*"))
        i += 1
        continue
    if line.startswith("| "):
        rows = []
        while i < len(LINES) and LINES[i].startswith("| "):
            vals = [v.strip() for v in LINES[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"[-: ]+", v) for v in vals):
                rows.append(vals)
            i += 1
        add_table(doc, rows)
        continue
    if line.startswith("!["):
        m = re.match(r"!\[(.*)\]\((.*)\)", line)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.add_run().add_picture(str(HERE / m.group(2)), width=Cm(7.45))
        caption(doc, m.group(1), before=0, after=4)
        i += 1
        continue
    if line.startswith("[") and re.match(r"\[\d+\]", line):
        para(doc, line, 10, after=3)
        i += 1
        continue
    if line.startswith("C_i dT_i/dt"):
        para(doc, line, 10, align=WD_ALIGN_PARAGRAPH.CENTER, after=3)
        i += 1
        continue
    para(doc, line, 12, first_indent=24)
    i += 1

doc.core_properties.title = LINES[0][2:]
doc.core_properties.subject = "2027 工程科技應用研討會審閱稿；共同假設模型之模擬比較"
doc.save(OUT)
print(OUT)
