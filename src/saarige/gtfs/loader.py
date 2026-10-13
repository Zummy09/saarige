"""Load a GTFS zip into Polars DataFrames.

Design choices:
- Every column is read as a string first (infer_schema=False). IDs like "0123"
  must stay strings; type inference would silently turn them into integers.
- Only columns we know are numeric get cast afterwards.
- GTFS times can exceed 24:00:00 (see Phase 1 Block 1), so we never parse them
  with datetime. Instead we add `<col>_s` columns: seconds since service-day start.
"""

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import polars as pl

NUMERIC_COLUMNS: dict[str, dict[str, pl.DataType]] = {
    "stops": {"stop_lat": pl.Float64, "stop_lon": pl.Float64},
    "stop_times": {"stop_sequence": pl.Int32},
    "trips": {"direction_id": pl.Int8},
    "fare_attributes": {"price": pl.Float64},
}

TIME_COLUMNS: dict[str, list[str]] = {
    "stop_times": ["arrival_time", "departure_time"],
}


def gtfs_time_to_seconds(col: str) -> pl.Expr:
    """'25:35:00' -> 92100. Empty or malformed values become null."""
    parts = pl.col(col).str.strip_chars().str.split(":")
    return (
        parts.list.get(0, null_on_oob=True).cast(pl.Int32, strict=False) * 3600
        + parts.list.get(1, null_on_oob=True).cast(pl.Int32, strict=False) * 60
        + parts.list.get(2, null_on_oob=True).cast(pl.Int32, strict=False)
    ).alias(f"{col}_s")


@dataclass
class Feed:
    name: str
    tables: dict[str, pl.DataFrame] = field(default_factory=dict)

    def __getitem__(self, table: str) -> pl.DataFrame:
        return self.tables[table]

    def has(self, table: str) -> bool:
        return table in self.tables


def _prepare(table: str, df: pl.DataFrame) -> pl.DataFrame:
    casts = [
        pl.col(c).cast(t, strict=False)
        for c, t in NUMERIC_COLUMNS.get(table, {}).items()
        if c in df.columns
    ]
    times = [gtfs_time_to_seconds(c) for c in TIME_COLUMNS.get(table, []) if c in df.columns]
    return df.with_columns(casts + times) if casts or times else df


def load_feed(zip_path: Path, name: str | None = None) -> Feed:
    feed = Feed(name=name or zip_path.stem)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            if not member.endswith(".txt"):
                continue
            table = Path(member).stem
            df = pl.read_csv(zf.read(member), infer_schema=False)
            feed.tables[table] = _prepare(table, df)
    return feed
