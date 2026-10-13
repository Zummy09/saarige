"""Data-quality checks for a GTFS feed.

YOU write the check functions. Each one:
  - takes a Feed (plus options),
  - returns a CheckResult: how many rows are bad + up to 5 example rows,
  - never raises just because data is bad. Bad data is the expected input.

Run the tests:  uv run pytest tests/test_quality.py -v
They fail now. Make them pass one at a time, top to bottom.

Polars cheat-sheet for this file:
  df.filter(pl.col("a") > pl.col("b"))                  keep rows matching a condition
  df.join(other, on="stop_id", how="anti")              rows in df with NO match in other
  df.join(other, on="stop_id", how="semi")              rows in df WITH a match (no extra cols)
  df.sort(["trip_id", "stop_sequence"])
  pl.col("x").shift(1).over("trip_id")                  previous row's x, within each trip
  df.group_by("k").agg(pl.col("v").unique())            collect values per key
  df.height                                             number of rows
  df.head(5).to_dicts()                                 examples as list[dict]
"""

import math
from dataclasses import dataclass, field
from datetime import date

import polars as pl

from saarige.gtfs.loader import Feed

MAX_EXAMPLES = 5


@dataclass
class CheckResult:
    name: str
    count: int
    examples: list[dict] = field(default_factory=list)
    note: str = ""

    @property
    def ok(self) -> bool:
        return self.count == 0


def _result(name: str, bad: pl.DataFrame, note: str = "") -> CheckResult:
    """Helper: build a CheckResult from a DataFrame of bad rows."""
    return CheckResult(name, bad.height, bad.head(MAX_EXAMPLES).to_dicts(), note)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres. Given to you; not the point of this exercise."""
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------------------------------------------------------- 1. orphans
def check_orphan_stop_refs(feed: Feed) -> CheckResult:
    """Rows in stop_times whose stop_id does not exist in stops.

    TODO: one anti join. That's it.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- 2. unused
def check_unused_stops(feed: Feed) -> CheckResult:
    """Stops that no stop_times row ever visits.

    TODO: the mirror image of check 1.
    Hint: which DataFrame goes on the left this time?
    """
    raise NotImplementedError


# ---------------------------------------------------------------- 3. times
def check_impossible_times(feed: Feed) -> CheckResult:
    """Two kinds of bad row in stop_times:
      (a) arrival_time_s > departure_time_s on the same row (leaves before it arrives)
      (b) arrival_time_s < previous stop's departure_time_s in the same trip (time goes backwards)

    TODO:
      - sort by trip_id, stop_sequence  (NEVER trust file order)
      - add prev_dep = departure_time_s shifted by 1, within each trip_id
      - filter rows matching (a) OR (b)
    Think: what is prev_dep for the first stop of a trip? Does your filter handle it?
    """
    raise NotImplementedError


# ---------------------------------------------------------------- 4. duplicates
def check_duplicate_stops(feed: Feed, max_dist_m: float = 50) -> CheckResult:
    """Likely-duplicate stops: same stop_name, within max_dist_m,
    AND served by the same (route_id, direction_id) pairs.

    Opposite-direction pairs (like 21629 / 21630 Nagarabhavi) are NOT duplicates.

    TODO:
      1. For each stop_id, build its set of "route_id:direction_id" strings
         (stop_times -> trips join, then group_by stop_id).
      2. Self-join stops on stop_name; keep pairs where a.stop_id < b.stop_id
         (why "<" and not "!="? think about it).
      3. Keep pairs within max_dist_m (haversine_m; map_elements or a vectorised
         formula are both fine for ~10k stops).
      4. Keep pairs whose served sets overlap.
    Return one row per pair, with both stop_ids and the distance.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- 5. fares
def check_routes_without_fares(feed: Feed) -> CheckResult:
    """Routes that no fare rule can price.

    Careful: in fare_rules, an EMPTY route_id means "applies to all routes".
    BMTC uses zone-based rules (origin_id / destination_id), with route_id empty.

    TODO:
      - if the feed has no fare_rules at all -> every route is unpriced
      - if any rule has an empty/null route_id -> treat all routes as priceable
        BUT set `note` to say pricing is zone-based and not verified per route
      - otherwise anti-join routes against fare_rules on route_id
    """
    raise NotImplementedError


# ---------------------------------------------------------------- 6. calendar
def check_calendar(feed: Feed, today: date) -> CheckResult:
    """Problems with service dates:
      - `today` is outside every service's start_date..end_date  (feed expired / not started)
      - feed has calendar.txt but no calendar_dates.txt  (no holiday exceptions)
      - every service runs all 7 days  (no weekday/weekend difference)

    Return count = number of problems found (0..3), one example dict per problem,
    e.g. {"problem": "no_calendar_dates"}.

    Hint: GTFS dates are strings "YYYYMMDD". Compare `today.strftime("%Y%m%d")`
    as a string; that works because the format sorts correctly.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- runner
def run_all(feed: Feed, today: date) -> list[CheckResult]:
    return [
        check_orphan_stop_refs(feed),
        check_unused_stops(feed),
        check_impossible_times(feed),
        check_duplicate_stops(feed),
        check_routes_without_fares(feed),
        check_calendar(feed, today),
    ]
