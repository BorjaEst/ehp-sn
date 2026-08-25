"""Behavioral tests for the framework-wide digest mechanism (Target 0 hardening).

These tests verify that ``ehp_sn.digests`` owns the exact RFC 8785 (JCS)
canonical serialization and the ``sha256:<hex>`` digest operation, with no
dependence on a lifecycle stage (planning/execution) utility. They lock the
byte-exact canonicalization against RFC 8785 rules so the earlier
"JCS-like" approximation (RFC-8785-*intent*) cannot regress into a new one.
"""

from __future__ import annotations

import hashlib

import pytest
from ehp_sn.digests import canonical_digest, canonicalize


def test_canonicalize_sorts_object_keys_recursively() -> None:
    assert canonicalize({"c": 3, "a": 1, "b": {"z": 26, "y": 25}}) == (
        '{"a":1,"b":{"y":25,"z":26},"c":3}'
    )


def test_canonicalize_is_compact_no_whitespace() -> None:
    assert canonicalize({"a": 1, "b": [1, 2]}) == '{"a":1,"b":[1,2]}'


def test_string_escaping_is_exact_rfc8785() -> None:
    # Control characters U+0000..U+001F are escaped as lower-case \\u00xx.
    assert canonicalize("\u0000\u0001\u001f") == '"\\u0000\\u0001\\u001f"'
    # Quote and backslash.
    assert canonicalize('a"b\\c') == '"a\\"b\\\\c"'
    # BMP non-ASCII printable characters are emitted raw (not \\uXXXX-escaped).
    assert canonicalize("caf\u00e9") == '"caf\u00e9"'
    assert canonicalize("\u4e2d\u6587") == '"\u4e2d\u6587"'


def test_supplementary_plane_escaped_as_surrogate_pair() -> None:
    # U+1D800 lies outside the BMP; JCS requires a \\uXXXX\\uYYYY pair.
    assert canonicalize("\U0001d800") == '"\\uD836\\uDC00"'


def test_number_normalization_is_exact() -> None:
    assert canonicalize(100.0) == "100"  # integer-valued float loses .0
    assert canonicalize(-0.0) == "0"  # negative zero normalizes to 0
    assert canonicalize(1e21) == "1e+21"
    assert canonicalize(1.5e-7) == "1.5e-7"  # exponent has no leading zero
    assert canonicalize(5e-7) == "5e-7"
    assert canonicalize(0.5) == "0.5"
    assert canonicalize(123.456) == "123.456"
    assert canonicalize(-12.5) == "-12.5"


def test_arrays_and_booleans() -> None:
    assert canonicalize([1, True, None, "x"]) == '[1,true,null,"x"]'


def test_order_independence() -> None:
    assert canonicalize({"a": 1, "b": 2}) == canonicalize({"b": 2, "a": 1})


def test_non_json_values_rejected() -> None:
    with pytest.raises(TypeError):
        canonicalize(object())
    with pytest.raises(TypeError):
        canonicalize({"k": {1, 2}})
    # NaN / Infinity are not valid JSON numbers and must be rejected.
    with pytest.raises(TypeError):
        canonicalize(float("nan"))
    with pytest.raises(TypeError):
        canonicalize(float("inf"))


def test_canonical_digest_is_sha256_over_canonical_bytes() -> None:
    value = {"b": 2, "a": 1}
    canonical = canonicalize(value)
    expected = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert canonical_digest(value) == expected


def test_equal_values_yield_equal_digests_different_order() -> None:
    assert canonical_digest({"a": 1, "b": 2}) == canonical_digest({"b": 2, "a": 1})
