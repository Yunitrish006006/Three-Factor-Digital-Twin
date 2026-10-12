"""Render the guide's small Markdown subset with native offline MathML.

Markdown is the prose source of truth. Unknown named math fences fail the build.
"""
from html import escape
import os
from pathlib import Path
import re
from professor_report_math import TEACHING_EQUATIONS

ROOT=Path(__file__).resolve().parents[1]
GUIDE=ROOT/'docs/research/lqr_practical_guide_2026-10-12_zh.md'


def inline(text):
    text=escape(text)
    def link(match):
        label,target=match.groups()
        if not target.startswith(('https://','http://','#')):
            path,separator,fragment=target.partition('#')
            target=os.path.relpath((GUIDE.parent/path).resolve(),ROOT/'docs/reports')
            if separator: target+='#'+fragment
        return '<a href="'+target+'">'+label+'</a>'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    return re.sub(r'`([^`]+)`',r'<code>\1</code>',text)


def render_guide():
    lines=GUIDE.read_text().splitlines(); parts=[]; index=0; expanded=False
    while index<len(lines):
        line=lines[index]
        if not line.strip(): index+=1; continue
        if line.startswith('# '): index+=1; continue
        if line.startswith('## '):
            if expanded: parts.append('</details>')
            parts.append('<details class="lqr-study"><summary>'+inline(line[3:])+'</summary>')
            expanded=True;index+=1;continue
        if line.startswith('### '):
            parts.append('<h4>'+inline(line[4:])+'</h4>');index+=1;continue
        if line.startswith('```'):
            language=line[3:]; block=[];index+=1
            while index<len(lines) and not lines[index].startswith('```'):
                block.append(lines[index]);index+=1
            if index==len(lines): raise ValueError('Unclosed guide code fence')
            index+=1
            if language.startswith('math:'):
                parts.append(TEACHING_EQUATIONS[language[5:]]())
            else: parts.append('<pre>'+escape('\n'.join(block))+'</pre>')
            continue
        if line.startswith('|'):
            table=[]
            while index<len(lines) and lines[index].startswith('|'):
                table.append([inline(cell.strip()) for cell in lines[index].strip('|').split('|')]);index+=1
            parts.append('<div class="table-wrap" tabindex="0" role="region" aria-label="LQR 對照表，可左右捲動"><table><thead><tr>'+''.join('<th>'+cell+'</th>' for cell in table[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+cell+'</td>' for cell in row)+'</tr>' for row in table[2:])+'</tbody></table></div>')
            continue
        if line.startswith('- '):
            items=[]
            while index<len(lines) and lines[index].startswith('- '):
                items.append('<li>'+inline(lines[index][2:])+'</li>');index+=1
            parts.append('<ul>'+''.join(items)+'</ul>');continue
        paragraph=[line];index+=1
        while index<len(lines) and lines[index].strip() and not lines[index].startswith(('#','```','|','- ')):
            paragraph.append(lines[index]);index+=1
        parts.append('<p>'+inline(' '.join(paragraph))+'</p>')
    if expanded: parts.append('</details>')
    return '<div class="lqr-detailed-guide">'+''.join(parts)+'</div>'
