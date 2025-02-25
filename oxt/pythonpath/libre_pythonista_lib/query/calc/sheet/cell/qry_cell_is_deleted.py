from __future__ import annotations

from typing import TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import (
        QryCellIsDeleted as UnoQryCellIsDeleted,
    )
else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.query.calc.sheet.uno_cell.qry_cell_is_deleted import (
        QryCellIsDeleted as UnoQryCellIsDeleted,
    )


class QryCellIsDeleted(QryBase, QryCellT[bool]):
    """Gets the source code for a cell"""

    def __init__(self, cell: CalcCell) -> None:
        """Constructor

        Args:
            uri (str): URI of the source code.
            cell (CalcCell): Cell to query.
            src_provider (PySrcProvider, optional): Source provider. Defaults to None.
        """
        QryBase.__init__(self)
        self._cell = cell

    def execute(self) -> bool:
        """
        Executes the query to get the script URL.
        The url will start with ``vnd.sun.star.script:``

        Returns:
            str | None: The script URL if successful, otherwise None.
        """

        qry = UnoQryCellIsDeleted(cell=self._cell.component)
        return self._execute_qry(qry)

    @property
    def cell(self) -> CalcCell:
        return self._cell
