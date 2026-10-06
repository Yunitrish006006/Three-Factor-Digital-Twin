"""Render the existing reading notes without inventing reading dates or coverage."""
from html import escape
import json
import re


def reading_section(root):
    inventory=json.loads((root/'docs/thesis/used_papers_inventory_zh.json').read_text())
    papers=[r for r in inventory['records'] if r['kind']=='paper']
    numbered={r['zh_number']:r for r in papers if r.get('zh_number') is not None}

    def record(number, status):
        r=numbered[number]
        authors=r['reference'].split(r['title'],1)[0].strip(' ,')
        years=re.findall(r'\b(?:19|20)\d{2}\b',r['reference'].split('DOI:')[0])
        return (r['title'],authors,years[-1] if years else '書目未記錄',
                'https://doi.org/'+r['doi'] if r.get('doi') else '',r['purpose'],status)

    def table(items):
        rows=[]
        for title,authors,year,url,purpose,status in items:
            label=escape(title)
            if url:label=f'<a href="{escape(url,quote=True)}">{label}</a>'
            rows.append(f'<tr><td>{label}<br><span class="source">{escape(authors)} · {escape(year)}</span></td><td>{escape(purpose)}</td><td>{escape(status)}</td></tr>')
        return '<div class="table-wrap"><table><thead><tr><th>論文／作者／發表年</th><th>對我的研究用途</th><th>查閱紀錄</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

    def group(title,items,source,label):
        return '<h3 style="margin-top:24px">'+escape(title)+'</h3>'+table(items)+f'<p class="source">依據：<a href="{source}">{label}</a>。</p>'

    parts=['''<section id="reading"><h2>各階段查閱的論文與文獻清單</h2><p>我依既有閱讀筆記與引用盤點，列出各階段參考哪些論文、想借用哪些做法，以及查閱到哪裡。日期表示筆記所記錄的查閱階段；作者旁的年份是論文發表年。沒有逐篇閱讀日期的部分按研究階段整理。</p>''']
    core=[record(n,'已有閱讀筆記；逐篇全文覆蓋未記錄') for n in (7,1,2,6,8,5,4,9)]
    core.append(('Fast prediction for indoor environment: Models assessment','Zhuangbo Feng, Chuck Wah Yu, Shi-Jie Cao','2019','https://doi.org/10.1177/1420326X19852450','快速室內模型與即時推估的選擇依據。','已有閱讀筆記；逐篇全文覆蓋未記錄'))
    parts.append(group('前期・主模型與稀疏感測（閱讀日未留存）',core,'../models/model_reading_notes_zh.md','主模型閱讀筆記'))
    parts.append(group('前期・殘差學習、RNN與濾波（逐次閱讀日未留存）',
        [record(n,'既有引用／相關方法工作；全文查閱程度未逐篇記錄') for n in (26,27,28,31,32)],
        '../thesis/used_papers_inventory_zh.md','既有引用與用途盤點'))
    equipment=[
        ('Model and data driven transient thermal system modelings for contained data centers','Wang et al.','2022','https://doi.org/10.1016/j.enbuild.2021.111790','參考熱節點ODE與資料驅動模型的同場比較。','候選文獻盤點；全文查閱程度未記錄'),
        ('A time-varying state-space model for real-time temperature predictions in rack-based cooling data centers','Tong et al.','2023','https://doi.org/10.1016/j.applthermaleng.2023.120737','參考動態狀態空間、回流與旁通的建模。','候選文獻盤點；全文查閱程度未記錄'),
        ('Energy efficiency enhancement in two European data centers through CFD modeling','Melgaard et al.','2025','https://doi.org/10.1038/s41598-025-11048-0','參考入口／出口測點、airflow與量測不確定度。','候選文獻盤點；全文查閱程度未記錄'),
        ('Thermal Elasticity-Aware Host Resource Provision for Carbon Efficiency on Virtualized Servers','Zhang et al.','2025','https://doi.org/10.1109/TC.2025.3603698','參考BMC遙測、負載與風扇模式的資料需求。','候選文獻盤點；全文查閱程度未記錄')]
    parts.append(group('前期・機箱／機房轉移的候選文獻（閱讀日未留存）',equipment,'../experiments/equipment_enclosure_literature_and_datasets_zh.md','機箱／設備櫃文獻筆記'))
    precision=[
        ('Auto-tuned variable structure control of cleanrooms','K. K. Tan, Q. G. Wang, T. H. Lee, C. H. Gan','1998','https://doi.org/10.1016/S0019-0578(98)00029-9','受控擾動、物理模型辨識與自動調適的既有先例。','當時查閱作者機構摘要'),
        ('Multivariable Model Predictive Control of Cleanroom Pressure Cascades','Branislav M. Jeremić, Aleksandar Ž. Rakić','2025','https://doi.org/10.3390/electronics14163296','系統辨識與MPC設計的參考；任務是壓差串級。','當時查閱出版社索引；全文存取受限'),
        ('Safe Contextual Bayesian Optimization for Sustainable Room Temperature PID Control Tuning','Marcello Fiducioso et al.','2019','https://arxiv.org/abs/1906.12086','參考外溫條件化PI調參與commissioning；調控制增益與辨識模型參數須分開。','筆記定位§4–5及§7.3；未宣稱全文逐頁核對'),
        ('OpenHumidistat: Humidity-controlled experiments for everyone','Lars B. Veldscholte, Sissi de Beer','2022（2021預印本）','https://doi.org/10.1016/j.ohx.2022.e00288','乾／濕氣流混合與濕度回授的可介入平台備案。','當時僅核對摘要')]
    parts.append(group('9月上旬・環境調參與平台探索（9/8筆記）',precision,'../research/precision_environment_pid_data_review_2026-09-08_zh.md','精密環境與資料初查'))
    cooling=[
        ('Data center cooling using model-predictive control','Nevena Lazic et al.','2018','https://papers.neurips.cc/paper_files/paper/2018/hash/059fdcd96baeb75112f09fa1dcc740cc-Abstract.html','ARX動態辨識、多步預測與滾動控制的機箱移植參考。','已取得PDF文字；筆記定位§4.1、Eq.(1)、Table 1、§4.2／§5.1'),
        ('PTEC: A System for Predictive Thermal and Energy Control in Data Centers','Jinzhu Chen, Rui Tan, Guoliang Xing, Xiaorui Wang','2014','https://personal.ntu.edu.sg/tanrui/pub/control-rtss14.pdf','入口溫度／負載前饋、預測誤差裕量與風扇功耗。','已取得PDF文字；筆記定位§IV-A、§V-A／Eq.(2)、§V-C'),
        ('Optimal Self-Tuning PID Controller Based on Low Power Consumption for a Server Fan Cooling System','Chengming Lee, Rongshun Chen','2015','https://doi.org/10.3390/s150511685','風扇功率曲線、PIDNN與公平的耗能／暫態比較。','已取得索引相關段落；當時直接全文端點受限'),
        ('Adaptive physically consistent neural networks for data center thermal dynamics modeling','Dong Chen, Chee-Kong Chui, Poh Seng Lee','2025','https://doi.org/10.1016/j.apenergy.2024.124637','固定物理骨架與自適應係數的候選建模方向。','查閱Abstract／Introduction索引；完整方程尚未核對'),
        ('Self-Tuning Fully-Connected PID Neural Network System for Distributed Temperature Sensing and Control of Instrument with Multi-Modules','Zhen Zhang, Cheng Ma, Rong Zhu','2016','https://doi.org/10.3390/s16101709','多測點、多風扇耦合控制的後續候選。','已取得索引相關段落；筆記定位§2.2、Figure 1')]
    parts.append(group('9月上旬・機箱控制與模型遷移（9/8筆記）',cooling,'../research/enclosure_temperature_control_method_selection_zh.md','五篇機箱候選論文'))
    parts.append('''<p class="source">環境PID筆記也引用Lee與Chen（2015）的自調PID研究。另查到的EP3660323A1屬專利，TCLab／BOPTEST屬平台或官方文件，未混計為論文。</p>
<h3 style="margin-top:24px">本輪方法實作・查閱的官方方法文件</h3><p>這輪方法紀錄列出的新增來源是官方範例與文件；未記錄新增原始PID／LQR論文的全文閱讀。既有論文保留在上方研究脈絡。</p><ul>
<li><a href="https://osqp.org/docs/examples/mpc.html">OSQP：MPC官方範例</a>——有限預測、限制與每步重新求解。</li>
<li><a href="https://osqp.org/docs/interfaces/solver_settings.html">OSQP：求解設定</a>——數值容差、迭代與求解設定。</li>
<li><a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html">SciPy：solve_discrete_are</a>——LQR使用的離散Riccati方程求解。</li>
<li><a href="https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html">SciPy：SLSQP</a>——第一階段受限制最佳化實作來源。</li></ul><p class="source">依據：<a href="../research/enclosure_control_v2_method_2026-10-05_zh.md">本輪方法來源</a>、<a href="../research/enclosure_mpc_method_2026-10-05_zh.md">第一階段方法來源</a>。</p>''')
    appendix=[]
    for r in papers:
        url='https://doi.org/'+r['doi'] if r.get('doi') else ''
        title=escape(r['title'])
        if url:title=f'<a href="{escape(url,quote=True)}">{title}</a>'
        appendix.append(f'<li><strong>{title}</strong><p>{escape(r["reference"])}</p><p>用途：{escape(r["purpose"])}</p></li>')
    parts.append(f'<details id="reading-citations"><summary>展開既有引用盤點：{len(papers)}篇外部論文完整書目</summary><p>這是既有主稿的引用盤點，不代表本輪重新閱讀{len(papers)}篇，也不作為逐篇全文閱讀證明。未逐篇重新查證的書目沿用原清單。</p><ol>'+''.join(appendix)+'</ol><p class="source"><a href="../thesis/used_papers_inventory_zh.md">原引用清單</a> · <a href="../thesis/used_papers_inventory_zh.json">原始盤點資料</a></p></details>')
    parts.append('<p class="callout"><strong>下週閱讀紀錄：</strong>新增查閱時逐篇記錄實際日期、題名、作者／年份、原文連結、讀到的章節／公式、可借鑑的機制與適用限制，再對應到自己模型的辨識、校正或決策改進。</p></section>')
    return '\n'.join(parts)
