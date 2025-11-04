# client_horizons.py
from __future__ import annotations
from astroquery.jplhorizons import Horizons
from astropy.time import Time
import pandas as pd
from pathlib import Path
from tenacity import retry, wait_exponential, stop_after_attempt
import hashlib

CACHE_DIR = Path("cache/horizons")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_key(target: str, site: str, start_jd: float, stop_jd: float, step: str) -> str:
    s = f"{target}|{site}|{start_jd}|{stop_jd}|{step}"
    return hashlib.sha256(s.encode()).hexdigest()

def _read_cache(key: str) -> pd.DataFrame | None:
    p = CACHE_DIR / f"{key}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    return None

def _write_cache(key: str, df: pd.DataFrame) -> None:
    p = CACHE_DIR / f"{key}.parquet"
    df.to_parquet(p, compression="zstd", index=False)

@retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
def _fetch_chunk(target: str, site: str, t0_iso: str, t1_iso: str, step: str) -> pd.DataFrame:
    # Konwersja na format Horizons (BC dla dat przed naszą erą)
    def _to_horizons_time(iso_str: str) -> str:
        if iso_str.startswith('-'):
            # Format: -YYYY-MM-DD -> YYYY BC MM DD
            parts = iso_str[1:].split('-')  # usuń minus, split
            year = int(parts[0])
            month = parts[1]
            day = parts[2][:2]  # bez czasu
            return f"{year} BC {month} {day}"
        else:
            return iso_str

    t0_h = _to_horizons_time(t0_iso)
    t1_h = _to_horizons_time(t1_iso)

    # id_type: auto — Horizons sam rozpozna (można też wymusić 'majorbody' / 'smallbody')
    obj = Horizons(id=target, location=site, epochs={'start': t0_h, 'stop': t1_h, 'step': step})
    tab = obj.ephemerides()
    df = tab.to_pandas()
    return df

def fetch_ephem(target: str, start_jd: float, stop_jd: float, step: str = "1h",
                site: str = "500", chunk_days: int = 30) -> pd.DataFrame:
    start = float(start_jd); stop = float(stop_jd)
    out = []
    cur = start
    while cur < stop:
        end = min(cur + chunk_days, stop)
        key = _cache_key(target, site, cur, end, step)
        cached = _read_cache(key)
        if cached is not None:
            out.append(cached)
        else:
            t0 = Time(cur, format="jd", scale="utc").isot
            t1 = Time(end, format="jd", scale="utc").isot
            df = _fetch_chunk(target, site, t0, t1, step)

            # Normalizacja czasu
            if 'datetime_jd' in df.columns:
                df['jd_utc'] = df['datetime_jd'].astype(float)
            else:
                # best-effort: jeśli brak 'datetime_jd', spróbuj standardowych kolumn
                for cand in ('JD', 'jd', 'JDTDB'):
                    if cand in df.columns:
                        df['jd_utc'] = df[cand].astype(float); break

            tt = Time(df['jd_utc'].values, format='jd', scale='utc').tt
            df['jd_tt'] = tt.jd
            df['delta_t_sec'] = (df['jd_tt'] - df['jd_utc']) * 86400.0
            df['target'] = target
            df['site'] = site

            _write_cache(key, df)
            out.append(df)
        cur = end
    if not out:
        return pd.DataFrame(columns=['jd_utc','jd_tt','delta_t_sec','target','site'])
    return pd.concat(out, ignore_index=True)