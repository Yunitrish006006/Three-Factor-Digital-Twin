"""Publish byte-identical derived result JSON for the portable paper graph."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=['sml2010_hybrid_twin_comparison','cu_bems_hybrid_twin_comparison','rnn_sml2010_comparison','gru_lstm_sml2010_comparison','oh2024_inspired_sml2010_comparison','next_day_temperature_improvement']
AAU=['aau_spatial_baseline','aau_local_idw_confirmation','aau_role_conditioned_confirmation','aau_hierarchical_development','aau_tail_safe_development','aau_commissioning_development','aau_commissioning_confirmation_e11f']
def main():
    files=[f'outputs/data/public_benchmarks/{n}.json' for n in PUBLIC]+[f'outputs/data/enclosure/{n}.json' for n in AAU]+['outputs/data/thesis_result_verification_report.json']
    mapping={}
    for original in files:
        source=ROOT/original
        if not source.exists():raise FileNotFoundError(source)
        json.loads(source.read_text())
        relative='docs/research/published_results/'+original.removeprefix('outputs/data/')
        dest=ROOT/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        mapping[original]=dict(path=relative,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size)
    (ROOT/'docs/research/published_graph_evidence.json').write_text(json.dumps(dict(schemaVersion=1,scope='Derived result snapshots only; no raw datasets or FMUs',files=mapping),indent=2)+'\n')
    print(len(mapping),'result snapshots;',sum(r['bytes'] for r in mapping.values()),'bytes')
if __name__=='__main__':main()
