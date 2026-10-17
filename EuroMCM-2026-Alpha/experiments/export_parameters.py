"""Export provenance records without manually editing the generated table."""
from pathlib import Path
import pandas as pd
from alpha.parameters import HISTORICAL_RECORDS, RSI_RECORDS, records_to_rows


def main():
    rows = []
    for domain, records in [("historical", HISTORICAL_RECORDS), ("rsi", RSI_RECORDS)]:
        rows.extend(dict(domain=domain, **row) for row in records_to_rows(records.values()))
    root = Path(__file__).resolve().parents[1]
    pd.DataFrame(rows).to_csv(root / "results/tables/parameter_table.csv", index=False)


if __name__ == "__main__":
    main()
