# parquet_utils.py
import pandas as pd
from pathlib import Path

def jd_to_utc_timestamp(jd_series: pd.Series) -> pd.Series:
    # Szybka konwersja: Unix epoch w JD to 2440587.5
    return pd.to_datetime((jd_series - 2440587.5) * 86400.0, unit="s", utc=True)

def write_partitioned_parquet(df: pd.DataFrame, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = jd_to_utc_timestamp(df['jd_utc'])
    df = df.copy()
    df['year'] = ts.dt.year
    df['month'] = ts.dt.month
    for (yr, mo), part in df.groupby(['year','month'], dropna=False):
        p = out / f"year={int(yr):04d}" / f"month={int(mo):02d}" / f"ephem_{int(yr):04d}{int(mo):02d}.parquet"
        p.parent.mkdir(parents=True, exist_ok=True)
        part.drop(columns=['year','month'], errors='ignore').to_parquet(p, compression="zstd", index=False)