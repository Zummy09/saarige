import polars as pl

from saarige.gtfs.loader import gtfs_time_to_seconds


def test_time_to_seconds_handles_past_midnight_and_garbage():
    df = pl.DataFrame({"t": ["08:05:00", "24:10:00", "25:35:00", "", None, " 7:00:00"]})
    out = df.select(gtfs_time_to_seconds("t"))["t_s"].to_list()
    assert out == [29100, 87000, 92100, None, None, 25200]
