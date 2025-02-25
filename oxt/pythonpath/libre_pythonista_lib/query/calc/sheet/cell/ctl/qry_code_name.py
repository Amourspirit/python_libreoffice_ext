from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import (
        QryCodeName as QryPropCodeName,
    )
else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_code_name import QryCodeName as QryPropCodeName


class QryCodeName(QryBase, QryCellT[str]):
    """Gets the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        self.kind = CalcQryKind.CELL
        self._cell = cell
        self._ctl = ctl

    def execute(self) -> str:
        """
        Executes the query to get code name

        Returns:
            str: The code name
        """
        qry_code_name = QryPropCodeName(cell=self.cell)
        value = self._execute_qry(qry_code_name)

        if self._ctl is not None:
            self._ctl.ctl_code_name = value
            if not self._ctl.cell:
                self._ctl.cell = self.cell
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
