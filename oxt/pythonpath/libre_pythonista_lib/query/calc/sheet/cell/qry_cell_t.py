from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_t import QryT
else:
    from libre_pythonista_lib.query.qry_t import QryT


class QryCellT(QryT, Protocol):
    @property
    def cell(self) -> CalcCell: ...
