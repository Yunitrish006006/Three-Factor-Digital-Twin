import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from digital_twin.enclosure.bmc_baseline import evaluate_bmc_paths, write_bmc_summary


DEFAULT_OUTPUT = ROOT / "outputs" / "data" / "enclosure" / "enclosure_bmc_baseline.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the pre-registered E11A equipment-enclosure BMC baseline comparison."
    )
    parser.add_argument("paths", nargs="+", help="BMC InfluxDB-style CSV traces.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Machine-readable JSON output path.")
    args = parser.parse_args()

    summary = evaluate_bmc_paths([Path(value) for value in args.paths])
    output_path = Path(args.output)
    write_bmc_summary(summary, output_path)
    try:
        display_path = output_path.relative_to(ROOT)
    except ValueError:
        display_path = output_path
    print(display_path)
    print(
        "status={status} evaluated_cases={cases} thermal_wins={wins}".format(
            status=summary["summary"]["status"],
            cases=summary["summary"]["evaluated_case_count"],
            wins=summary["summary"]["thermal_balance_wins_vs_persistence"],
        )
    )


if __name__ == "__main__":
    main()
