from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
else:
    from libre_pythonista_lib.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl


class CmdCodeNameDel(CmdBase, LogMixin, CmdCellCtlT):
    """Deletes the code name of the control"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_code_name = self._ctl.ctl_code_name
        self._current_dict_code_name = self.cell.extra_data.get("code_name", "")

    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        try:
            if not self._current_code_name:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.ctl_code_name = None
            if self.cell.extra_data.has("code_name"):
                del self.cell.extra_data.code_name
            self._state_changed = True
        except Exception:
            self.log.exception("Error setting code name")
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        self._ctl.ctl_code_name = self._current_code_name
        self.cell.extra_data.code_name = self._current_dict_code_name
        self.log.debug("Successfully executed undo command.")

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell
