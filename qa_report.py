#!/usr/bin/env python3
import argparse, duckdb, os
from pathlib import Path

HTML = """<!doctype html><meta charset="utf-8">
<title>AMJD Harvest QA</title>
<style>body{font-family:system-ui;margin:24px} table{border-collapse:collapse}
td,th{border:1px solid #ddd;padding:6px 10px} h1{margin:0 0 16px}</style>
<h1>AMJD Harvest QA</h1>
<p>Źródło: {src}</p>
<h2>Liczności (per target)</h2>
{tbl_target}
<h2>Zakres czasowy (UTC z jd_utc)</h2>
{tbl_range}
<h2>ΔT (TT-UTC) — statystyki</h2>
{tbl_dt}
"""

def df_to_html(cur, q):
    return cur.execute(q).df().to_html(index=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True, help="Katalog z Parquet (partycje year=/month=)")
    ap.add_argument("--out", default="reports", help="Katalog wyjściowy raportów")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    src = args.parquet.rstrip("/")

    con = duckdb.connect()
    con.execute(f"CREATE VIEW ephem AS SELECT * FROM read_parquet('{src}/**/*.parquet');")

    tbl_target = df_to_html(con, "SELECT target, COUNT(*) AS rows FROM ephem GROUP BY 1 ORDER BY 2 DESC;")
    tbl_range  = df_to_html(con, """
        SELECT MIN(jd_utc) AS jd_min, MAX(jd_utc) AS jd_max,
               MIN(to_timestamp((jd_utc-2440587.5)*86400)) AS utc_min,
               MAX(to_timestamp((jd_utc-2440587.5)*86400)) AS utc_max
        FROM ephem;
    """)
    tbl_dt     = df_to_html(con, """
        SELECT target,
               AVG(delta_t_sec) AS dt_avg_s,
               STDDEV(delta_t_sec) AS dt_std_s,
               MIN(delta_t_sec) AS dt_min_s,
               MAX(delta_t_sec) AS dt_max_s,
               COUNT(*) AS rows
        FROM ephem
        GROUP BY 1 ORDER BY 6 DESC;
    """)

    html = HTML.format(src=src, tbl_target=tbl_target, tbl_range=tbl_range, tbl_dt=tbl_dt)
    (out/"HARVEST_QA.html").write_text(html, encoding="utf-8")

    # CSV-y pomocnicze
    con.execute("COPY (SELECT * FROM ephem LIMIT 200) TO '" + str(out/'preview_200.csv') + "' (HEADER, DELIMITER ',');")
    con.execute("COPY (SELECT target, COUNT(*) AS rows FROM ephem GROUP BY 1 ORDER BY 2 DESC) TO '" + str(out/'by_target.csv') + "' (HEADER, DELIMITER ',');")

    print(f"Raport: {out/'HARVEST_QA.html'}")

if __name__ == "__main__":
    main()