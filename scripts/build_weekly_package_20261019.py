"""Build a bounded review manuscript and weekly briefing from frozen results."""
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
from statistics import mean

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'docs/papers/conference_review_2026-10-19'
OUT=ROOT/'openspec/changes/diagnose-enclosure-lqr-20261019/artifacts/reporting'
REPORT=ROOT/'docs/reports/professor_weekly_2026-10-19_zh.html'
LABELS={'fixed':'固定風扇','pi':'PI','pid':'PID','lqr':'LQR','linear_mpc':'線性 MPC','rank_h1':'單步排序','rank_h6':'六步排序','rank_h6_no_correction':'六步無校正'}


def load(study):
    return json.loads((ROOT/'openspec/changes'/study/'artifacts/result.json').read_text())


def tables():
    first=load('integrate-enclosure-session-20261012');second=load('select-enclosure-structure-20261012')
    c=first['aggregates']['closed_loop']['holdout'];o=first['aggregates']['open_loop']['holdout'];s=second['aggregates']['closed_loop']['holdout']
    data={
      'control_table':('表 1　第一階段留出控制結果（四回合平均）',['配置','追蹤 °C','proxy Wh','超溫 s'],[[LABELS[m]]+[f'{c[m][k]:.4f}' for k in ('tracking_mae_C','fan_energy_proxy_Wh','overtemp_s')] for m in LABELS]),
      'cost_table':('表 2　估測、動作及計算成本',['配置','估測 °C','PWM 變化','ms/步'],[[LABELS[m]]+[f'{c[m][k]:.4f}' for k in ('source_mae_C','command_variation','compute_mean_ms')] for m in LABELS]),
      'rig_table':('表 3　逐平台追蹤 MAE（各兩回合）',['配置','接觸/容量 °C','額外路徑 °C'],[[LABELS[m]]+[f'{mean(x["metrics"]["tracking_mae_C"] for x in first["runs"] if x["task"]=="closed_loop" and x["split"]=="holdout" and x["rig"]==rig and x["method"]==m):.4f}' for rig in ('contact_capacity','extra_path')] for m in LABELS]),
      'observer_table':('表 4　同軌跡開迴路估測比較',['配置','熱源 MAE °C'],[[name,f'{o[m]["source_mae_C"]:.4f}'] for m,name in [('nominal_physics','名義物理'),('calibrated_physics','辨識後物理'),('sparse_corrected','稀疏校正')]]),
      'structure_table':('表 5　第二階段控制結果（六回合平均）',['配置','追蹤 °C','proxy Wh','超溫 s'],[[name]+[f'{s[m][k]:.4f}' for k in ('tracking_mae_C','fan_energy_proxy_Wh','overtemp_s')] for m,name in [('S_pi','S＋PI'),('selected_pi','選擇＋PI'),('S_rank_h6','S＋六步'),('selected_rank_h6','選擇＋六步')]]),
      'failure_table':('表 6　逐平台校正後熱源 MAE',['平台','S °C','選擇模型 °C'],[[name]+[f'{mean(x["metrics"]["source_mae_C"] for x in second["runs"] if x["task"]=="open_loop" and x["split"]=="holdout" and x["rig"]==rig and x["method"]==m):.4f}' for m in ('S_corrected','selected_corrected')] for rig,name in [('contact_variant','接觸/容量'),('path_capacity','路徑/容量'),('convection_mismatch','對流失配')]])}
    from enclosure_lqr_diagnostic_summary import comparison_table
    data['diagnostic_table']=comparison_table()
    return data


def html_table(item):
    caption,headers,rows=item
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="資料表，可左右捲動"><table><caption>'+escape(caption)+'</caption><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'


CSS='''figure{margin:24px 0}.figure-wrap{overflow-x:auto}.figure-wrap img{min-width:640px}#diagnostic details table{min-width:850px}*{box-sizing:border-box}body{margin:0;color:#203647;background:#eef3f6;font:17px/1.85 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:24px}header,section{background:white;padding:28px;margin:0 0 22px;border-radius:12px;border:1px solid #d7e1e8}h1{font-size:30px;line-height:1.5}h2{font-size:24px;margin-top:26px}h3{font-size:19px}p,li{overflow-wrap:anywhere}a{color:#176a91}nav{display:flex;gap:12px;flex-wrap:wrap}.meta,.caption{font-size:14px;color:#526979}.status{padding:14px 18px;background:#edf5f7;border-left:4px solid #2c7382}table{width:100%;border-collapse:collapse;font-size:15px}th,td{padding:10px;border-bottom:1px solid #d7e1e8;text-align:left}th{background:#edf3f8}caption{text-align:left;font-weight:600;margin-bottom:10px}.table-wrap{overflow-x:auto;margin:20px 0}.table-wrap table{min-width:520px}details{border-top:1px solid #d7e1e8;padding:15px 0}summary{cursor:pointer;font-weight:600}.math{overflow-x:auto;background:#f6f8fa;padding:15px}.math math{display:block;margin:14px 0;width:max-content}:focus-visible{outline:3px solid #bf8b35}@media(max-width:650px){main{padding:12px}header,section{padding:18px}h1{font-size:25px}}@media print{.figure-wrap img{min-width:0}#diagnostic details table{min-width:0}body{background:white;font-size:10pt}main{padding:0}header,section{border:0;padding:0}nav{display:none}.table-wrap table{min-width:0}table{font-size:9pt}tr{break-inside:avoid}}'''


def html_page(title,content):
    return '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+CSS+'</style></head><body><main>'+content+'</main></body></html>\n'


def plain_html(text):
    value=escape(text)
    value=re.sub(r'https?://[^\s）]+',lambda m:'<a href="'+m[0]+'">'+m[0]+'</a>',value)
    for x in ('h','p','a'):value=value.replace('T_'+x,'T<sub>'+x+'</sub>')
    return value


def pdf_text(text):
    # Keep long URLs clickable with compact labels so they do not overflow a column.
    chunks=re.split(r'(https?://[^\s）]+)',text);out=[]
    for chunk in chunks:
        if chunk.startswith(('https://','http://')):
            out.append('<link href="'+escape(chunk,quote=True)+'" color="#174d71">線上來源</link>');continue
        chunk=escape(chunk)
        chunk=re.sub(r'([\x20-\x7e\u00a0-\u024f\u0300-\u03ff]+)',lambda m:'<font name="TimesNewRoman">'+m[0]+'</font>',chunk)
        for x in ('h','p','a'):chunk=chunk.replace('T_'+x,'T<sub>'+x+'</sub>')
        out.append(chunk)
    return ''.join(out)


EQUATIONS=[
    'x<sub>k+1</sub> = F(x<sub>k</sub>, u<sub>k</sub>, d<sub>k</sub>)',
    'u<sub>k</sub> = u* - K(x̂<sub>k</sub> - x*)',
    'J = Σ<sub>j=0</sub><super>H-1</super> ℓ(x<sub>k+j</sub>, u<sub>k+j</sub>, Δu<sub>k+j</sub>)']


class BoldParagraph(Paragraph):
    """Synthesize a light bold stroke for the installed regular BiauKai face."""
    def draw(self):
        self.canv.saveState()
        self.canv.setLineWidth(.18)
        mode=self.canv.beginText();mode.setTextRenderMode(2);self.canv.drawText(mode)
        super().draw()
        self.canv.restoreState()


def make_pdf(source,data):
    kai=os.environ.get('REVIEW_KAI_FONT','/System/Library/AssetsV2/PreinstalledAssetsV2/InstallWithOs/com_apple_MobileAsset_Font7/66746e61b4dbfa104b24e08fd5cdadcea3816e57.asset/AssetData/BiauKai.ttf')
    times=os.environ.get('REVIEW_TIMES_FONT','/System/Library/Fonts/Supplemental/Times New Roman.ttf')
    pdfmetrics.registerFont(TTFont('BiauKai',kai));pdfmetrics.registerFont(TTFont('TimesNewRoman',times))
    normal=ParagraphStyle('body',fontName='BiauKai',fontSize=10,leading=13.5,firstLineIndent=20,spaceAfter=5,wordWrap='CJK',alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0)
    head=ParagraphStyle('head',parent=normal,fontSize=11,leading=15,firstLineIndent=0,spaceBefore=9,spaceAfter=6,keepWithNext=True)
    small=ParagraphStyle('table',parent=normal,fontSize=10,leading=12,firstLineIndent=0,spaceAfter=0,alignment=0)
    caption=ParagraphStyle('caption',parent=normal,firstLineIndent=0,alignment=TA_CENTER,spaceBefore=8,spaceAfter=4,keepWithNext=True)
    equation=ParagraphStyle('eq',parent=normal,fontName='TimesNewRoman',alignment=TA_CENTER,firstLineIndent=0,spaceAfter=5)
    width,height=A4;left=2*cm;bottom=3*cm;gap=.65*cm;column=(width-4*cm-gap)/2
    frames=[Frame(left,bottom,column,height-6*cm,id='left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),Frame(left+column+gap,bottom,column,height-6*cm,id='right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]
    title_height=103
    first=[Frame(left,bottom,column,height-6*cm-title_height,id='first-left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),Frame(left+column+gap,bottom,column,height-6*cm-title_height,id='first-right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]
    def header(c,doc):
        c.setFont('TimesNewRoman',9);c.drawString(left,height-2.05*cm,'CSME 2026')
        c.setFont('BiauKai',9);c.drawString(left+48,height-2.05*cm,'候選格式審閱稿');c.drawRightString(width-left,height-2.05*cm,'會議未定／尚未投稿')
        if doc.page==1:
            def centered(text,y,size=12,bold=False):
                style=ParagraphStyle('title-line',fontName='BiauKai',fontSize=size,leading=size*1.3,alignment=TA_CENTER)
                p=(BoldParagraph if bold else Paragraph)(text,style)
                _,h=p.wrap(width-4*cm,100);p.drawOn(c,left,y-h)
            centered('稀疏感測機箱熱控制之方法比較與模型失配分析',height-3.03*cm,14,True)
            sup=lambda n:'<super><font name="TimesNewRoman">'+str(n)+'</font></super>'
            centered('林昀佑'+sup(1)+'、易昶霈'+sup(1)+'、沈慧宇'+sup(2),height-3.75*cm)
            centered(sup(1)+'國立彰化師範大學資訊工程學系',height-4.35*cm)
            centered(sup(2)+'建國科技大學電機工程系',height-4.95*cm)
            c.setFont('TimesNewRoman',10);c.drawCentredString(width/2,height-5.9*cm,'Contact: yunitrish0419@gmail.com')
    target=PAPER/'manuscript_zh.pdf'
    doc=BaseDocTemplate(str(target),pagesize=A4,title='稀疏感測機箱熱控制之方法比較與模型失配分析',author='Yun-You Lin; Chang-Pei Yi; Hui-Yu Shen',leftMargin=left,rightMargin=left,topMargin=3*cm,bottomMargin=bottom)
    doc.addPageTemplates([PageTemplate(id='First',frames=first,onPage=header,autoNextPageTemplate='Later'),PageTemplate(id='Later',frames=frames,onPage=header)])
    story=[]
    for block in source.split('\n\n'):
        block=block.strip()
        if not block or block.startswith('# '):continue
        if block.startswith('{{'):
            key=block[2:-2]
            if key=='equations':
                for number,eq in enumerate(EQUATIONS,1):
                    tab=Table([[Paragraph(eq,equation),Paragraph(f'({number})',equation)]],colWidths=[column-20,20])
                    tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
                    story.append(tab)
                story.append(Paragraph(pdf_text('式 (2) 為 LQR 工作點回授，式 (3) 為有限視野成本記號；實際輸出另經限制，單步成本的各項於第 3 節說明。'),normal));continue
            title,headers,rows=data[key]
            cells=[[Paragraph(pdf_text(v),small) for v in row] for row in [headers]+rows]
            w=[column/len(headers)]*len(headers)
            if len(headers)==4:w=[column*.31]+[column*.23]*3
            tab=Table(cells,colWidths=w,repeatRows=1,hAlign='LEFT')
            tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,-1),(-1,-1),.4,colors.black),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2)]))
            preceding=[]
            while story and isinstance(story[-1],BoldParagraph):
                preceding.insert(0,story.pop())
            story.append(KeepTogether(preceding+[Paragraph(pdf_text(title),caption),tab,Spacer(1,5)]));continue
        is_head=block.startswith('##')
        story.append((BoldParagraph if is_head else Paragraph)(pdf_text(re.sub(r'^#+ ','',block)),head if is_head else normal))
    doc.build(story)
    reader=PdfReader(target)
    info={'pages':len(reader.pages),'bytes':target.stat().st_size,'page_size_points':list(reader.pages[0].mediabox),'chinese_font':kai,'latin_font':times,'format':'A4; body margins top/bottom 3cm left/right 2cm; two columns; 10pt body, 11pt headings, 14pt title, 12pt authors; no page numbers','submission_status':'NOT_SUBMITTED; venue undecided; review copy uses existing author metadata'}
    (OUT/'pdf_format.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(info,ensure_ascii=False))


def build():
    OUT.mkdir(parents=True,exist_ok=True);data=tables();source=(PAPER/'manuscript_zh.md').read_text()
    parts=[]
    for block in source.split('\n\n'):
        block=block.strip()
        if not block:continue
        if block.startswith('{{'):
            key=block[2:-2]
            if key=='equations':
                parts.append('<div class="math" tabindex="0"><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msub><mi>x</mi><mrow><mi>k</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>=</mo><mi>F</mi><mo>(</mo><msub><mi>x</mi><mi>k</mi></msub><mo>,</mo><msub><mi>u</mi><mi>k</mi></msub><mo>,</mo><msub><mi>d</mi><mi>k</mi></msub><mo>)</mo><mspace width="1em"/><mtext>(1)</mtext></mrow></math><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msub><mi>u</mi><mi>k</mi></msub><mo>=</mo><msup><mi>u</mi><mo>*</mo></msup><mo>−</mo><mi>K</mi><mo>(</mo><msub><mover><mi>x</mi><mo>^</mo></mover><mi>k</mi></msub><mo>−</mo><msup><mi>x</mi><mo>*</mo></msup><mo>)</mo><mspace width="1em"/><mtext>(2)</mtext></mrow></math><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>J</mi><mo>=</mo><munderover><mo>∑</mo><mrow><mi>j</mi><mo>=</mo><mn>0</mn></mrow><mrow><mi>H</mi><mo>−</mo><mn>1</mn></mrow></munderover><mi>ℓ</mi><mo>(</mo><msub><mi>x</mi><mrow><mi>k</mi><mo>+</mo><mi>j</mi></mrow></msub><mo>,</mo><msub><mi>u</mi><mrow><mi>k</mi><mo>+</mo><mi>j</mi></mrow></msub><mo>,</mo><mi>Δ</mi><msub><mi>u</mi><mrow><mi>k</mi><mo>+</mo><mi>j</mi></mrow></msub><mo>)</mo><mspace width="1em"/><mtext>(3)</mtext></mrow></math></div><p>式 (2) 為 LQR 工作點回授，式 (3) 為有限視野成本；實際輸出另經限制。</p>')
            else:parts.append(html_table(data[key]))
        elif block.startswith('#'):
            level=len(block)-len(block.lstrip('#'));parts.append(f'<h{level}>'+plain_html(block[level+1:])+f'</h{level}>')
        else:parts.append('<p>'+plain_html(block)+'</p>')
    intro='<header><p class="meta">2026-10-19｜完整審閱草稿，會議未選定、尚未投稿</p><p>作者資料沿用現有稿件：林昀佑、易昶霈、沈慧宇；作者順序及通訊作者待共同確認。</p><nav><a href="../../reports/professor_weekly_2026-10-19_zh.html">本週報告</a><a href="manuscript_zh.pdf">PDF 審閱稿</a><a href="manuscript_zh.md">文字來源</a><a href="readiness_zh.md">投稿準備狀態</a></nav></header>'
    (PAPER/'manuscript_zh.html').write_text(html_page('機箱熱控制比較：論文審閱稿',intro+'<section>'+''.join(parts)+'</section>'))
    make_pdf(source,data)
    talk='''# 本週教授報告講稿

整理日期：2026-10-19。約十分鐘；口頭報告狀態未確認。實驗證據產生於 10/12，本週完成數據覆核與稿件整合。

## 0–2 分鐘：我如何回應交辦

我把各方法比較、原因說明與實驗結論整理成同一份完整稿件。這週重新核對了兩階段 184 回合、22,080 筆既有紀錄，數字與原結果一致。這是證據整理與核對，沒有把舊實驗改稱新實驗，也沒有重跑挑選較好的結果。

## 2–5 分鐘：每個方法得到什麼結論

第一階段，PI 的平均追蹤誤差最低，PID 幾乎相同。LQR 的這組權重與限制下沒有優於 PI；MPC 的風扇耗能估計較低，但追蹤稍差。六步排序相對單步只改善 0.069%，沒有達到事前門檻。關閉校正後雖然耗能估計更低，超溫卻更多，所以不能單看省能數字。

我把原因分成實作事實與待驗證的解釋。能確認的是控制器資訊、權重、視野與限制；尚不能確認的是哪一因素導致差異。例如 LQR 的尺度、飽和與模型失配都可能有影響，不能只看排名就斷言主因。

## 5–7 分鐘：模型結構的反例

第二階段使用新資料比較模型結構。可見感測擬合較好，隱藏熱源卻可能更差；平均誤差增加 25.12%。新增路徑平台有改善，對流失配平台退步，並出現容量碰界。我因此保留各平台差異，不把更複雜模型寫成已證明較佳的方法。

## 7–9 分鐘：稿件與 LQR 準備

LQR 的原始論文、推導、機箱狀態與方法限制已備妥。我將本次比較整理成中文完整論文審閱稿，先依候選會議篇幅排版。貢獻聚焦可重現比較與失配限制，而不是宣稱發明 LQR 或全面優於傳統方法。

## 9–10 分鐘：我要確認的下一步

我想請老師先確認稿件主軸是否聚焦控制取捨，或以可見擬合與隱藏熱源的落差作為核心。若要驗證原因，我會先訂新實驗與共同選參預算，再使用新資料。現階段沒有實機資料，硬體節能與安全仍不能宣稱已完成。
'''
    from enclosure_lqr_diagnostic_summary import paragraphs as diagnostic_paragraphs, html_section
    dp=diagnostic_paragraphs()
    talk='''# 本週教授報告講稿

整理與新診斷日期：2026-10-19。約十分鐘。10/12 的 184 回合為既有研究，本次另新增 40 回合資訊診斷；口頭報告未確認。

## 0–2 分鐘：比較研究的進度

我完成八種控制配置與模型結構的比較，並保留負面結果。先前 PI 在固定測試中追蹤最低，MPC 的風扇 proxy 較低；LQR 沒有勝過 PI。六步排序改善未達門檻，可見量測擬合變好也沒有保證隱藏熱源更準。

## 2–4 分鐘：我如何檢驗 LQR 的可能原因

'''+dp[0]+'''

## 4–6 分鐘：新實驗結果

'''+dp[1]+'''

## 6–8 分鐘：限制與反例

'''+dp[2]+'''

## 8–10 分鐘：我能下的結論與下一步

'''+dp[3]+'\n\n我把新實驗補進完整論文審閱稿與 HTML。LQR 原始論文與詳解仍可一起查閱。下一步想請老師確認應優先隔離控制限制與權重，或準備實機辨識；目前沒有設備資料，尚不能宣稱硬體節能或安全。\n'
    (ROOT/'docs/reports/professor_weekly_script_2026-10-19_zh.md').write_text(talk)
    body='<header><p class="meta">2026-10-19 本週整理｜實驗證據 2026-10-12｜口頭報告未確認</p><h1>方法比較、原因與結論：本週完成進度</h1><p class="status">我完成既有結果覆核、逐方法結論、完整中文論文審閱稿與本週講稿。實機驗證仍待設備；會議尚未選定，尚未投稿。</p><nav><a href="#tasks">交辦對照</a><a href="#results">比較與結論</a><a href="#reasons">原因與邊界</a><a href="#paper">稿件</a><a href="#talk">十分鐘講稿</a><a href="professor_research_2026-10-12_zh.html#lqr">LQR 與原文</a></nav></header>'
    body+='<section id="tasks"><h2>交辦與完成範圍</h2>'+html_table(('本週進度',['教授要求','這次完成','狀態'],[['比較每個方法','八種配置、逐平台與估測／控制分開比較','完成'],['解釋原因','逐方法機制、數據現象、可能原因及驗證缺口','說明完成；因果驗證未做'],['實驗結論','兩階段負面結果與適用條件均保留','完成'],['找臺灣研討會','10/19 重查 CSME 與 ICCE-TW，備妥候選格式全文','準備完成；待選會議'],['LQR 與論文本體','沿用完整詳解、原始 18 頁論文與引用','材料完成'],['實機與投稿','無設備資料；使用者確認未選會議、未投稿','待條件／決定']]))+'<p>這週新增的是完整稿件、覆核與報告整合。10/12 已完成的合成實驗沒有重新命名成新研究成果。</p></section>'
    body+='<section id="results"><h2>各方法比較與實驗結論</h2>'+html_table(data['control_table'])+'<p>PI 在第一階段固定設定中追蹤最低；MPC 較低的風扇 proxy 伴隨稍大的追蹤誤差。PID 與 PI 幾乎相同；LQR 未勝過 PI。六步視野改善未達 5% 判準；無校正的低 proxy 伴隨較多超溫。</p>'+html_table(data['rig_table'])+html_table(data['failure_table'])+'<p>第二階段可見擬合改善仍不能保證隱藏熱源較準。兩階段資料不同，我不把它們合成新排名。<a href="professor_comparison_2026-10-12_zh.html">完整八方法說明與配對回合</a></p></section>'
    body+='<section id="reasons"><h2>哪些原因已知，哪些仍待驗證</h2>'+html_table(('解釋層次',['方法／問題','已知事實','尚未證明'],[['PI/PID','相同估測輸入、固定增益、積分反算；PID 加濾波微分','慢變負載是否是兩者接近的主因'],['LQR','局部模型、固定 Q/R、每步求工作點、共同限幅','尺度、飽和、失配各造成多少差異'],['MPC','同時處罰追蹤、輸入、變化與超溫','調整權重後是否仍有相同取捨'],['六步排序','九個固定請求，增加視野而非序列自由度','視野收益小是否主要來自候選限制'],['結構選擇','對流失配時熱源／空氣容量碰界','參數補償的唯一因果解釋或全域不可辨識性']]))+'<p>我已完成可由現有證據支持的解釋。若要將可能原因提升為因果結論，需先固定新實驗規則，再做新資料消融；目前不把候選驗證寫成已完成成果。</p></section>'
    body+='<section id="paper"><h2>完整中文審閱稿與原始論文</h2><p>稿件涵蓋摘要、熱模型、稀疏校正、八種配置、兩階段評估、逐方法討論、限制、結論及六筆參考文獻；六張資料表從原始結果產生。</p><p><a href="../papers/conference_review_2026-10-19/manuscript_zh.html">閱讀完整稿件 HTML</a> · <a href="../papers/conference_review_2026-10-19/manuscript_zh.pdf">PDF 審閱稿</a> · <a href="../papers/conference_review_2026-10-19/readiness_zh.md">投稿準備與候選會議狀態</a></p><p><a href="../papers/reference_sources/kalman_1960_optimal_control_original.pdf">Kalman 1960 完整原文（18 頁）</a> · <a href="../research/lqr_practical_guide_2026-10-12_zh.md">LQR 十五主題詳解</a></p></section>'
    body+='<section id="talk"><h2>十分鐘第一人稱講稿</h2>'
    for block in talk.split('\n\n'):
        if block.startswith('## '):body+='<h3>'+escape(block[3:])+'</h3>'
        elif not block.startswith('# '):body+='<p>'+escape(block)+'</p>'
    body+='</section><section><h2>可核對的研究來源</h2><p><a href="../../openspec/changes/integrate-enclosure-session-20261012/artifacts/result.json">第一階段結果</a> · <a href="../../openspec/changes/select-enclosure-structure-20261012/artifacts/result.json">第二階段結果</a> · <a href="professor_research_2026-10-12_zh.html#online">公開模擬場景與執行範圍</a></p><p>本週覆核涵蓋全部 184 回合、22,080 筆與 3,128 個原有回合指標；前次實驗、主要論文內容及假設判定保持一致。</p></section>'
    body=body.replace('<a href="#paper">稿件</a>','<a href="#diagnostic">新 LQR 診斷</a><a href="#paper">稿件</a>')
    body=body.replace('<section id="paper">',html_section(html_table)+'<section id="paper">',1)
    body=body.replace('我完成既有結果覆核、逐方法結論、完整中文論文審閱稿與本週講稿。','我完成既有結果覆核，另新增 40 回合 LQR 狀態／模型診斷，並更新完整論文與本週講稿。')
    body=body.replace('實驗證據 2026-10-12','既有證據 2026-10-12；新診斷 2026-10-19')
    body=body.replace('說明完成；因果驗證未做','已完成新模擬資訊介入；權重與限制尚待隔離')
    body=body.replace('這週新增的是完整稿件、覆核與報告整合。','這週先完成稿件與覆核，接著新增 40 回合資訊診斷。')
    body=body.replace('我已完成可由現有證據支持的解釋。若要將可能原因提升為因果結論，需先固定新實驗規則，再做新資料消融；目前不把候選驗證寫成已完成成果。','以上保留原比較提出的問題。新增資訊診斷已隔離狀態與控制器模型的替換效果，結果見下一節；權重、飽和與模型結構的作用仍未被分別隔離。')
    body=body.replace('六筆參考文獻；六張資料表','七筆參考文獻；七張資料表')
    body=body.replace('兩階段評估、逐方法討論','兩階段比較與新資訊診斷、逐方法討論')
    REPORT.write_text(html_page('本週教授報告：方法比較與 LQR 資訊診斷',body))
    (OUT/'tables.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(REPORT)


if __name__=='__main__':build()
