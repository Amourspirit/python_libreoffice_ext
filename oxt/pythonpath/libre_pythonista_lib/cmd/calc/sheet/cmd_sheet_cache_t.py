from __future__ import annotations
from typing import Tuple, Protocol


from ooodev.calc import CalcSheet


class CmdSheetCacheT(Protocol):
    def execute(self) -> None:  # noqa: ANN401
        ...

    def undo(self) -> None:  # noqa: ANN401
        ...

    @property
    def success(self) -> bool: ...

    @property
    def sheet(self) -> CalcSheet: ...

    @property
    def cache_keys(self) -> Tuple[str, ...]: ...
