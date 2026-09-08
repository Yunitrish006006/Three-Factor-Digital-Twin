"""Inventory existing citations; does not change manuscript claims or bibliography."""
from pathlib import Path
import re
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ZH = 'docs/thesis/thesis_draft_zh.md'
EN = 'docs/papers/ieee/paper.tex'
BIB = 'docs/papers/ieee/references.bib'
OUT = ROOT / 'docs/thesis/used_papers_inventory_zh.md'

PURPOSE = {
1: '簡化熱動態與 grey-box 建模依據。',
2: '室內溫度動態預測與低參數模型依據。',
3: '物理導向與神經網路結合的建模背景。',
4: 'zonal model 的方法背景與適用範圍。',
5: 'hybrid 空間溫度模型的相似研究及差異定位。',
6: '動態 zonal／送風模型的相似研究及差異定位。',
7: '建築數位孿生研究背景與本研究定位。',
8: '有限觀測、資料同化與室內溫濕度場重建的相似研究。',
9: '感測器配置與 zonal model 的方法背景。',
10: 'IDW baseline 的文獻依據；中文列入書目但未找到編號引用，英文有明確引用。',
11: 'MCP 服務介面文件；屬網站文件。',
12: 'CU-BEMS 資料集描述論文；公開 task-aligned benchmark 的資料來源。',
13: '候選公開資料的適用性盤點；不能據此認定已投入實驗。',
14: 'SML2010 公開比較的資料集來源。',
15: '候選公開資料的適用性盤點；不能據此認定已投入實驗。',
16: '住宅 IEQ 候選資料適用性盤點；不能據此認定已投入實驗。',
17: '熱舒適資料庫描述論文；主稿用於候選資料適用性與舒適目標參考。',
18: '室溫與日光照度聯合實驗的文獻背景。',
19: '日光與熱感知交互作用的文獻背景。',
20: '熱環境、照明與學習表現的房間尺度實驗背景。',
21: '冷氣與自然通風操作的現地量測背景。',
22: '綠建築辦公室 IEQ 與能源使用的現地研究背景。',
23: '住宅冬季 IEQ 的現地量測背景。',
24: '辦公室能源使用與 IEQ 的比較背景。',
25: '工作型態、IEQ 與生產力的比較背景。',
26: '物理基線加 learned residual 的方法啟發，並有本地移植比較。',
27: 'Vanilla Elman RNN 的方法依據；本地同資料 RNN 比較。',
28: 'Kalman 狀態估測架構依據；本地受控濾波比較。',
29: '植物生長環境的動態溫濕度／光照設定值候選應用。',
30: '植物工廠日夜溫差及光週期的候選應用。',
31: '模型濾波的限制與負向結果背景，約束 Kalman 效益主張。',
32: '溫室 EKF 線上參數調整的候選方法背景。',
33: 'E11A thermal-balance 與 data-driven 模型分工的設計參考。',
34: 'BMC 公開資料所對應的伺服器研究背景。',
35: 'E11A 與 BMC 後續實驗的資料來源。',
36: 'AAU 空間估測及 commissioning 系列的資料來源。',
37: '交叉確認 AAU 機房設備及量測背景。',
38: 'E11C 局部 IDW／時空插值的方法依據。',
39: 'E11C 最近鄰搜尋／局部插值的方法依據。',
40: '資料中心 IDW／kriging 的相關方法與研究邊界。',
41: '機架冷卻的動態 state-space 溫度預測方法參考。',
}
TITLES = {
18:'Influence of indoor temperature and daylight illuminance on visual perception',
19:'Daylight affects human thermal perception',
20:"Experimental study on the impact of indoor lighting and thermal environment on university students' learning performance in summer",
21:'Studying the Indoor Environment and Comfort of a University Laboratory: Air-Conditioning Operation and Natural Ventilation Used as a Countermeasure against COVID-19',
22:'Indoor environmental quality and energy use evaluation of a three-star green office building in China with field study',
23:'Indoor environment quality in a low-energy residential building in winter in Harbin',
24:'Comparative study on indoor environment quality of green office buildings with different levels of energy use intensity',
25:'A Comparative Field Study of Indoor Environment Quality and Work Productivity between Job Types in a Research Institute in Korea',
28:'A New Approach to Linear Filtering and Prediction Problems',
30:'Preventing Overgrowth of Cucumber and Tomato Seedlings Using Difference between Day and Night Temperature in a Plant Factory with Artificial Lighting',
13:'Appliances Energy Prediction',15:'Occupancy Detection',
}
GROUPS = [
('建築數位孿生與研究定位', [7]),
('室內熱模型、空間估測與感測器配置', [1,2,3,4,5,6,8,9,10]),
('房間環境、舒適度與現地實驗', list(range(18,26))),
('Residual、RNN 與 Kalman 方法', [26,27,28,31,32]),
('候選植物生長應用', [29,30]),
('機箱、資料中心與局部插值', [33,34,37,38,39,40,41]),
('資料集描述論文', [12,17]),
]


def build():
    zh, en, bib = [(ROOT / p).read_text() for p in (ZH, EN, BIB)]
    bibliography = {}
    for block in re.split(r'(?=@\w+\{)', bib):
        m = re.match(r'@(\w+)\{([^,]+),', block)
        if not m:
            continue
        fields = dict(re.findall(r'^\s*(\w+)\s*=\s*\{(.*)\},?\s*$', block, re.M))
        bibliography[m[2]] = dict(fields, key=m[2], type=m[1], line=bib[:bib.index(block)].count('\n') + 1)
    references = {}
    for match in re.finditer(r'^- \[(\d+)\] (.+)$', zh, re.M):
        no, raw = int(match[1]), match[2]
        doi_match = re.search(r'DOI:\s*(\S+)', raw)
        doi = doi_match[1] if doi_match else None
        b = next((b for b in bibliography.values() if doi and b.get('doi') == doi), None)
        if no in (10,11,35):
            b = bibliography[{10:'shepard1968two',11:'mcp2025',35:'bmcdata2026'}[no]]
        title = ((b or {}).get('title') or TITLES.get(no) or raw).replace('{','').replace('}','')
        references[no] = {
            'id': f'zh-{no}', 'zh_number': no, 'title': title, 'reference': raw,
            'kind': 'dataset' if no in (13,14,15,16,35,36) else 'website' if no == 11 else 'paper',
            'bib_key': (b or {}).get('key'), 'doi': doi,
            'purpose': PURPOSE[no], 'citations': [],
            'bibliography_location': {'path': ZH, 'line': zh[:match.start()].count('\n')+1},
        }
    heading, in_refs = '', False
    for line_no, line in enumerate(zh.splitlines(), 1):
        if line.startswith('# 參考文獻'):
            in_refs = True
        elif in_refs and line.startswith('# 附錄'):
            in_refs = False
        if in_refs:
            continue
        if re.match(r'^#{1,6} ', line):
            heading = line.lstrip('# ')
        for no in set(map(int, re.findall(r'\[(\d+)\]', line))):
            if no in references:
                references[no]['citations'].append({'path':ZH,'line':line_no,'section':heading,'context':line})
    records = list(references.values())
    by_key = {r['bib_key']:r for r in records if r['bib_key']}
    heading = ''
    cited_keys = set()
    for line_no, line in enumerate(en.splitlines(), 1):
        line = re.split(r'(?<!\\)%', line)[0]
        h = re.search(r'\\(?:sub)*section\{([^}]+)\}', line)
        if h:
            heading = h[1]
        for match in re.finditer(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', line):
            for key in map(str.strip, match[1].split(',')):
                cited_keys.add(key)
                if key not in by_key:
                    b = bibliography[key]
                    r = {'id':key,'zh_number':None,'title':b.get('title',key),'reference':f"{b.get('author','')}, {b.get('title','')}, {b.get('journal','')}, {b.get('year','')}.", 'kind':'paper' if b['type'] in ('article','inproceedings') else 'reference','bib_key':key,'doi':b.get('doi'),'purpose':'英文稿 Related Work 的數位孿生定義、技術及研究挑戰背景。','citations':[], 'bibliography_location':{'path':BIB,'line':b['line']}}
                    by_key[key] = r
                    records.append(r)
                by_key[key]['citations'].append({'path':EN,'line':line_no,'section':heading,'context':line})
    used = [r for r in records if r['kind']=='paper' and r['citations']]
    bib_only = [b for k,b in bibliography.items() if k not in cited_keys and k not in {r['bib_key'] for r in references.values()}]
    summary = {'used_external_papers':len(used),'dataset_records':sum(r['kind']=='dataset' for r in records),'website_records':sum(r['kind']=='website' for r in records),'english_only_papers':sum(r['kind']=='paper' and r['zh_number'] is None for r in records)}
    data = {'scope':'Existing Chinese/IEEE manuscript citations; no external full-text verification performed.', 'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (ZH,EN,BIB)},'summary':summary,'records':records,'bib_only_not_used':bib_only}
    output = ['# 主稿實際使用論文清單', '', '盤點日期：2026-09-08。此文件盤點中英文正式來源的既有引用，不更動研究結論。', '',
      f"合計 **{len(used)} 篇外部論文**（含 2 篇資料集描述論文），另有 **6 筆資料集、1 份網站文件**。中文書目涵蓋 34 篇外部論文；英文稿另引用 Tao 2019 與 Fuller 2020。主論文本身不計入外部文獻。", '',
      '原 3D 視圖的 35 篇＝主論文 1 篇＋中文書目中的外部論文 34 篇；因此不能當成中英文合併後的外部論文總數。', '',
      '以下「用途」是對主稿引用方式的整理；不代表已重新閱讀外部全文，也不代表原論文的章節、頁碼或實驗結果已核實。DOI 沿用現有書目。', '',
      '## 閱讀索引', '',
      '| 類別 | 論文編號 |', '| --- | --- |']
    for title, ids in GROUPS:
        output.append(f"| {title} | {', '.join('['+str(n)+']' for n in ids)} |")
    output += ['| 英文稿獨有的數位孿生文獻 | Tao 2019、Fuller 2020 |', '',
      '## 逐篇清單', '']
    def location(c):
        rel = '../papers/ieee/paper.tex' if c['path']==EN else 'thesis_draft_zh.md'
        return f"{c['section']}（[{c['path'].split('/')[-1]} L{c['line']}]({rel}#L{c['line']})）"
    for group, ids in GROUPS + [('英文稿獨有文獻', [r['id'] for r in used if r['zh_number'] is None])]:
        output += [f'### {group}', '']
        for key in ids:
            r = references[key] if isinstance(key,int) else next(r for r in records if r['id']==key)
            if r['kind']!='paper':continue
            prefix = f"[{r['zh_number']}]" if r['zh_number'] else r['bib_key']
            output += [f"#### {prefix} {r['title']}", '', f"- 書目：{r['reference']}",f"- 本論文用途：{r['purpose']}"]
            locs = list(dict.fromkeys(location(c) for c in r['citations']))
            output += ['- 實際引用位置：' + ('；'.join(locs) or '正文未找到明確引用。')]
            if r['doi']:output += [f"- 原文入口：[DOI](https://doi.org/{r['doi']})。"]
            if r['zh_number']==26:
                output += ['- 比較邊界：有 Oh2024-inspired 本地方法移植；不等於原文 CNN–LSTM、物理模擬器或原始 BEMS 資料的重現，不能直接宣稱勝過原論文。']
            elif r['zh_number'] in (10,27,28,38,39,40,41):
                output += ['- 比較邊界：方法引用與本地 baseline／實驗比較須分開記錄；本地數值不等同原论文數值。'.replace('原论文','原論文')]
            else:output += ['- 比較邊界：此處記錄引用用途，未建立與原文相同資料／任務的直接優劣比較。']
            output += ['']
    output += ['## 資料集與網站文件', '', '| 編號 | 來源 | 用途／引用位置 |','| --- | --- | --- |']
    for r in records:
        if r['kind']=='paper':continue
        output += [f"| [{r['zh_number']}] | {r['title']} | {r['purpose']} {'；'.join(dict.fromkeys(location(c) for c in r['citations']))} |"]
    output += ['', '## 只在 BibTeX 中、未在兩份主稿找到引用的其他項目', '']
    for b in bib_only:output += [f"- `{b['key']}`：{b.get('title','')}。不計入已使用清單。"]
    output += ['', '## 後續對應到 3D 視圖的資料', '',
      '同名 JSON 保存逐筆引用的原始段落、章節、行號、BibTeX key、DOI 與來源 SHA-256。可用於補入英文稿獨有論文與修正論文計數；本輪只完成清單，尚未變更 3D 視圖。', '',
      '外部原文論點與頁碼仍需逐篇核對，不能把本清單的「主稿引用段落」當作對方原文的定位。', '',
      '重建：`python3 scripts/build_used_papers_inventory.py`。', '']
    OUT.write_text('\n'.join(output))
    OUT.with_suffix('.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
    assert len({r['id'] for r in records}) == len(records)
    assert all(r['citations'] for r in used)
    assert len(used)==36, 'Citation inventory changed; inspect before publishing the count.'

if __name__ == '__main__':build()
