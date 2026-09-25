"""iNaturalist API client with an on-disk cache.

Every response is saved under data/raw/inat/ keyed by the request, so re-running a
script repeats no network calls and the raw pulls behind every number can be inspected.
The API asks for about one request per second; `get` sleeps to respect that.
"""

import hashlib
import json
import threading
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from . import PLACE_TEXAS, SEASON, TAXON_BLUEBONNET, UPLOAD_CUTOFF

API = "https://api.inaturalist.org/v1"
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "inat"
HEADERS = {"User-Agent": "bluebonnet-bloom-study (github.com/kvenanzi/bluebonnet)"}
_last = [0.0]
_lock = threading.Lock()   # requests start at most once per second, even from several threads


def get(path: str, params: dict, refresh: bool = False) -> dict:
    key = hashlib.sha1(json.dumps([path, sorted(params.items())], default=str).encode()).hexdigest()[:20]
    # Observation pages keep their original (short) names so an existing cache stays valid.
    stem = path.strip("/").split("/")[0]
    file = CACHE / f"{stem}-{key}.json"
    if file.exists() and not refresh:
        return json.loads(file.read_text())
    for attempt in range(6):
        with _lock:
            wait = 1.05 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        r = requests.get(f"{API}/{path.strip('/')}", params=params, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            data = r.json()
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps({"params": params, "path": path,
                                        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                        "data": data}))
            return {"data": data}
        time.sleep(5 * 2 ** attempt)
    r.raise_for_status()
    raise RuntimeError(f"iNaturalist request failed: {path} {params}")


def season_params(year: int) -> dict:
    """The filters of preregistration §2: verifiable, observed in the season window,
    uploaded by the cut-off of the same year."""
    return {"verifiable": "true", "d1": f"{year}-{SEASON[0]}", "d2": f"{year}-{SEASON[1]}",
            "created_d2": f"{year}-{UPLOAD_CUTOFF}"}


def bluebonnet_observations(year: int, refresh: bool = False) -> pd.DataFrame:
    """Every bluebonnet observation in Texas for one spring (paged by id)."""
    rows, id_above = [], 0
    while True:
        params = {"taxon_id": TAXON_BLUEBONNET, "place_id": PLACE_TEXAS, **season_params(year),
                  "order_by": "id", "order": "asc", "per_page": 200, "id_above": id_above}
        page = get("observations", params, refresh)["data"]["results"]
        for o in page:
            loc = (o.get("location") or ",").split(",")
            rows.append({
                "id": o["id"], "observed_on": o.get("observed_on"), "created_at": o.get("created_at"),
                "quality_grade": o.get("quality_grade"), "obscured": o.get("obscured"),
                "geoprivacy": o.get("geoprivacy"), "taxon_id": (o.get("taxon") or {}).get("id"),
                "user_id": (o.get("user") or {}).get("id"), "place_ids": o.get("place_ids") or [],
                "lat": float(loc[0]) if loc[0] else None, "lon": float(loc[1]) if loc[1] else None,
            })
        if len(page) < 200:
            break
        id_above = page[-1]["id"]
    df = pd.DataFrame(rows)
    df["spring"] = year
    return df


def places(ids: list[int]) -> pd.DataFrame:
    out = []
    ids = sorted(set(ids))
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        res = get(f"places/{','.join(map(str, chunk))}", {})["data"]["results"]
        out += [{"place_id": p["id"], "name": p["name"], "display_name": p["display_name"],
                 "place_type": p.get("place_type"), "admin_level": p.get("admin_level"),
                 "ancestors": p.get("ancestor_place_ids") or []} for p in res]
    return pd.DataFrame(out)


def texas_counties(place_ids: list[int]) -> pd.DataFrame:
    """The Texas county places (iNat place_type 9) among the given ids."""
    p = places(place_ids)
    p = p[(p.place_type == 9) & p.ancestors.apply(lambda a: PLACE_TEXAS in a)]
    return p[["place_id", "name", "display_name"]].sort_values("name").reset_index(drop=True)


def daily_histogram(place_id: int, year: int, taxon_id: int, extra: dict | None = None,
                    refresh: bool = False) -> pd.Series:
    """Observations per observed day for one place and spring, same filters as the numerator."""
    params = {"place_id": place_id, "taxon_id": taxon_id, **season_params(year),
              "date_field": "observed", "interval": "day", **(extra or {})}
    res = get("observations/histogram", params, refresh)["data"]["results"]["day"]
    s = pd.Series(res, dtype="int64")
    s.index = pd.to_datetime(s.index)
    full = pd.date_range(f"{year}-{SEASON[0]}", f"{year}-{SEASON[1]}", freq="D")
    return s.reindex(full, fill_value=0)


def today() -> str:
    return date.today().isoformat()
