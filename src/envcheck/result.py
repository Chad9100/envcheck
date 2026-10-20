from __future__ import annotations

from dataclasses import asdict, dataclass

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"


@dataclass
class Result:
    check: str
    status: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)
