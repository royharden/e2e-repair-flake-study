"""SQLite business state and atomic effects. No process-global business state."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid


def metadata() -> dict:
    return {"schema_version": 1, "origin": "AUTHORED", "mode": "fixture", "runtime_verified": False}


def seed_slots() -> tuple:
    return (("harbour-a", "Harbour A", 8, 2500), ("harbour-b", "Harbour B", 12, 1800))


def quote(unit_cents: int, party: int) -> dict:
    subtotal = unit_cents * party
    discount = subtotal // 10 if party >= 4 else 0
    return {"subtotal_cents": subtotal, "discount_cents": discount,
            "total_cents": subtotal - discount}


class Store:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connection(self, *, read_only: bool = False):
        location = self.path.resolve().as_uri() + "?mode=ro" if read_only else self.path
        db = sqlite3.connect(location, timeout=5, uri=read_only)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS slots (
                  id TEXT PRIMARY KEY, label TEXT NOT NULL,
                  capacity INTEGER NOT NULL CHECK(capacity>0),
                  unit_cents INTEGER NOT NULL CHECK(unit_cents>0));
                CREATE TABLE IF NOT EXISTS bookings (
                  position INTEGER PRIMARY KEY AUTOINCREMENT,
                  id TEXT UNIQUE NOT NULL, slot_id TEXT NOT NULL REFERENCES slots(id),
                  label TEXT NOT NULL, party INTEGER NOT NULL CHECK(party BETWEEN 1 AND 8),
                  subtotal_cents INTEGER NOT NULL, discount_cents INTEGER NOT NULL,
                  total_cents INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('active','cancelled')));
                CREATE TABLE IF NOT EXISTS events (
                  seq INTEGER PRIMARY KEY, kind TEXT NOT NULL, booking_id TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
            db.execute("BEGIN IMMEDIATE")
            db.executemany("INSERT OR IGNORE INTO slots VALUES (?,?,?,?)", seed_slots())
            db.execute("INSERT OR IGNORE INTO meta VALUES ('epoch',?)", (uuid.uuid4().hex,))

    def slots(self) -> list[dict]:
        with self.connection(read_only=True) as db:
            rows = db.execute("""SELECT s.*, s.capacity-COALESCE(SUM(CASE WHEN b.status='active'
                THEN b.party ELSE 0 END),0) AS remaining FROM slots s
                LEFT JOIN bookings b ON b.slot_id=s.id GROUP BY s.id ORDER BY s.id""")
            return [dict(row) for row in rows]

    def bookings(self) -> list[dict]:
        with self.connection(read_only=True) as db:
            return [dict(row) for row in db.execute("""SELECT b.*,s.label AS slot_label FROM bookings b
                JOIN slots s ON s.id=b.slot_id ORDER BY b.position LIMIT 1000""")]

    def booking(self, booking_id: str) -> dict:
        with self.connection(read_only=True) as db:
            row = db.execute("""SELECT b.*,s.label AS slot_label FROM bookings b
                JOIN slots s ON s.id=b.slot_id WHERE b.id=?""", (booking_id,)).fetchone()
            if row is None:
                raise ValueError("Unknown booking")
            return dict(row)

    def create(self, slot_id: str, label: str, party_text: str) -> str:
        label = label.strip()
        if re.fullmatch(r"[A-Za-z0-9 -]{1,40}", label) is None:
            raise ValueError("Use a nonpersonal demo label: 1–40 letters, digits, spaces or hyphens")
        if re.fullmatch(r"[1-8]", party_text) is None:
            raise ValueError("Party must be an integer from 1 to 8")
        party = int(party_text)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            slot = db.execute("SELECT * FROM slots WHERE id=?", (slot_id,)).fetchone()
            if slot is None:
                raise ValueError("Unknown slot")
            if db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] >= 1000:
                raise ValueError("Demo booking limit reached; owner-controlled reset required")
            occupied = db.execute("SELECT COALESCE(SUM(party),0) FROM bookings WHERE slot_id=? AND status='active'",
                                  (slot_id,)).fetchone()[0]
            if party > slot["capacity"] - occupied:
                raise ValueError("Not enough seats remaining")
            amounts = quote(slot["unit_cents"], party)
            booking_id = uuid.uuid4().hex
            db.execute("""INSERT INTO bookings(id,slot_id,label,party,subtotal_cents,discount_cents,total_cents,status)
                VALUES (?,?,?,?,?,?,?,'active')""", (booking_id, slot_id, label, party,
                amounts["subtotal_cents"], amounts["discount_cents"], amounts["total_cents"]))
            db.execute("INSERT INTO events(kind,booking_id) VALUES ('created',?)", (booking_id,))
            return booking_id

    def cancel(self, booking_id: str) -> None:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM bookings WHERE id=?", (booking_id,)).fetchone()
            if row is None:
                raise ValueError("Unknown booking")
            if row["status"] == "active":
                db.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
                db.execute("INSERT INTO events(kind,booking_id) VALUES ('cancelled',?)", (booking_id,))

    def reset(self) -> dict:
        """Exec-only destructive demo reset; never called by an HTTP handler."""
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM events")
            db.execute("DELETE FROM bookings")
            db.execute("DELETE FROM sqlite_sequence WHERE name='bookings'")
            db.execute("DELETE FROM slots")
            db.executemany("INSERT INTO slots VALUES (?,?,?,?)", seed_slots())
            epoch = uuid.uuid4().hex
            db.execute("UPDATE meta SET value=? WHERE name='epoch'", (epoch,))
            return {**metadata(), "reset": "authored_demo_state", "epoch": epoch}

    def state_hash(self) -> dict:
        with self.connection(read_only=True) as db:
            db.execute("BEGIN")
            state = {"slots": [dict(r) for r in db.execute("SELECT * FROM slots ORDER BY id")],
                     "bookings": [dict(r) for r in db.execute("SELECT * FROM bookings ORDER BY position")]}
            canonical = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
            return {**metadata(), "state_sha256": hashlib.sha256(canonical).hexdigest(),
                    "scope": "logical slots and bookings only; excludes epoch/effects"}

    def observe(self, epoch: str, since: int) -> dict:
        with self.connection(read_only=True) as db:
            db.execute("BEGIN")
            actual = db.execute("SELECT value FROM meta WHERE name='epoch'").fetchone()[0]
            latest = db.execute("SELECT COALESCE(MAX(seq),0) FROM events").fetchone()[0]
            if epoch != actual or type(since) is not int or not 0 <= since <= latest:
                raise ValueError("Observer epoch or cursor mismatch")
            events = [dict(r) for r in db.execute("SELECT * FROM events WHERE seq>? ORDER BY seq", (since,))]
            return {**metadata(), "epoch": actual, "cursor": latest, "events": events}

    def observation_start(self) -> dict:
        with self.connection(read_only=True) as db:
            db.execute("BEGIN")
            epoch = db.execute("SELECT value FROM meta WHERE name='epoch'").fetchone()[0]
            cursor = db.execute("SELECT COALESCE(MAX(seq),0) FROM events").fetchone()[0]
            return {**metadata(), "epoch": epoch, "cursor": cursor}
