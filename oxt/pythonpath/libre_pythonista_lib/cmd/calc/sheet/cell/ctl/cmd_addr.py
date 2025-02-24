from __future__ import annotations
from typing import List, TYPE_CHECKING

from ooodev.utils.gen_util import NULL_OBJ

if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr as CmdPropAddr
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr
    from oxt.pythonpath.libre_pythonista_lib.query.qry_handler import QryHandler
else:
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_addr import CmdAddr as CmdPropAddr
    from libre_pythonista_lib.cmd.cmd_handler import CmdHandler
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.cell.prop.qry_addr import QryAddr
    from libre_pythonista_lib.query.qry_handler import QryHandler


class CmdAddr(LogMixin, CmdCellCtlT):
    """Sets the address of the cell such as ``sheet_index=0&cell_addr=A1``"""

    def __init__(self, cell: CalcCell, ctl: Ctl) -> None:
        LogMixin.__init__(self)
        self._ctl = ctl
        self._success = False

        self._kind = CalcCmdKind.CELL
        self._cmd_handler = CmdHandler()
        self._qry_handler = QryHandler()
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._current_state = NULL_OBJ

    def _get_current_state(self) -> str:
        qry = QryAddr(cell=self.cell)
        return self._qry_handler.handle(qry)

    def execute(self) -> None:
        if self._current_state is NULL_OBJ:
            self._current_state = self._get_current_state()

        self._success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            addr = f"sheet_index={self.cell.calc_sheet.sheet_index}&cell_addr={self.cell.cell_obj}"
            if self._current_state == addr:
                self.log.debug("State is already set.")
                self._success = True
                return
            self._ctl.addr = addr

            cmd_prop_addr = CmdPropAddr(cell=self.cell, addr=addr)
            self._cmd_handler.handle(cmd_prop_addr)
            if cmd_prop_addr.success:
                self._success_cmds.append(cmd_prop_addr)
            else:
                raise Exception("Error setting cell address")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting address: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            cmd.undo()
        self._success_cmds.clear()
        self._ctl.addr = self._current_state
        self.log.debug("Successfully executed undo command.")

    def undo(self) -> None:
        if self._success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell

    @property
    def kind(self) -> CalcCmdKind:
        """Gets/Sets the kind of the command. Defaults to ``CalcCmdKind.CELL``."""
        return self._kind

    @kind.setter
    def kind(self, value: CalcCmdKind) -> None:
        self._kind = value
