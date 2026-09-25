"""NOAA weather: nClimDiv county monthly values, GHCN-Daily station temperatures, and
the Oceanic Niño Index. Downloads are cached under data/raw/noaa/.

nClimDiv identifies a county by NCDC state code + county FIPS, and NCDC numbers Texas
41 (not FIPS 48): Travis County (FIPS 48453) is `41453`. Missing months are -9.99 / -99.90.
"""

import gzip
import io
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "noaa"
CLIMDIV = "https://www.ncei.noaa.gov/monitoring-content/data/us/climdiv/monthly/current/"
GHCN = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
GAZ = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip"
NCDC_TEXAS = "41"


def fetch(url: str, name: str | None = None, refresh: bool = False) -> bytes:
    file = CACHE / (name or url.rstrip("/").split("/")[-1])
    if file.exists() and not refresh:
        return file.read_bytes()
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(r.content)
    return r.content


def climdiv_filename(element: str, refresh: bool = False) -> str:
    """The current file name, whose date suffix changes with each monthly release."""
    listing = fetch(CLIMDIV, "climdiv-listing.html", refresh=refresh).decode()
    names = sorted(set(re.findall(rf"climdiv-{element}cy-v[0-9.]+-\d{{8}}", listing)))
    if not names:
        raise RuntimeError(f"no climdiv file for {element}")
    return names[-1]


def climdiv(element: str, refresh: bool = False) -> pd.DataFrame:
    """Texas county monthly values, long format: fips (48xxx), year, month, value.
    element: pcpn (precipitation, inches), tmpc (mean temperature, °F), pdsi."""
    name = climdiv_filename(element, refresh)
    text = fetch(CLIMDIV + name, name, refresh).decode()
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if not parts or not parts[0].startswith(NCDC_TEXAS):
            continue
        code = parts[0]
        fips, year = "48" + code[2:5], int(code[7:11])
        for m, v in enumerate(parts[1:13], start=1):
            v = float(v)
            rows.append((fips, year, m, np.nan if v in (-9.99, -99.9, -99.99) else v))
    df = pd.DataFrame(rows, columns=["fips", "year", "month", "value"])
    df.attrs["source_file"] = name
    return df


def oni(refresh: bool = False) -> pd.DataFrame:
    """CPC Oceanic Niño Index: season (e.g. OND), year, anomaly (°C)."""
    text = fetch(ONI, "oni.ascii.txt", refresh).decode()
    rows = [l.split() for l in text.splitlines()[1:] if l.strip()]
    return pd.DataFrame([(s, int(y), float(a)) for s, y, _, a in rows], columns=["season", "year", "anom"])


def counties_gazetteer(refresh: bool = False) -> pd.DataFrame:
    """Texas counties: fips, name ('Travis'), interior-point latitude/longitude."""
    raw = fetch(GAZ, "gaz_counties.zip", refresh)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        df = pd.read_csv(z.open(z.namelist()[0]), sep="\t", dtype={"GEOID": str})
    df.columns = [c.strip() for c in df.columns]
    df = df[df.USPS == "TX"]
    return pd.DataFrame({"fips": df.GEOID, "name": df.NAME.str.replace(" County", "", regex=False),
                         "lat": df.INTPTLAT, "lon": df.INTPTLONG}).reset_index(drop=True)


def ghcn_stations(refresh: bool = False) -> pd.DataFrame:
    """GHCN-Daily stations with both TMAX and TMIN, with their first and last year."""
    inv = fetch(GHCN + "ghcnd-inventory.txt", refresh=refresh).decode().splitlines()
    rows = [(l[0:11], float(l[12:20]), float(l[21:30]), l[31:35], int(l[36:40]), int(l[41:45])) for l in inv]
    inv = pd.DataFrame(rows, columns=["id", "lat", "lon", "element", "first", "last"])
    inv = inv[inv.element.isin(["TMAX", "TMIN"])]
    g = inv.groupby(["id", "lat", "lon"]).agg(n=("element", "nunique"), first=("first", "max"), last=("last", "min"))
    return g[g.n == 2].drop(columns="n").reset_index()


def station_daily(station: str, refresh: bool = False) -> pd.DataFrame:
    """Daily TMAX/TMIN (°C) for one station; values with a quality flag are dropped."""
    raw = fetch(f"{GHCN}by_station/{station}.csv.gz", f"ghcn/{station}.csv.gz", refresh)
    df = pd.read_csv(io.BytesIO(gzip.decompress(raw)), header=None, dtype={1: str, 5: str},
                     names=["id", "date", "element", "value", "mflag", "qflag", "sflag", "obstime"])
    df = df[df.element.isin(["TMAX", "TMIN"]) & df.qflag.isna()]
    df = df.pivot_table(index="date", columns="element", values="value", aggfunc="first") / 10.0
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))
