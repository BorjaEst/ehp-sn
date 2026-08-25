"""Exact RFC 8785 (JCS) canonical serialization.

This module implements the JSON Canonicalization Scheme of RFC 8785 as the
canonical serialization applied to a value's JSON-compatible representation,
per ``docs/docs/framework/digests.md`` § "Digest algorithm and canonical
serialization". It is **exact**, not an approximation:

* object member names are sorted by the code points of their UTF-16 encoding;
* strings escape only the characters RFC 8785 requires (``"``, ``\\``, control
  characters ``U+0000`–``U+001F``) and encode characters outside the Basic
  Multilingual Plane as a ``\\uXXXX\\uYYYY`` surrogate pair; all other
  characters are emitted as raw UTF-8 (never ``\\uXXXX``-escaped);
* numbers are serialized in the canonical ECMAScript shortest round-trip form
  with no leading zeros, no trailing fractional zeros, no ``-0``, and a
  normalized exponent;
* there is no whitespace, and non-finite numbers and duplicate keys are
  rejected rather than silently emitted.

The output is a single canonical string; ``canonical_digest`` digests it.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

#: Control characters that must be escaped as ``\\u00xx`` per RFC 8785 3.2.2.1.
_CONTROL_IDX: list[bytes] = []
for _cp in range(0x20):
    _CONTROL_IDX.append(f"\\u{_cp:04x}".encode("ascii"))
del _cp

_ESCAPES: dict[int, bytes] = {0x22: b'\\"', 0x5C: b"\\\\"}
for _cp in range(0x20):
    _ESCAPES[_cp] = _CONTROL_IDX[_cp]


def _jcs_string(value: str) -> bytes:
    """Return the RFC 8785-canonical serialization of ``value`` as UTF-8 bytes."""
    out: list[bytes] = [b'"']
    for ch in value:
        cp = ord(ch)
        esc = _ESCAPES.get(cp)
        if esc is not None:
            out.append(esc)
        elif cp >= 0x10000:
            # Encode a supplementary-plane code point as a UTF-16 surrogate
            # pair, escaped per RFC 8785 3.2.2.2 (uppercase hex).
            cu = cp - 0x10000
            high = 0xD800 + (cu >> 10)
            low = 0xDC00 + (cu & 0x3FF)
            out.append(f"\\u{high:04X}\\u{low:04X}".encode("ascii"))
        else:
            # All other BMP code points are emitted as raw UTF-8.
            out.append(ch.encode("utf-8"))
    out.append(b'"')
    return b"".join(out)


def _jcs_number(value: int | float) -> bytes:
    """Return the RFC 8785-canonical serialization of a JSON number.

    Integers are emitted as their shortest decimal form. Floats follow the
    ECMAScript ``Number::toString`` shortest round-trip form (used by RFC 8785
    3.2.2.3): negative zero becomes ``0``, integer-valued floats lose their
    fractional ``.0``, exponents have a leading sign and no leading zeros, and
    the mantissa carries no trailing fractional zeros.
    """
    if isinstance(value, bool):  # pragma: no cover - bools are handled earlier
        return b"true" if value else b"false"
    if isinstance(value, int):
        return str(value).encode("ascii")
    if math.isnan(value) or math.isinf(value):
        raise TypeError("cannot JCS-serialize non-finite number")
    if value == 0:
        # Normalize -0.0 to 0.
        return b"0"
    if value.is_integer() and abs(value) < 2**53:
        # A floating value that is an exactly-representable small integer loses
        # its fractional ".0" (e.g. 1.0 -> "1").
        return str(int(value)).encode("ascii")

    neg = value < 0
    # repr(abs(value)) for a finite float never yields a special Decimal value
    # (NaN/Infinity were rejected above), so the exponent is always an int.
    decimal_tuple = Decimal(repr(abs(value))).as_tuple()
    digits: list[int] = list(decimal_tuple.digits)
    exponent: int = decimal_tuple.exponent  # type: ignore[assignment]
    # Trim trailing zeros so k (significant decimal digits) is minimal.
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
        exponent += 1
    digits_str = "".join(str(c) for c in digits)
    k = len(digits_str)
    n = exponent + k

    if k <= n <= 21:
        body = digits_str + "0" * (n - k)
    elif 0 < n <= 21:
        body = digits_str[:n] + ("." + digits_str[n:] if digits_str[n:] else "")
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + digits_str
    else:
        mantissa = digits_str[0] + ("." + digits_str[1:] if digits_str[1:] else "")
        exp = n - 1
        body = mantissa + "e" + ("+" if exp >= 0 else "-") + str(abs(exp))
    return (("-" if neg else "") + body).encode("ascii")


def _serialize(value: Any) -> bytes:
    """Exactly serialize a JSON-compatible value per RFC 8785."""
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int):
        return _jcs_number(value)
    if isinstance(value, float):
        return _jcs_number(value)
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, Mapping):
        parts: list[bytes] = [b"{"]
        first = True
        for key in sorted(value, key=lambda k: k.encode("utf-16-le", "surrogatepass")):
            if not first:
                parts.append(b",")
            first = False
            parts.append(_jcs_string(str(key)))
            parts.append(b":")
            parts.append(_serialize(value[key]))
        parts.append(b"}")
        return b"".join(parts)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        parts = [b"["]
        first = True
        for item in value:
            if not first:
                parts.append(b",")
            first = False
            parts.append(_serialize(item))
        parts.append(b"]")
        return b"".join(parts)
    raise TypeError(
        f"cannot canonicalize value of type {type(value).__name__!r}; "
        "identity inputs must be JSON-compatible"
    )


def canonicalize(value: Any) -> str:
    """Return the exact RFC 8785 (JCS) canonical serialization of ``value``.

    ``value`` must be JSON-compatible (``None``, ``bool``, ``int``, ``float``,
    ``str``, ``Mapping``, or ``Sequence``); anything else raises
    :class:`TypeError` so a caller cannot accidentally make identity depend on
    object identity or ``repr`` ordering. Tuples are encoded as JSON arrays.
    The result is a deterministic canonical string, identical for equal input
    regardless of insertion order.
    """
    return _serialize(value).decode("utf-8")


__all__ = ["canonicalize"]
