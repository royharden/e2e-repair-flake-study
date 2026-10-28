"""Bounded, text-only projection for authored demo fixtures.

This is an allowlist projection, not a browser, HTML renderer or isolation proof.
"""

from html.parser import HTMLParser
import re


_BLOCKED = {"script", "style", "template", "noscript", "iframe", "object", "embed", "svg", "math", "head"}
_METADATA = re.compile(
    r"(?:(?:https?://|file://)[^\s<>]+|"
    r"(?:[A-Za-z]:[\\/]|\\\\)[^\s<>]+|"
    r"(?:\.{1,2}[\\/]|/)[^\s<>]+|"
    r"\b[A-Za-z0-9_.-]+(?:[\\/][A-Za-z0-9_.-]+)+|"
    r"\b(?:data-oracle|data-testid|data-test|data-cy|data-hook|oracle|"
    r"variant[_-]?(?:id|label)|source[_-]?path|control[_-]?path)\b"
    r"\s*(?:[=:]\s*)?[^\s<>]*)",
    re.IGNORECASE,
)


class _TextProjection(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocked: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _BLOCKED:
            self.blocked.append(tag)
        elif not self.blocked:
            self.parts.append(" ")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.blocked:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.blocked:
            # Malformed nesting fails closed: an inner close cannot expose an outer payload.
            index = len(self.blocked) - 1 - self.blocked[::-1].index(tag)
            del self.blocked[index:]
        if not self.blocked:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.blocked:
            self.parts.append(data)


def project_fixture_text(value: str) -> str:
    """Discard all attributes/comments and non-user-facing payload elements.

    Known path/URL and metadata tokens in visible text are redacted. Output is
    plain text: consumers must escape it if embedding it in HTML. There is no
    arbitrary free-text secrecy guarantee; only explicitly selected fixture
    fields may be passed here, never evaluator labels or source/control blobs.
    """
    if type(value) is not str or len(value.encode("utf-8")) > 65536:
        raise ValueError("fixture text must be a string of at most 64 KiB")
    parser = _TextProjection()
    parser.feed(value)
    parser.close()
    text = " ".join("".join(parser.parts).split())
    return _METADATA.sub("[redacted]", text)
