#!/usr/bin/env python3
from __future__ import annotations
import argparse, yaml
from pathlib import Path
from tqdm import tqdm
import pandas as pd

from client_horizons import fetch_ephem
from parquet_utils import write_partitioned_parquet

def load_cfg(cfg_path: str) -> dict:
    return yaml.safe_load(Path(cfg_path).read_text())

def main():
    ap = argparse.ArgumentParser(description="AMJD Harvester (JPL Horizons)")
    ap.add_argument("--config", "-c", default="config/epochs.yaml", help="Ścieżka do pliku YAML z epokami")
    ap.add_argument("--out", "-o", default="parquet", help="Katalog wyjściowy na Parquet")
    ap.add_argument("--targets", "-t", default=None, help="Lista celów CSV (np. 'Sun,Moon,Venus')")
    ap.add_argument("--site", default=None, help="Kod Horizons (np. 500)")
    ap.add_argument("--step", default=None, help="Krok (np. 1h, 1d)")
    ap.add_argument("--chunk-days", type=int, default=None, help="Długość jednego zapytania do API (dni)")
    args = ap.parse_args()

    cfg = load_cfg(args.config)
    site = args.site or cfg.get("site","500")
    step = args.step or cfg.get("step","1h")
    chunk_days = args.chunk_days or int(cfg.get("chunk_days", 30))
    targets = (args.targets.split(",") if args.targets else cfg.get("targets", ["Sun","Moon"]))

    epochs = cfg["epochs"]
    out_dir = args.out

    for ep in epochs:
        name = ep["name"]
        jd0 = float(ep["jd_start"]); jd1 = float(ep["jd_end"])
        print(f"\n=== EPOKA: {name} | JD: {jd0} → {jd1} | step={step} | site={site} ===")
        for target in tqdm(targets, desc=f"{name}"):
            df = fetch_ephem(target=target, start_jd=jd0, stop_jd=jd1, step=step, site=site, chunk_days=chunk_days)
            if df.empty:
                print(f"[WARN] Brak danych dla {target} w {name}")
                continue
            df["epoch_name"] = name
            df["quality"] = ep.get("status", "PASS")
            write_partitioned_parquet(df, out_dir)

    print("\nOK. Dane zapisane w partycjach Parquet. Uruchom QA: `python qa_report.py --parquet parquet --out reports`")

if __name__ == "__main__":
    main()