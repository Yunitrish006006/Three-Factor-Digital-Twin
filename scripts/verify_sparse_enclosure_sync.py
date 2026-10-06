"""Verify candidate supplement content/copies; record visual QA separately."""
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from artifact_visual_qa import visual_qa_status
from sparse_enclosure_corrections import ARTIFACTS as CORRECTION_ARTIFACTS

from sparse_enclosure_summary import ROOT, TITLE, summary, SUMMARY_KEYS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def office_text(path, member):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read(member))
    return ''.join(node.text or '' for node in root.iter() if node.tag.endswith('}t'))


def verify_sync(root=ROOT, observation_file=None):
    root = Path(root)
    observation_file = observation_file or CORRECTION_ARTIFACTS / 'visual_qa_observations.json'
    s = summary()
    checks = []
    hashes = {}
    def require(condition, label):
        if not condition:
            raise ValueError(label)
        checks.append(label)
    for filename in ('thesis_draft_zh.docx', 'thesis_draft_zh.pdf',
                     'thesis_presentation_zh.pptx', 'thesis_presentation_zh_30min.pptx'):
        published = root / 'docs/papers/thesis' / filename
        generated = root / 'outputs/papers' / filename
        require(digest(published) == digest(generated), f'byte-equal copies: {filename}')
        hashes[str(published.relative_to(root))] = digest(published)
    for relative in ('docs/thesis/thesis_draft_zh.md',
                     'docs/thesis/presentation_outline_zh.md',
                     'docs/thesis/presentation_outline_zh_30min.md',
                     'docs/thesis/presentation_speaker_notes_zh_30min.md'):
        content = (root / relative).read_text()
        require(all(s[key] in content for key in SUMMARY_KEYS),
                f'evidence-derived supplement: {relative}')
        hashes[relative] = digest(root / relative)
    docx = root / 'docs/papers/thesis/thesis_draft_zh.docx'
    content = office_text(docx, 'word/document.xml')
    require(all(s[key] in content for key in SUMMARY_KEYS), 'DOCX supplement text')
    from pptx import Presentation
    slide_counts = {}
    for suffix in ('', '_30min'):
        relative = f'docs/papers/thesis/thesis_presentation_zh{suffix}.pptx'
        deck = Presentation(root / relative)
        matches = [slide for slide in deck.slides if any(TITLE in shape.text for shape in slide.shapes if shape.has_text_frame)]
        require(len(matches) == 1, f'exactly one supplement slide: {relative}')
        slide = matches[0]
        notes = slide.notes_slide.notes_text_frame.text
        require(all(s[key] in notes for key in SUMMARY_KEYS), f'slide notes preserve evidence/limits: {relative}')
        require(all(shape.left >= 0 and shape.top >= 0 and shape.left + shape.width <= deck.slide_width
                    and shape.top + shape.height <= deck.slide_height for shape in slide.shapes),
                f'supplement shape bounds: {relative}')
        slide_counts[relative] = len(deck.slides)
    tex = (root / 'docs/papers/ieee/paper.tex').read_text()
    require(all(value in tex for value in ('0.9610/0.6580/0.3352', '108 episodes (19,440 steps)',
                                           'does not outperform PI', 'remain unevaluated', '150/360', '124 actual')), 'IEEE text numbers and limits')
    pdf_pages = {}
    for relative, needles in (
        ('docs/papers/thesis/thesis_draft_zh.pdf', ('0.3352', '49.06', 'Kalman', '32.40', '124')),
        ('docs/papers/ieee/paper.pdf', ('0.9610/0.6580/0.3352', '19,440', 'does not outperform PI', '150/360', '124 actual')),
    ):
        path = root / relative
        text = subprocess.check_output(['pdftotext', str(path), '-'], text=True)
        compact = ''.join(text.split())
        require(all(''.join(value.split()) in compact for value in needles), f'PDF text numbers/limits: {relative}')
        pdf_pages[relative] = text.count('\f')
        hashes[relative] = digest(path)
    for relative in ('docs/papers/ieee/paper.tex', 'docs/papers/ieee/references.bib',
                     'docs/reports/professor_research_2026-10-06_zh.html',
                     'docs/research/lqr_kalman1960_reading_2026-10-06_zh.md',
                     'docs/reports/lqr_oral_script_2026-10-06_zh.md'):
        hashes[relative] = digest(root / relative)
    html = 'docs/reports/professor_research_2026-10-06_zh.html'
    observed = {html: visual_qa_status(root, observation_file, html,
                        ('desktop', 'tablet', 'mobile', 'anchors', 'interaction', 'console', 'local_links', 'offline_assets'))}
    for relative in pdf_pages:
        observed[relative] = visual_qa_status(root, observation_file, relative, ('inspected_pages',))
    return {'status': 'PASS', 'checks': checks, 'sha256': hashes,
            'slide_counts': slide_counts, 'pdf_pages': pdf_pages, 'observed_qa': observed,
            'html_delivery_status': 'PASS' if observed[html]['status'] == 'PASS' else 'NOT_ACCEPTED',
            'office_full_render': 'NOT_EVALUATED', 'html_print': 'NOT_EVALUATED',
            'scope': 'Automatic content checks are separate from hash-bound observed QA. PDF QA accepts recorded pages only; no complete Office visual acceptance or hardware evidence.'}


def main():
    report = verify_sync()
    output = CORRECTION_ARTIFACTS / 'artifact_sync_verification.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"Content {report['status']}: {len(report['checks'])} checks; HTML delivery {report['html_delivery_status']}; Office QA NOT_EVALUATED.")
    if report['html_delivery_status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
