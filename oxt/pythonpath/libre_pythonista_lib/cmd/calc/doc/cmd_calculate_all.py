from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcDoc
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_base import CmdBase
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT
else:
    from libre_pythonista_lib.cmd.cmd_base import CmdBase
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.calc.doc.cmd_doc_t import CmdDocT


class CmdCalculateAll(CmdBase, LogMixin, CmdDocT):
    """Calculate all cells in the document"""

    def __init__(self, doc: CalcDoc) -> None:
        CmdBase.__init__(self)
        LogMixin.__init__(self)
        self._doc = doc

    def execute(self) -> None:
        self.success = False
        try:
            self._doc.component.calculateAll()
        except Exception as e:
            self.log.exception("Error calculating all. Error: %s", e)
            return
        self.log.debug("Successfully executed command.")
        self.success = True

    def undo(self) -> None:
        self.log.debug("Undo not needed for this command.")
