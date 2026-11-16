#!/usr/bin/env python3
"""Render numbered manuscript equations from their Markdown LaTeX source."""
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for fontfile in Path("/System/Library/Fonts/Supplemental").glob("Times New Roman*.ttf"):
    font_manager.fontManager.addfont(str(fontfile))

HERE = Path(__file__).resolve().parent
source = (HERE / "manuscript_zh.md").read_text()
blocks = re.findall(r"\$\$\s*\n(.*?)\n\$\$", source, re.S)
plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "custom", "mathtext.rm":"Times New Roman", "mathtext.it":"Times New Roman:italic", "mathtext.bf":"Times New Roman:bold"})

for block in blocks:
    number = int(re.search(r"\\tag\{(\d+)\}", block).group(1))
    body = re.sub(r"\\tag\{\d+\}", "", block)
    body = body.replace(r"\begin{aligned}", "").replace(r"\end{aligned}", "")
    body = body.replace(r"\mathrm d", r"\mathrm{d}").replace(r"\mathsf T", r"\mathsf{T}")
    rows = [row.strip().replace("&", "") for row in body.split(r"\\") if row.strip()]
    width, dpi, size = 7.54 / 2.54, 400, 10.0
    fig = plt.figure(figsize=(width, 2), dpi=dpi)
    texts = [fig.text(0, 0, f"${row}$", fontsize=size) for row in rows]
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = [t.get_window_extent(renderer) for t in texts]
    max_width = max(b.width for b in bounds)
    available = width * dpi * .88
    if max_width > available:
        size *= available / max_width
        if size < 10.0:
            raise ValueError(f"Equation {number} requires line breaks, would use {size:.2f} pt")
        for t in texts:
            t.set_fontsize(size)
        fig.canvas.draw()
        bounds = [t.get_window_extent(renderer) for t in texts]
    heights = [b.height / dpi for b in bounds]
    gap, pad = .065, .055
    height = sum(heights) + gap * (len(rows) - 1) + 2 * pad
    fig.set_size_inches(width, height)
    top = height - pad
    for t, h in zip(texts, heights):
        t.set_position((0, top / height))
        t.set_verticalalignment("top")
        top -= h + gap
    fig.text(1, .5, f"({number})", fontsize=10, ha="right", va="center")
    name = "model_equation" if number == 1 else f"control_equation_{number}"
    for suffix in ("png", "svg"):
        output = HERE / "figures" / f"{name}.{suffix}"
        fig.savefig(output, dpi=dpi, facecolor="white")
        if suffix == "svg":
            output.write_text("\n".join(line.rstrip() for line in output.read_text().splitlines()) + "\n")
    plt.close(fig)
    print(f"Equation {number}: {len(rows)} lines, {size:.2f} pt")
