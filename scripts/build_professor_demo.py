# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs" / "demos" / "professor_two_week_demo_2026-08-04_2026-08-17_zh.html"
SUBMISSION_SUMMARY = ROOT / "outputs" / "data" / "submission_readiness_summary.json"
BEDROOM_SUMMARY = ROOT / "outputs" / "data" / "bedroom_01_weekly" / "weekly_simulation_summary.json"
RNN_SUMMARY = ROOT / "outputs" / "data" / "public_benchmarks" / "rnn_sml2010_comparison.json"
RNN_3D_SUMMARY = ROOT / "outputs" / "data" / "rnn_3d_field_comparison.json"
KALMAN_SUMMARY = ROOT / "outputs" / "data" / "public_benchmarks" / "kalman_sml2010_filtering_comparison.json"
E8_SUMMARY = ROOT / "outputs" / "data" / "e8_intervention_summary.json"


def build_professor_demo(output_path: Path = DEFAULT_OUTPUT) -> Path:
    submission = _read_json(SUBMISSION_SUMMARY)
    bedroom = _read_json(BEDROOM_SUMMARY)
    rnn = _read_json(RNN_SUMMARY)
    rnn_3d = _read_json(RNN_3D_SUMMARY)
    kalman = _read_json(KALMAN_SUMMARY)
    e8 = _read_json(E8_SUMMARY)
    if rnn.get("status") != "COMPLETE" or rnn_3d.get("status") != "COMPLETE" or kalman.get("status") != "COMPLETE":
        raise ValueError("Professor demo requires COMPLETE temporal RNN, 3-D RNN, and Kalman evidence.")

    variants = submission["base_ablation"]["variants"]
    idw = variants["idw"]["average_field_mae"]
    base = variants["full_base"]["average_field_mae"]
    hybrid = submission["leave_one_scenario_out"]["average_hybrid_field_mae"]
    pure_rnn = rnn_3d["summary"]["average_field_mae"]["pure_rnn"]
    bedroom_aggregate = bedroom["aggregate"]
    rnn_counts = rnn["summary"]["lowest_mae_counts"]
    kalman_counts = kalman["summary"]["lowest_mae_counts"]
    representative = _representative_kalman_case(kalman["cases"])
    generated_at = datetime.now(timezone.utc).isoformat()

    comparison_cards = _comparison_cards(idw=idw, base=base, pure_rnn=pure_rnn, hybrid=hybrid)
    rnn_3d_rows = _rnn_3d_rows(rnn_3d["summary"]["average_field_mae"])
    rnn_case_rows = _rnn_rows(rnn["cases"])
    bedroom_rows = _bedroom_rows(
        bedroom_aggregate["raw_pillow_mae"], bedroom_aggregate["estimated_pillow_mae"]
    )
    kalman_rows = _kalman_rows(kalman["cases"])
    trace_svg = _trace_svg(representative["preview"])
    adverse_rows = "".join(
        "<tr>"
        f"<td>{_target_label(case['target'])}</td>"
        f"<td>{_profile_label(case['noise_profile'])}</td>"
        f"<td>{_method_label(case['winner'])}</td>"
        f"<td>{float(case['winner_mae']):.4f}</td>"
        f"<td>{float(case['kalman_mae']):.4f}</td>"
        "</tr>"
        for case in kalman["summary"]["adverse_cases"]
    )

    document = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>兩週研究成果教授 Demo｜2026-08-04 至 2026-08-17</title>
  <style>
    :root {{ --ink:#172033; --muted:#667085; --paper:#f4f7fb; --card:#fff; --navy:#173b66; --blue:#2f80ed; --green:#1f9d68; --orange:#ee8b2d; --red:#d24b4b; --line:#dce4ef; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif; color:var(--ink); background:var(--paper); line-height:1.62; }}
    header {{ padding:48px max(24px,calc((100vw - 1120px)/2)); color:white; background:linear-gradient(120deg,#102d50,#1e5d8f 65%,#278b91); }}
    header .eyebrow {{ letter-spacing:.14em; font-size:13px; opacity:.78; }}
    header h1 {{ max-width:850px; margin:8px 0 10px; font-size:clamp(30px,5vw,52px); line-height:1.15; }}
    header p {{ max-width:840px; margin:0; font-size:18px; opacity:.9; }}
    nav {{ position:sticky; top:0; z-index:10; display:flex; gap:8px; padding:10px max(18px,calc((100vw - 1120px)/2)); overflow:auto; background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); backdrop-filter:blur(10px); }}
    nav button {{ white-space:nowrap; border:0; border-radius:999px; padding:9px 14px; color:var(--navy); background:#edf3fa; cursor:pointer; font-weight:700; }}
    main {{ max-width:1120px; margin:auto; padding:28px 20px 70px; }}
    section {{ scroll-margin-top:72px; margin:0 0 32px; }}
    h2 {{ margin:0 0 14px; color:var(--navy); font-size:28px; }}
    h3 {{ margin:0 0 10px; font-size:19px; }}
    .grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }}
    .card {{ grid-column:span 6; padding:22px; background:var(--card); border:1px solid var(--line); border-radius:18px; box-shadow:0 8px 25px rgba(26,50,75,.055); }}
    .wide {{ grid-column:1/-1; }} .third {{ grid-column:span 4; }}
    .metric {{ font-size:36px; font-weight:800; color:var(--navy); line-height:1.05; }}
    .label {{ color:var(--muted); font-size:14px; }}
    .tag {{ display:inline-block; margin:2px 4px 2px 0; padding:4px 9px; border-radius:999px; font-size:12px; font-weight:800; background:#e8f3ff; color:#1e5f9f; }}
    .tag.good {{ background:#e9f8f1; color:#157653; }} .tag.warn {{ background:#fff2df; color:#985814; }} .tag.bad {{ background:#fdeaea; color:#9b2e2e; }}
    .bar-row {{ display:grid; grid-template-columns:120px 1fr 90px; gap:10px; align-items:center; margin:7px 0; font-size:14px; }}
    .track {{ height:10px; overflow:hidden; background:#edf1f6; border-radius:999px; }} .fill {{ height:100%; border-radius:inherit; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }} th,td {{ padding:10px 9px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }} th {{ color:#42526a; background:#f8fafc; }}
    .table-wrap {{ overflow:auto; }} .callout {{ padding:16px 18px; border-left:5px solid var(--orange); border-radius:8px; background:#fff7e9; }}
    .command {{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin:10px 0; padding:13px 15px; color:#eaf2fb; background:#13233a; border-radius:10px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; overflow:auto; }}
    .command button {{ border:1px solid #58718d; border-radius:7px; padding:6px 9px; color:white; background:#284866; cursor:pointer; }}
    .trace {{ width:100%; height:auto; border:1px solid var(--line); border-radius:12px; background:white; }}
    .legend {{ display:flex; flex-wrap:wrap; gap:14px; margin-top:8px; font-size:13px; }} .dot {{ display:inline-block; width:10px; height:10px; margin-right:5px; border-radius:50%; }}
    footer {{ padding:24px; text-align:center; color:var(--muted); border-top:1px solid var(--line); }}
    @media(max-width:760px) {{ .card,.third {{ grid-column:1/-1; }} .bar-row {{ grid-template-columns:96px 1fr 76px; }} }}
    @media print {{ nav,.copy {{ display:none; }} body {{ background:white; }} .card {{ box-shadow:none; break-inside:avoid; }} }}
  </style>
</head>
<body>
<header><div class="eyebrow">PROFESSOR RESEARCH DEMO · TWO-WEEK PROGRESS</div><h1>稀疏感測空間數位孿生：兩週研究成果展示</h1><p>期間：2026-08-04 至 2026-08-17。聚焦同資料模型比較、Kalman 受控去噪、20–30°C 應用邊界與可操作系統展示。</p></header>
<nav><button onclick="go('overview')">兩週摘要</button><button onclick="go('progress')">前後對比</button><button onclick="go('rnn')">RNN</button><button onclick="go('kalman')">Kalman</button><button onclick="go('live')">實際 Demo</button><button onclick="go('limits')">研究邊界</button></nav>
<main>
  <section id="overview"><h2>兩週交付摘要</h2><div class="grid">
    <article class="card"><span class="tag good">第一週</span><h3>Pure RNN 3-D 與時序公平比較</h3><div class="metric">0/24 · 0/12</div><div class="label">3-D fold×因子／SML2010 時序最低 MAE 次數</div><p>兩種 RNN 任務均完成資料 parity，負向結果保留；3-D pure RNN 不使用 physics estimate。人體舒適改採 tolerance，精準動態應用限制於 20–30°C 候選情境。</p></article>
    <article class="card"><span class="tag good">第二週</span><h3>Kalman 受控同資料比較</h3><div class="metric">{int(kalman_counts['linear_kalman_random_walk'])} : {int(kalman_counts['causal_moving_average_3'])}</div><div class="label">Kalman 與 causal MA(3) 最低 MAE 案例數</div><p>12/12 案例完成；Kalman 全部勝過未濾波，但在溫度 6 案例均不如簡單移動平均。</p></article>
    <article class="card third"><div class="metric">20–30°C</div><div class="label">目前室內適用範圍</div></article><article class="card third"><div class="metric">{int(bedroom['snapshot_count'])}</div><div class="label">真實臥室 snapshots</div></article><article class="card third"><div class="metric">{html.escape(str(e8['evidence_status']))}</div><div class="label">真實推薦介入狀態</div></article>
  </div></section>
  <section id="progress"><h2>先前表現與改進後對比</h2><div class="grid">{comparison_cards}<article class="card wide"><h3>相同 SML2010 資料的時序模型比較（包含 RNN）</h3><div class="table-wrap"><table><thead><tr><th>目標</th><th>Horizon</th><th>Persistence</th><th>Sequence LR</th><th>Physics readout</th><th>Vanilla RNN</th><th>最低 MAE</th></tr></thead><tbody>{rnn_case_rows}</tbody></table></div><div class="callout"><strong>公平比較：</strong>12/12 案例使用相同 history、split、targets 與 test rows。RNN 是時序預測模型，不能和上方 3-D field reconstruction 的 IDW／Base／LOO hybrid MAE 混算。</div></article><article class="card wide"><h3>真實臥室 pillow 保留點：校正前後</h3><div class="table-wrap"><table><thead><tr><th>環境因子</th><th>校正前 MAE</th><th>校正後 MAE</th><th>相對下降</th></tr></thead><tbody>{bedroom_rows}</tbody></table></div><p class="label">證據只涵蓋一個房間、一個 held-out pillow 位置與七個觀察日期，不代表 dense 3-D ground truth。</p></article></div></section>
  <section id="rnn"><h2>Demo 1｜兩種 RNN 同資料公平比較</h2><div class="grid"><article class="card wide"><h3>完整 3-D 場：八情境 LOO 平均 field MAE</h3><div class="table-wrap"><table><thead><tr><th>方法</th><th>溫度</th><th>濕度</th><th>照度</th></tr></thead><tbody>{rnn_3d_rows}</tbody></table></div><div class="callout"><strong>結果：</strong>Pure RNN 最低 MAE 0/24；LOO hybrid 為 24/24。這是 controlled synthetic full-field evidence，不是任意真實房間結果。</div></article><article class="card wide"><h3>SML2010 時序預測</h3><div class="table-wrap"><table><thead><tr><th>最低 MAE 方法</th><th>案例數</th><th>解讀</th></tr></thead><tbody>
    <tr><td>Sequence linear regression</td><td>{int(rnn_counts['sequence_linear_regression'])}/12</td><td>相同四筆歷史下，簡單線性序列模型最常勝出。</td></tr><tr><td>Persistence</td><td>{int(rnn_counts['persistence'])}/12</td><td>長時間慣性仍是強基準。</td></tr><tr><td>Physics-structured readout</td><td>{int(rnn_counts['physics_structured_readout'])}/12</td><td>此 public task 沒有取得最低 MAE。</td></tr><tr><td>Vanilla RNN</td><td>{int(rnn_counts['vanilla_rnn'])}/12</td><td>固定小型 recurrent architecture 未建立優勢。</td></tr>
  </tbody></table></div><div class="callout"><strong>研究判斷：</strong>「加入 RNN」不等於「RNN 一定改善」。所有方法使用相同 history、split、target 與 test rows，負向結果仍是有效研究成果。</div></article></div></section>
  <section id="kalman"><h2>Demo 2｜Kalman Filter 受控去噪</h2><div class="grid">
    <article class="card wide"><h3>12 個 target × noise-profile 案例</h3><div class="table-wrap"><table><thead><tr><th>目標</th><th>雜訊</th><th>Raw MAE</th><th>MA(3) MAE</th><th>Kalman MAE</th><th>最低</th></tr></thead><tbody>{kalman_rows}</tbody></table></div></article>
    <article class="card wide"><h3>代表性 current-time trace：{_target_label(representative['target'])}／{_profile_label(representative['noise_profile'])}</h3>{trace_svg}<div class="legend"><span><i class="dot" style="background:#172033"></i>reference</span><span><i class="dot" style="background:#d24b4b"></i>corrupted</span><span><i class="dot" style="background:#ee8b2d"></i>MA(3)</span><span><i class="dot" style="background:#2f80ed"></i>Kalman</span></div></article>
    <article class="card wide"><h3>必須保留的 adverse cases</h3><div class="table-wrap"><table><thead><tr><th>目標</th><th>雜訊</th><th>勝出方法</th><th>勝出 MAE</th><th>Kalman MAE</th></tr></thead><tbody>{adverse_rows}</tbody></table></div><div class="callout">溫度 6 案例全部由 causal MA(3) 勝出；濕度 6 案例由 Kalman 勝出。因此結論是「方法與變數動態有關」，不是「Kalman 普遍最佳」。</div></article>
  </div></section>
  <section id="live"><h2>Demo 3｜實際房間系統操作</h2><div class="grid">
    <article class="card"><h3>離線成果頁</h3><p>本頁可直接雙擊開啟，不需啟動服務。適合先用 3–5 分鐘說明研究結果與限制。</p><span class="tag good">可離線</span><span class="tag">數值來自 JSON</span></article>
    <article class="card"><h3>Live Web Demo</h3><p>啟動後可操作冷氣、窗戶、照明、時間與 estimator，旋轉 3-D 場、查詢點位並查看候選動作排序。</p><span class="tag good">實際服務</span><span class="tag warn">不是獨立量化實驗</span></article>
    <article class="card wide"><h3>啟動方式</h3><div class="command"><span id="cmd">python3 scripts/run_web_demo.py</span><button class="copy" onclick="copyText('cmd')">複製</button></div><div class="command"><span id="url">http://127.0.0.1:8765</span><button class="copy" onclick="copyText('url')">複製</button></div><ol><li>切換冷氣、窗戶與照明，觀察 3-D 溫度／濕度／照度場。</li><li>切換 base 與 hybrid estimator，說明 residual 是修正層，不取代物理主模型。</li><li>在 point sample 查詢指定座標，展示稀疏感測如何支援空間查詢。</li><li>輸入三因子目標並查看 recommendation ranking；同時說明 E8 仍為 {html.escape(str(e8['evidence_status']))}。</li><li>開啟 public comparison，說明 RNN 與其他模型的同資料負向結果。</li></ol></article>
  </div></section>
  <section id="limits"><h2>教授討論時應明示的邊界</h2><div class="grid">
    <article class="card"><h3>Kalman 證據</h3><p>固定種子、受控 injected noise、SML2010 current-time filtering；不是實體感測器測試，也不是預測或 3-D 場驗證。</p></article><article class="card"><h3>應用範圍</h3><p>室內受控／估測狀態限 20–30°C。封閉植物生長環境只是候選，仍缺 PPFD/PAR、CO₂、基質水分、氣流與生物 endpoint。</p></article><article class="card"><h3>推薦控制</h3><p>目前展示的是模型反事實排序。真實 before/after trial 為 0，不能宣稱因果改善。</p></article><article class="card"><h3>Demo 定位</h3><p>介面證明系統可操作、可查詢；論文數值仍以 machine-readable experiment evidence 為準。</p></article>
  </div></section>
</main>
<footer>Generated {html.escape(generated_at)} from canonical repository evidence · 3-D RNN {html.escape(str(rnn_3d['created_at']))} · Temporal RNN {html.escape(str(rnn['created_at']))} · Kalman {html.escape(str(kalman['created_at']))}</footer>
<script>function go(id) {{ document.getElementById(id).scrollIntoView({{behavior:'smooth'}}); }} async function copyText(id) {{ const text=document.getElementById(id).textContent; try {{ await navigator.clipboard.writeText(text); }} catch (_) {{ window.prompt('請複製：',text); }} }}</script>
</body></html>
"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def _comparison_cards(idw: Mapping[str, float], base: Mapping[str, float], pure_rnn: Mapping[str, float], hybrid: Mapping[str, float]) -> str:
    labels = {"temperature": ("溫度 field MAE", "°C"), "humidity": ("濕度 field MAE", "%RH"), "illuminance": ("照度 field MAE", "lux")}
    colors = {"IDW": "#d24b4b", "Base": "#ee8b2d", "Pure RNN": "#7b61c9", "LOO hybrid": "#1f9d68"}
    cards: List[str] = []
    for metric, (label, unit) in labels.items():
        values = {"IDW": float(idw[metric]), "Base": float(base[metric]), "Pure RNN": float(pure_rnn[metric]), "LOO hybrid": float(hybrid[metric])}
        maximum = max(values.values())
        rows = "".join("<div class='bar-row'>" f"<span>{name}</span><div class='track'><div class='fill' style='width:{max(value/maximum*100,1):.2f}%;background:{colors[name]}'></div></div>" f"<strong>{value:.4f}</strong></div>" for name, value in values.items())
        cards.append(f"<article class='card third'><h3>{label}</h3>{rows}<div class='label'>單位：{unit}；八情境受控模擬</div></article>")
    return "".join(cards)


def _rnn_3d_rows(methods: Mapping[str, Mapping[str, float]]) -> str:
    labels = {
        "idw": "IDW",
        "base_model": "Base model",
        "pure_rnn": "Pure RNN",
        "loo_hybrid": "LOO hybrid",
    }
    rows = []
    for method in ("idw", "base_model", "pure_rnn", "loo_hybrid"):
        values = methods[method]
        rows.append(
            "<tr>"
            f"<td>{labels[method]}</td>"
            f"<td>{float(values['temperature']):.4f} °C</td>"
            f"<td>{float(values['humidity']):.4f} %RH</td>"
            f"<td>{float(values['illuminance']):.4f} lux</td>"
            "</tr>"
        )
    return "".join(rows)


def _bedroom_rows(raw: Mapping[str, float], improved: Mapping[str, float]) -> str:
    labels = {"temperature": ("溫度", "°C"), "humidity": ("相對濕度", "%RH"), "illuminance": ("照度", "lux")}
    rows = []
    for metric, (label, unit) in labels.items():
        before, after = float(raw[metric]), float(improved[metric])
        rows.append(f"<tr><td>{label}</td><td>{before:.4f} {unit}</td><td>{after:.4f} {unit}</td><td>{(before-after)/before*100.0:.2f}%</td></tr>")
    return "".join(rows)


def _rnn_rows(cases: Sequence[Mapping[str, object]]) -> str:
    method_labels = {
        "persistence": "Persistence",
        "sequence_linear_regression": "Sequence LR",
        "physics_structured_readout": "Physics readout",
        "vanilla_rnn": "Vanilla RNN",
    }
    rows = []
    for case in cases:
        metrics = case["metrics"]
        winner = str(case["lowest_mae_method"])
        rows.append(
            "<tr>"
            f"<td>{_target_label(str(case['target']))}</td>"
            f"<td>{int(case['horizon_minutes']):,} 分鐘</td>"
            f"<td>{float(metrics['persistence']['mae']):.6f}</td>"
            f"<td>{float(metrics['sequence_linear_regression']['mae']):.6f}</td>"
            f"<td>{float(metrics['physics_structured_readout']['mae']):.6f}</td>"
            f"<td>{float(metrics['vanilla_rnn']['mae']):.6f}</td>"
            f"<td><span class='tag good'>{method_labels.get(winner, html.escape(winner))}</span></td>"
            "</tr>"
        )
    return "".join(rows)


def _kalman_rows(cases: Sequence[Mapping[str, object]]) -> str:
    rows = []
    for case in cases:
        metrics, winner = case["metrics"], str(case["lowest_mae_method"])
        winner_class = "good" if winner == "linear_kalman_random_walk" else "warn"
        rows.append("<tr>" f"<td>{_target_label(str(case['target']))}</td><td>{_profile_label(str(case['noise_profile']))}</td>" f"<td>{float(metrics['raw_noisy']['mae']):.4f}</td><td>{float(metrics['causal_moving_average_3']['mae']):.4f}</td><td>{float(metrics['linear_kalman_random_walk']['mae']):.4f}</td>" f"<td><span class='tag {winner_class}'>{_method_label(winner)}</span></td></tr>")
    return "".join(rows)


def _representative_kalman_case(cases: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    return next((case for case in cases if case["target"] == "room_humidity" and case["noise_profile"] == "high"), cases[0])


def _trace_svg(preview: Sequence[Mapping[str, object]]) -> str:
    series = {"reference": [float(row["reference"]) for row in preview], "corrupted": [float(row["corrupted"]) for row in preview], "moving_average": [float(row["moving_average"]) for row in preview], "kalman": [float(row["kalman"]) for row in preview]}
    values = [value for row in series.values() for value in row]
    minimum, maximum = min(values), max(values)
    if maximum - minimum < 1e-12:
        maximum = minimum + 1.0
    colors = {"reference": "#172033", "corrupted": "#d24b4b", "moving_average": "#ee8b2d", "kalman": "#2f80ed"}
    polylines = []
    for name, row in series.items():
        points = [f"{42.0+index*(650.0/float(max(len(row)-1,1))):.2f},{18.0+(maximum-value)/(maximum-minimum)*174.0:.2f}" for index, value in enumerate(row)]
        polylines.append(f"<polyline points='{' '.join(points)}' fill='none' stroke='{colors[name]}' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>")
    return "<svg class='trace' viewBox='0 0 720 220' role='img' aria-label='Kalman comparison trace'><line x1='42' y1='18' x2='42' y2='192' stroke='#c9d4e2'/><line x1='42' y1='192' x2='692' y2='192' stroke='#c9d4e2'/>" + f"<text x='6' y='24' font-size='11' fill='#667085'>{maximum:.2f}</text><text x='6' y='194' font-size='11' fill='#667085'>{minimum:.2f}</text>" + "".join(polylines) + "</svg>"


def _target_label(value: str) -> str:
    return {"dining_temperature": "餐區溫度", "room_temperature": "房間溫度", "dining_humidity": "餐區濕度", "room_humidity": "房間濕度"}.get(value, html.escape(value))


def _profile_label(value: str) -> str:
    return {"low": "低", "nominal": "標準", "high": "高"}.get(value, html.escape(value))


def _method_label(value: str) -> str:
    return {"raw_noisy": "未濾波", "causal_moving_average_3": "因果 MA(3)", "linear_kalman_random_walk": "Linear Kalman"}.get(value, html.escape(value))


def _read_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Missing professor-demo evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a self-contained professor-facing two-week evidence demo.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"Wrote {build_professor_demo(args.output)}")


if __name__ == "__main__":
    main()
