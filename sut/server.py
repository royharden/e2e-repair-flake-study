"""Loopback-only toy HTTP source. Starting it requires later owner/port authorization."""

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import secrets
import sqlite3
from urllib.parse import parse_qs, urlsplit

from sut.store import Store


def money(cents: int) -> str:
    return f"${cents // 100}.{cents % 100:02d}"


class HarbourServer(HTTPServer):
    def __init__(self, port: int, store: Store):
        self.store = store
        self.form_token = secrets.token_urlsafe(32)  # Ephemeral anti-CSRF value, never persisted.
        super().__init__(("127.0.0.1", port), HarbourHandler)


class HarbourHandler(BaseHTTPRequestHandler):
    server: HarbourServer

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, format: str, *args: object) -> None:
        # No demo label, form token or user-controlled request text in logs.
        return

    def send_body(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def page(self, title: str, body: str, status: int = 200) -> None:
        html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{escape(title)} · Harbour Bookings</title><link rel="stylesheet" href="/static/style.css">
          <script src="/static/app.js" defer></script><script src="/hooks.js" defer></script></head>
          <body><header><p class="eyebrow">AUTHORED DEMO · NOT REAL RESERVATIONS</p>
          <h1 data-oracle-id="app-title">Harbour Bookings</h1>
          <nav><a href="/">Slots</a><a href="/bookings">Bookings</a></nav></header>
          <main><h2>{escape(title)}</h2>{body}</main>
          <footer>Invented demo data only. Source runtime unverified; no payments or accounts.</footer></body></html>"""
        self.send_body(status, html.encode("utf-8"), "text/html; charset=utf-8")

    def form_token(self) -> str:
        return f'<input type="hidden" name="token" value="{escape(self.server.form_token, quote=True)}">'

    def route(self) -> tuple[str, dict[str, str]]:
        if len(self.path) > 512:
            raise ValueError("URL too long")
        url = urlsplit(self.path)
        if url.scheme or url.netloc or url.fragment:
            raise ValueError("App-relative URL required")
        query = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=4)
        if any(len(values) != 1 for values in query.values()):
            raise ValueError("Duplicate query field")
        return url.path, {key: values[0] for key, values in query.items()}

    def do_GET(self) -> None:
        try:
            route, query = self.route()
            assets = {"/static/style.css": ("static/style.css", "text/css; charset=utf-8"),
                      "/static/app.js": ("static/app.js", "text/javascript; charset=utf-8"),
                      "/hooks.js": ("hooks.js", "text/javascript; charset=utf-8")}
            if route in assets and not query:
                name, content_type = assets[route]
                self.send_body(200, (Path(__file__).parent / name).read_bytes(), content_type)
            elif route == "/" and not query:
                cards = []
                for slot in self.server.store.slots():
                    sid = escape(slot["id"], quote=True)
                    cards.append(f'<article><h3 data-oracle-id="slot-title-{sid}">{escape(slot["label"])}</h3>'
                                 f'<p data-oracle-id="slot-price-{sid}">{money(slot["unit_cents"])} per guest</p>'
                                 f'<p>Capacity {slot["capacity"]}; <strong data-oracle-id="remaining-{sid}">{slot["remaining"]}</strong> remaining</p>'
                                 f'<a class="button" href="/book?slot={sid}">Book {escape(slot["label"])}</a></article>')
                self.page("Choose a harbour session", '<p>Parties of 4–8 save 10%. Demo labels only.</p><div class="grid">' + ''.join(cards) + '</div>')
            elif route == "/book" and set(query) == {"slot"}:
                slot = next((s for s in self.server.store.slots() if s["id"] == query["slot"]), None)
                if slot is None:
                    raise ValueError("Unknown slot")
                self.page("Book " + slot["label"], f'<p>{money(slot["unit_cents"])} per guest; 10% discount at 4 guests.</p>'
                    f'<form method="post" action="/book">{self.form_token()}'
                    f'<input type="hidden" name="slot" value="{escape(slot["id"], quote=True)}">'
                    '<label>Demo label (no personal information)<input name="label" required maxlength="40" pattern="[A-Za-z0-9 -]+" data-oracle-id="book-label"></label>'
                    '<label>Party size<input name="party" type="number" min="1" max="8" step="1" required data-oracle-id="book-party"></label>'
                    '<button type="submit" data-oracle-id="book-submit">Confirm booking</button></form><p data-oracle-id="quote-note">Final integer-cent total appears on confirmation.</p>')
            elif route == "/confirmation" and set(query) == {"id"}:
                booking = self.server.store.booking(query["id"])
                self.page("Booking confirmation", self.booking_card(booking))
            elif route == "/bookings" and not query:
                rows = self.server.store.bookings()
                self.page("Your demo bookings", ''.join(self.booking_card(row) for row in rows) if rows else '<p data-oracle-id="empty-bookings">No demo bookings yet.</p>')
            else:
                self.page("Not found", "<p>No such app route.</p>", 404)
        except ValueError as exc:
            self.page("Request refused", f'<p role="alert" data-oracle-id="error">{escape(str(exc))}</p>', 400)
        except (OSError, sqlite3.Error):
            self.page("Unavailable", '<p role="alert">Demo store unavailable.</p>', 503)

    def booking_card(self, row: dict) -> str:
        bid = escape(row["id"], quote=True)
        cancel = (f'<form method="post" action="/cancel">{self.form_token()}'
                  f'<input type="hidden" name="id" value="{bid}"><button data-oracle-id="cancel-{bid}">Cancel</button></form>'
                  if row["status"] == "active" else '')
        return (f'<article data-oracle-id="booking-{bid}"><h3>{escape(row["label"])} · {escape(row["slot_label"])}</h3>'
                f'<p>Party {row["party"]} · <span data-oracle-id="status-{bid}">{escape(row["status"])}</span></p>'
                f'<p>Subtotal {money(row["subtotal_cents"])}; discount {money(row["discount_cents"])}</p>'
                f'<strong data-oracle-id="total-{bid}">{money(row["total_cents"])}</strong>{cancel}</article>')

    def read_form(self, fields: set[str]) -> dict[str, str]:
        if self.headers.get_all("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
            raise ValueError("One bounded Content-Length required; transfer encoding unsupported")
        length_text = self.headers.get("Content-Length", "")
        if not length_text.isascii() or not length_text.isdecimal() or len(length_text) > 4:
            raise ValueError("Invalid body size")
        length = int(length_text)
        if not 1 <= length <= 2048:
            raise ValueError("Body must be 1–2048 bytes")
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            raise ValueError("URL-encoded form required")
        origins = self.headers.get_all("Origin", [])
        expected_origin = f"http://127.0.0.1:{self.server.server_port}"
        if origins and origins != [expected_origin]:
            raise ValueError("Foreign Origin refused")
        body = self.rfile.read(length)
        if len(body) != length:
            raise ValueError("Truncated form")
        values = parse_qs(body.decode("utf-8", errors="strict"), keep_blank_values=True,
                          strict_parsing=True, max_num_fields=4, errors="strict")
        if set(values) != fields or any(len(v) != 1 for v in values.values()):
            raise ValueError("Missing, duplicate or extra form fields")
        form = {key: v[0] for key, v in values.items()}
        if not secrets.compare_digest(form["token"].encode("utf-8"), self.server.form_token.encode("ascii")):
            raise ValueError("Form token refused")
        return form

    def do_POST(self) -> None:
        try:
            route, query = self.route()
            if query:
                raise ValueError("Mutation query fields unsupported")
            if route == "/book":
                form = self.read_form({"token", "slot", "label", "party"})
                booking_id = self.server.store.create(form["slot"], form["label"], form["party"])
            elif route == "/cancel":
                form = self.read_form({"token", "id"})
                booking_id = form["id"]
                self.server.store.cancel(booking_id)
            else:
                self.page("Not found", "<p>No such mutation route.</p>", 404)
                return
            self.send_response(303)
            self.send_header("Location", "/confirmation?id=" + booking_id)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
        except (ValueError, UnicodeError) as exc:
            self.page("Request refused", f'<p role="alert" data-oracle-id="error">{escape(str(exc))}</p>', 400)
        except (OSError, sqlite3.Error):
            self.page("Unavailable", '<p role="alert">Demo store unavailable.</p>', 503)


def main() -> None:
    parser = argparse.ArgumentParser(description="Harbour authored demo; later owner/port authorization required")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 20000 <= args.port <= 29999:
        parser.error("Use an owner-authorized agent-ports reservation in 20000–29999")
    store = Store(args.state_dir / "harbour.sqlite")
    store.initialize()
    with HarbourServer(args.port, store) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
