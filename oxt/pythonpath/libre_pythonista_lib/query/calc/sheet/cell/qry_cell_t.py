from __future__ import annotations
from typing import Any, Protocol
from ooodev.calc import CalcCell


class QryCellT(Protocol):
    def execute(self) -> Any:  # noqa: ANN401
        ...

    @property
    def cell(self) -> CalcCell: ...
