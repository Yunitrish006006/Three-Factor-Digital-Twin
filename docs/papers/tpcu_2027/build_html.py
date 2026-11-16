#!/usr/bin/env python3
"""Build a printable, locally self-contained review copy of the TPCU paper."""
from pathlib import Path
from html import escape
import re

def inline_html(text):
    return re.sub(r'&lt;(/?(?:sub|sup))&gt;', r'<\1>', escape(text))

HERE = Path(__file__).resolve().parent
lines = (HERE / "manuscript_zh.md").read_text().splitlines()
title = lines[0][2:]
abstract_at = lines.index("## 摘要")
abstract = lines[abstract_at + 2]
keywords = lines[abstract_at + 4].split("：", 1)[1]
body_at = lines.index("## 一、前言")

parts = []
i = body_at
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    if line == "$$":
        i += 1
        equation = []
        while i < len(lines) and lines[i].strip() != "$$":
            equation.append(lines[i])
            i += 1
        assert i < len(lines), "Unclosed display equation"
        number = int(re.search(r"\\tag\{(\d+)\}", "\n".join(equation)).group(1))
        name = "model_equation" if number == 1 else f"control_equation_{number}"
        parts.append(f"<div class='display-equation'><img src='figures/{name}.svg' alt='公式（{number}）'></div>")
        i += 1
        continue
    if line.startswith("### "):
        parts.append(f"<h3>{escape(line[4:])}</h3>")
        i += 1
        continue
    if line.startswith("## "):
        parts.append(f"<h2>{escape(line[3:])}</h2>")
        i += 1
        continue
    if line.startswith("**表"):
        parts.append(f"<div class='table-caption'>{escape(line.strip('*'))}</div>")
        i += 1
        continue
    if line.startswith("**") and line.endswith("**"):
        parts.append(f"<h3>{escape(line[2:-2])}</h3>")
        i += 1
        continue
    if line.startswith("| "):
        rows = []
        while i < len(lines) and lines[i].startswith("| "):
            vals = [v.strip() for v in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"[-: ]+", v) for v in vals):
                rows.append(vals)
            i += 1
        n = len(rows[0])
        css = f"t{n}"
        table = [f"<table class='{css}'><thead><tr>"]
        table += [f"<th>{inline_html(v)}</th>" for v in rows[0]]
        table.append("</tr></thead><tbody>")
        for row in rows[1:]:
            values = [inline_html(v).replace("–", "–<br>") if n == 4 and index > 0 else inline_html(v)
                      for index, v in enumerate(row)]
            table.append("<tr>" + "".join(f"<td>{v}</td>" for v in values) + "</tr>")
        table.append("</tbody></table>")
        parts.extend(table)
        continue
    if line.startswith("!["):
        m = re.match(r"!\[(.*)\]\((.*)\)", line)
        parts.append(f"<figure><img src='{escape(m.group(2))}'><figcaption>{escape(m.group(1))}</figcaption></figure>")
        i += 1
        continue
    klass = "ref" if re.match(r"\[\d+\]", line) else "equation" if line.startswith("C_i dT_i/dt") else ""
    parts.append(f"<p class='{klass}'>{inline_html(line)}</p>")
    i += 1

style = """
@page { size: A4; margin: 2.54cm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { color:#111; font-family:'Times New Roman','BiauKaiTC',serif; font-size:12pt; line-height:1.10; }
.top { text-align:center; }
h1 {font-size:16pt;line-height:1.2;margin:0 0 8pt;font-weight:bold;}
.authors {font-size:12pt;font-weight:bold;margin:0 0 3pt;}
.affiliations {font-size:10pt;margin:0 0 7pt;}
.abstract-head,.keywords-head {font-size:14pt;font-weight:bold;margin:0 0 3pt;}
.abstract {font-size:12pt;font-style:italic;text-align:justify;text-indent:2em;margin:0 0 5pt;}
.keywords {font-size:12pt;margin:0 0 8pt;}
.article { column-count:2; column-gap:.84cm; column-fill:balance; }
h2 {font-size:14pt;line-height:1.15;margin:6pt 0 3pt;font-weight:bold;break-after:avoid;}
h3 {font-size:12pt;line-height:1.15;margin:6pt 0 3pt;font-weight:bold;break-after:avoid;}
p {margin:0 0 2pt;text-indent:2em;text-align:justify;orphans:2;widows:2;}
p:has(+ .display-equation) {break-inside:avoid;break-after:avoid;}
p.ref {font-family:'Times New Roman',serif;font-size:10pt;text-indent:0;text-align:justify;overflow-wrap:anywhere;}
.display-equation {break-inside:avoid;margin:4pt 0 5pt;text-align:center;}
.display-equation img {display:block;width:100%;height:auto;}
figure {margin:4pt 0;break-inside:avoid;}
figure img {width:100%;height:auto;display:block;}
figcaption,.table-caption {font-size:10pt;font-weight:bold;text-align:center;line-height:1.15;}
.table-caption {margin:5pt 0 2pt;break-after:avoid;}
table {border-collapse:collapse;width:100%;font-size:10pt;line-height:1.05;table-layout:fixed;break-inside:auto;margin:0 0 4pt;}
tr {break-inside:avoid;}
th,td {border:0.4pt solid #333;padding:1.4pt 1.5pt;vertical-align:top;overflow-wrap:normal;word-break:normal;}
th {font-weight:normal;}
.t4 th:nth-child(1),.t4 td:nth-child(1){width:14%;}
.t4 {break-inside:avoid;}
.t4 th:nth-child(2),.t4 td:nth-child(2){width:28%;}
.t4 th:nth-child(3),.t4 td:nth-child(3){width:29%;}
.t4 th:nth-child(4),.t4 td:nth-child(4){width:29%;}
.t3 th:nth-child(1),.t3 td:nth-child(1){width:18%;}
.t3 th:nth-child(2),.t3 td:nth-child(2){width:18%;}
.t3 th:nth-child(3),.t3 td:nth-child(3){width:64%;}
.t2 th:nth-child(1),.t2 td:nth-child(1){width:18%;}
.t2 {break-inside:avoid;}
.t2 th:nth-child(2),.t2 td:nth-child(2){width:82%;}
.t5 th:nth-child(1),.t5 td:nth-child(1){width:15%;}
.t5 th:nth-child(2),.t5 td:nth-child(2){width:15%;}
.t5 th:nth-child(3),.t5 td:nth-child(3){width:17%;}
.t5 th:nth-child(4),.t5 td:nth-child(4){width:31%;}
.t5 th:nth-child(5),.t5 td:nth-child(5){width:22%;}
@media screen {body{width:21cm;min-height:29.7cm;margin:auto;padding:2.54cm;box-shadow:0 0 15px #ccc;} }
"""
html = f"""<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'><title>{escape(title)}</title><style>{style}</style></head><body>
<header class='top'><h1>{escape(title)}</h1><div class='authors'>林昀佑¹、易昶霈¹、沈慧宇²</div><div class='affiliations'>¹ 國立彰化師範大學資訊工程學系；² 建國科技大學電機工程系</div><div class='abstract-head'>摘要</div></header>
<div class='abstract'>{escape(abstract)}</div><div class='top keywords-head'>關鍵詞</div><div class='keywords'>{escape(keywords)}</div>
<article class='article'>{''.join(parts)}</article></body></html>"""
(HERE / "manuscript_zh.html").write_text(html)
print(HERE / "manuscript_zh.html")
