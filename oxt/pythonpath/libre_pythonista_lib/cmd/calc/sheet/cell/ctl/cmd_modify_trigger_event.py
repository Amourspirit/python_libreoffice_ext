from __future__ import annotations
from typing import List, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcCell
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_base import CmdBase
    from oxt.___lo_pip___.basic_config import BasicConfig
    from oxt.pythonpath.libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import (
        CmdModifyTriggerEvent as CmdPropModifyTriggerEvent,
    )
else:
    from libre_pythonista_lib.cmd.cmd_base import CmdBase
    from ___lo_pip___.basic_config import BasicConfig
    from libre_pythonista_lib.cell.props.rule_name_kind import RuleNameKind
    from libre_pythonista_lib.cmd.calc.sheet.cell.ctl.cmd_cell_ctl_t import CmdCellCtlT
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.doc.calc.doc.sheet.cell.ctl.ctl import Ctl
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.sheet.cell.prop.cmd_modify_trigger_event import (
        CmdModifyTriggerEvent as CmdPropModifyTriggerEvent,
    )


class CmdModifyTriggerEvent(CmdBase, LogMixin, CmdCellCtlT):
    """
    Sets the modify trigger event for the control such as ``cell_data_type_str``.

    Assigns the modify trigger event to the control as property ``modify_trigger_event``.
    """

    def __init__(self, cell: CalcCell, ctl: Ctl, kind: RuleNameKind) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._ctl = ctl
        self._rule_kind = kind
        self._success_cmds: List[CmdT] = []
        if not self._ctl.cell:
            self._ctl.cell = cell
        self._config = BasicConfig()
        self._current = self._ctl.ctl_rule_kind

    def execute(self) -> None:
        self.success = False
        self._state_changed = False
        self._success_cmds.clear()
        try:
            if self._current == self._rule_kind:
                self.log.debug("State is already set.")
                self.success = True
                return
            self._ctl.modify_trigger_event = self._rule_kind

            trigger_event_modification_command = CmdPropModifyTriggerEvent(
                cell=self.cell, name=str(self._ctl.ctl_rule_kind)
            )
            self._execute_cmd(trigger_event_modification_command)
            if trigger_event_modification_command.success:
                self._success_cmds.append(trigger_event_modification_command)
            else:
                raise Exception("Error setting cell shape name")

            self._state_changed = True
        except Exception as e:
            self.log.exception("Error setting control shape name: %s", e)
            self._undo()
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def _undo(self) -> None:
        if not self._state_changed:
            self.log.debug("State has not changed. Undo not needed.")
            return
        for cmd in reversed(self._success_cmds):
            cmd.undo()
        self._success_cmds.clear()
        self._ctl.ctl_rule_kind = self._current
        self.log.debug("Successfully executed undo command.")

    def undo(self) -> None:
        if self.success:
            self._undo()
        else:
            self.log.debug("Undo not needed.")

    @property
    def cell(self) -> CalcCell:
        return self._ctl.cell
