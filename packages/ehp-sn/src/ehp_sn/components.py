from __future__ import annotations


class ComponentRef:
    def __init__(self, *, kind: str, name: str, version: str):
        self.kind = kind
        self.name = name
        self.version = version


class InvalidReferenceError(Exception):
    pass


__all__ = ["ComponentRef", "InvalidReferenceError"]
