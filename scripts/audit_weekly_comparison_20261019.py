"""Recompute declared metrics from every frozen CSV, without simulation."""
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
from verify_enclosure_session_study import recompute_metrics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'openspec/changes/prepare-weekly-comparison-package-20261019/artifacts'
STUDIES=('integrate-enclosure-session-20261012','select-enclosure-structure-20261012')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    baseline=OUT/'historical_hashes.json'
    paths=[p for p in (ROOT/'openspec/changes').glob('*/artifacts/**/*') if p.is_file() and OUT not in p.parents]
    paths += [ROOT/p for p in ('docs/thesis/thesis_draft_zh.md','scripts/build_thesis_docx.py','docs/papers/ieee/paper.tex','docs/papers/ieee/paper.pdf','docs/papers/thesis/thesis_draft_zh.docx','docs/papers/thesis/thesis_draft_zh.pdf','docs/papers/thesis/thesis_presentation_zh.pptx','docs/papers/thesis/thesis_presentation_zh_30min.pptx')]
    if not baseline.exists(): baseline.write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in paths},indent=2)+'\n')
    original=json.loads(baseline.read_text())
    assert all(sha(ROOT/p)==h for p,h in original.items()),'Historical artifact changed'
    receipt={'status':'PASS','scope':'stored CSV arithmetic only; no simulation/fitting/controller execution','historical_files_unchanged':len(original),'studies':{}}
    for study in STUDIES:
        base=ROOT/'openspec/changes'/study/'artifacts'; data=json.loads((base/'result.json').read_text())
        count=0; cells=0
        for run in data['runs']:
            path=base/run['csv']; assert sha(path)==run['sha256'],path
            with path.open() as f: rows=list(csv.DictReader(f))
            actual=recompute_metrics(rows,run['task']);count+=len(rows)
            for key,value in run['metrics'].items():
                assert math.isclose(actual[key],value,rel_tol=1e-9,abs_tol=1e-9),(study,run['csv'],key)
                cells+=1
        for task,splits in data['aggregates'].items():
            for split,methods in splits.items():
                for method,metrics in methods.items():
                    group=[r for r in data['runs'] if (r['task'],r['split'],r['method'])==(task,split,method)]
                    for key,value in metrics.items():
                        assert math.isclose(mean(r['metrics'][key] for r in group),value,rel_tol=1e-9,abs_tol=1e-9)
        assert len(data['runs'])==data['run_count'] and count==data['step_count']
        receipt['studies'][study]={'result_sha256':sha(base/'result.json'),'episodes':len(data['runs']),'rows':count,'metric_cells_checked':cells,'decisions':data['decisions']}
    (OUT/'metric_audit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
