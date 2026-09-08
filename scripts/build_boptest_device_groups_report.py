"""Descriptive grouping report, never a controller selection rule."""
import json
from pathlib import Path
from build_boptest_delayed_dynamics_report import table,sha,ROOT
ART=ROOT/'openspec/changes/analyze-boptest-device-groups/artifacts'
LABEL={'BOTH_IMPROVE':'兩天皆改善','BOTH_WORSEN':'兩天皆退步','MIXED':'混合結果','EXACT_FALLBACK':'停用持平','REJECTED':'辨識拒絕'}
NAMES={'air':'送風','hydronic':'水暖散熱器','heat_pump':'熱泵地暖','apartment':'公寓日間区','commercial':'商用散熱器'}

def main():
    d=json.loads((ART/'device_groups.json').read_text());rows=[]
    for e in d['groups']:
        m=e.get('model',{});ps=e['pairs'];mean=lambda k:sum(x[k] for x in ps)/len(ps) if ps else None
        fmt=lambda v:'—' if v is None else f'{v:.4f}'
        rows.append([NAMES[e['plant']],e['budget_h'],LABEL[e['group']],fmt(m.get('tau_min')),fmt(m.get('G10')),fmt(m.get('validation_rmse_C')),fmt(mean('correction_at_bound_pct')),fmt(mean('mae_gain_C')),'通過' if e['gate'] else '未通過'])
    sections=[('有共同特徵，但不能直接依設備名稱分類','<p class="lead">目前最清楚的描述性關聯是：穩定退步組的補償更常長時間頂住限幅。模型速度與短期反應也有幫助，但無法單獨分出好壞；同一商用設備只改資料量，結果就會反轉。</p><p>資料只有五種已參與開發的 FMU，同設備不同日期與資料量也非獨立樣本。以下是事後分析，不能当成因果證明、通用分類器或直接拿來調控制參數。</p>'),
    ('群體劃分',table(['群體','設備／辨識資料','共同觀察'],[
    ['兩天皆改善','送風2h、送風6h、商用2h','平均補償碰限幅約23–27%；辨識時間尺度約4–19min。'],
    ['兩天皆退步','水暖2h、商用6h','平均補償碰限幅約66–88%；長期偏置補償可能不適合目前模型／工作條件。'],
    ['混合','水暖6h','一天微幅退步、一天改善；原定整體門檻通過，不能說每個日期都改善。'],
    ['停用持平','熱泵2h／6h、公寓2h','辨識時間尺度約81–234min，10min反應很弱或為零；共用規則停用補償。'],
    ['辨識拒絕','公寓6h','沒有可用模型，不能歸類成控制效果差或持平。']])+'<p>碰限幅是額外補償達到±0.1，與致動器到0／1的飽和不同。表中的比例是每組兩個日期的算術平均。</p>'),
    ('最有辨識力的線索：補償持續碰限幅','<p>水暖2h在兩天分別有35.8%、97.0%的時間碰到補償限幅；商用6h為98.3%、78.0%。相比之下，送風與商用2h的兩日平均約23–27%。這表示退步組更常要求持續較大的修正，而不只是偶爾修補偏差。</p><p>可能是模型的持續偏差被當成擾動、補償與積分作用互相影響，或模型在新工作條件不適用；本輪沒有消融或介入實驗分離這些原因。水暖6h第25天也有54.6%碰限幅，卻只出現極小MAE損失，所以碰限幅比例不是已證實的判定門檻。</p>'),
    ('反應速度：能解釋停用，不能單獨解釋成敗','<p>送風辨識時間尺度約4.1min，水暖2h約113.4min；熱泵約80.8／192.3min，公寓2h約234.1min。這些是辨識極點推得的時間尺度，不是真實設備時間常數的獨立量測。</p><p>熱泵的10min單位指令反應約0.00348／0.00739°C，遠弱於送風約10.84°C；以允許的0.1指令修正計算，熱泵反應更低於0.02°C誤差尺度。公寓辨識延遲10min，等於補償視窗，因此短期反應為0。停用是這套公式的直接結果，不是證明它們永遠無法受益。</p><p>但商用2h與6h時間尺度都約19min、10min反應約0.22°C，效果卻一好一壞。所以不能只用「快設備好、慢設備差」來下結論。</p>'),
    ('最重要反例：預測更準，控制仍可能變差','<p>商用設備的校正10min推演RMSE由2h資料的0.01894°C降到6h資料的0.00517°C，但6h版本兩天都退步，補償也更常頂住限幅。這兩個校正分數來自不同驗證區段，不能當成相同測試資料上的預測優勝；它們至少提醒我們，較小的模型選擇分數不能直接保證更好的控制。</p><p>反向例子是水暖：2h兩天退步，6h改為混合且整體門檻通過。因此資料多寡本身也不是共通的成敗規則。</p>'),
    ('所有組合的數據',table(['設備','辨識h','原始MAE分組','辨識時間尺度min','10min單位反應°C','校正推演RMSE°C','平均補償碰限幅%','平均MAE增益°C','原控制門檻'],rows)+'<p>平均MAE增益＝基準−新版；正值改善。分組依兩天原始數值符號，沒有把微小損失改標持平。門檻還包含最大誤差、指令TV與允許的不退步幅度，因此與分組是不同判斷。</p>'),
    ('下一步研究問題','<p>優先檢驗「持續補償偏置」與模型誤差的關係，並研究跨設備共用的補償效益／資料充分性判斷。需要先訂新協定與評估條件，不能直接用上述23%或66%作為關閉門檻。</p><p>若要測慢速蓄熱設備，還需評估較長模型驗證與控制視窗是否值得增加資料及計算成本。本輪沒有追加模擬、換模型或改算法。</p>'),
    ('來源與3D同步','<p><a href="../../openspec/changes/analyze-boptest-device-groups/artifacts/device_groups.json">全部特徵與輸入雜湊</a> · <a href="../../openspec/changes/analyze-boptest-device-groups/evidence.md">分析紀錄</a> · <a href="boptest_consistent_2026-09-08_zh.html">原實驗完整報告</a></p><p>3D圖的「裝置群體分析」會保留每個設備／資料預算的原始特徵與群體判讀，連回原實驗結果。這是未採納主論文的事後描述性分析。</p>')]
    body=''.join(f'<section><small>{i:02}</small><h2>{title}</h2>{text}</section>' for i,(title,text) in enumerate(sections,1))
    page=ROOT/'docs/reports/boptest_device_groups_2026-09-08_zh.html'
    page.write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>進步與退步設備的共同特徵</title><style>body{font:18px/1.8 system-ui;background:#edf3f6;color:#16364a;margin:0}main{max-width:1280px;margin:auto;padding:28px}section{background:white;padding:30px;margin:25px 0;border-radius:14px}h1{font-size:36px}h2{font-size:27px}.lead{font-size:24px}small{float:right;color:#678}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:left}th{background:#edf4f7}.scroll{overflow:auto}a{color:#00728a}@media print{section{break-before:page}body{background:white}}@media(max-width:600px){main{padding:10px}section{padding:15px}}</style><main><h1>進步與退步設備，有什麼共同特徵？</h1><p>2026-09-08 · 五FMU／事後描述性分析 · 不作因果推論</p>'''+body+'</main></html>')
    page.with_suffix('.json').write_text(json.dumps(dict(status='DESCRIPTIVE_ONLY',html_sha256=sha(page),builder_sha256=sha(Path(__file__)),analysis_sha256=sha(ART/'device_groups.json')),indent=2)+'\n');print(page)
if __name__=='__main__':main()
