"""Tests for data-quality checks. Each test plants one known problem in a tiny fake feed."""

from datetime import date

import polars as pl

from saarige.gtfs.loader import Feed, _prepare
from saarige.gtfs.quality import (
    check_calendar,
    check_duplicate_stops,
    check_impossible_times,
    check_orphan_stop_refs,
    check_routes_without_fares,
    check_unused_stops,
)


def make_feed(**tables: list[dict]) -> Feed:
    """Build a Feed from rows of strings, prepared exactly like the real loader."""
    return Feed(
        name="test",
        tables={
            name: _prepare(name, pl.DataFrame(rows, schema={k: pl.String for k in rows[0]}))
            for name, rows in tables.items()
        },
    )


def st(trip, seq, stop, arr, dep=None):
    return {"trip_id": trip, "stop_sequence": str(seq), "stop_id": stop,
            "arrival_time": arr, "departure_time": dep or arr}


def stop(sid, name, lat, lon):
    return {"stop_id": sid, "stop_name": name, "stop_lat": str(lat), "stop_lon": str(lon)}


STOPS = [stop("A", "Alpha", 12.97, 77.59), stop("B", "Beta", 12.98, 77.60),
         stop("C", "Gamma", 12.99, 77.61)]
TRIPS = [{"trip_id": "T1", "route_id": "R1", "direction_id": "0", "service_id": "1"}]


# 1 ------------------------------------------------------------------
def test_orphan_stop_refs():
    feed = make_feed(stops=STOPS, trips=TRIPS,
                     stop_times=[st("T1", 1, "A", "08:00:00"), st("T1", 2, "GHOST", "08:05:00")])
    r = check_orphan_stop_refs(feed)
    assert r.count == 1
    assert r.examples[0]["stop_id"] == "GHOST"


# 2 ------------------------------------------------------------------
def test_unused_stops():
    feed = make_feed(stops=STOPS, trips=TRIPS,
                     stop_times=[st("T1", 1, "A", "08:00:00"), st("T1", 2, "B", "08:05:00")])
    r = check_unused_stops(feed)
    assert r.count == 1
    assert r.examples[0]["stop_id"] == "C"


# 3 ------------------------------------------------------------------
def test_impossible_times_catches_both_kinds():
    feed = make_feed(stops=STOPS, trips=TRIPS, stop_times=[
        st("T1", 1, "A", "08:00:00"),
        st("T1", 2, "B", "08:10:00", "08:05:00"),   # (a) departs before it arrives
        st("T1", 3, "C", "07:50:00"),               # (b) goes back in time
    ])
    assert check_impossible_times(feed).count == 2


def test_impossible_times_ignores_file_order_and_midnight():
    feed = make_feed(stops=STOPS, trips=TRIPS, stop_times=[
        st("T1", 2, "B", "24:10:00"),               # listed first, but it's stop 2
        st("T1", 1, "A", "23:50:00"),
    ])
    assert check_impossible_times(feed).count == 0


# 4 ------------------------------------------------------------------
def test_duplicate_stops_same_direction_is_duplicate():
    stops = [stop("S1", "Hebbal", 12.9900, 77.5900), stop("S2", "Hebbal", 12.9901, 77.5901)]
    feed = make_feed(stops=stops, trips=TRIPS,
                     stop_times=[st("T1", 1, "S1", "08:00:00"), st("T1", 2, "S2", "08:01:00")])
    r = check_duplicate_stops(feed)
    assert r.count == 1


def test_duplicate_stops_opposite_direction_is_not_duplicate():
    stops = [stop("21629", "Nagarabhavi", 12.96018, 77.51398),
             stop("21630", "Nagarabhavi", 12.96076, 77.51351)]
    trips = [{"trip_id": "UP", "route_id": "R1", "direction_id": "0", "service_id": "1"},
             {"trip_id": "DN", "route_id": "R1", "direction_id": "1", "service_id": "1"}]
    feed = make_feed(stops=stops, trips=trips,
                     stop_times=[st("UP", 1, "21629", "08:00:00"), st("DN", 1, "21630", "09:00:00")])
    assert check_duplicate_stops(feed, max_dist_m=100).count == 0


# 5 ------------------------------------------------------------------
ROUTES = [{"route_id": "R1"}, {"route_id": "R2"}]
FARE_ATTR = [{"fare_id": "F1", "price": "10"}]


def test_routes_without_fares_route_based():
    feed = make_feed(routes=ROUTES, fare_attributes=FARE_ATTR,
                     fare_rules=[{"fare_id": "F1", "route_id": "R1", "origin_id": "", "destination_id": ""}])
    r = check_routes_without_fares(feed)
    assert r.count == 1
    assert r.examples[0]["route_id"] == "R2"


def test_routes_without_fares_zone_based_adds_note():
    feed = make_feed(routes=ROUTES, fare_attributes=FARE_ATTR,
                     fare_rules=[{"fare_id": "F1", "route_id": "", "origin_id": "Z1", "destination_id": "Z2"}])
    r = check_routes_without_fares(feed)
    assert r.count == 0
    assert "zone" in r.note.lower()


def test_routes_without_fares_no_fare_file():
    feed = make_feed(routes=ROUTES)
    assert check_routes_without_fares(feed).count == 2


# 6 ------------------------------------------------------------------
CAL_ALL_DAYS = [{"service_id": "1", "monday": "1", "tuesday": "1", "wednesday": "1",
                 "thursday": "1", "friday": "1", "saturday": "1", "sunday": "1",
                 "start_date": "20260907", "end_date": "20270907"}]


def test_calendar_flags_bmtc_style_feed():
    feed = make_feed(calendar=CAL_ALL_DAYS)
    r = check_calendar(feed, today=date(2026, 10, 12))
    problems = {e["problem"] for e in r.examples}
    assert problems == {"no_calendar_dates", "all_services_every_day"}


def test_calendar_flags_expired_feed():
    feed = make_feed(calendar=CAL_ALL_DAYS)
    r = check_calendar(feed, today=date(2027, 12, 1))
    assert "outside_service_dates" in {e["problem"] for e in r.examples}
