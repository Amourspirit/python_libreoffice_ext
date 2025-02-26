from __future__ import annotations

from typing import Any, TYPE_CHECKING
from ooodev.calc import CalcCell

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.query.qry_base import QryBase
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import (
        QryModifyTriggerEvent,
    )
else:
    from libre_pythonista_lib.query.qry_base import QryBase
    from libre_pythonista_lib.query.calc.sheet.cell.qry_cell_t import QryCellT
    from libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_modify_trigger_event import QryModifyTriggerEvent


class QryCtlModifyTriggerEvent(QryBase, LogMixin, QryCellT[str]):
    """
    Gets the modify trigger event of the cell such as ``cell_data_type_str``.

    Assigns the modify trigger event to the control as property ``modify_trigger_event``.
    """

    def __init__(self, cell: CalcCell, ctl: Ctl | None = None) -> None:
        """Constructor

        Args:
            ctl (Ctl): Control to populate.
            cell (CalcCell): Cell to query.
        """
        QryBase.__init__(self)
        LogMixin.__init__(self)
        self._cell = cell
        self._ctl = ctl
        self.kind = CalcQryKind.CELL

    def execute(self) -> str:
        """
        Executes the query to get the modify trigger event of the cell.

        Assigns the modify trigger event to the control as property ``modify_trigger_event``

        Returns:
            str: The modify trigger event of the cell.
        """
        qry_shape = QryModifyTriggerEvent(cell=self.cell)
        value = self._execute_qry(qry_shape)
        if self._ctl is not None:
            try:
                kind = RuleNameKind(value)
                self._ctl.modify_trigger_event = kind
                if not self._ctl.cell:
                    self._ctl.cell = self.cell
            except Exception:
                self.log.exception("Error getting rule name")
        return value

    @property
    def cell(self) -> CalcCell:
        return self._cell
