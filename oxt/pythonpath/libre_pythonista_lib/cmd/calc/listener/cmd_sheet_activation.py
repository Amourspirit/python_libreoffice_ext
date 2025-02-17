from __future__ import annotations
from typing import cast, TYPE_CHECKING
import time

from ooodev.loader import Lo
from ooodev.exceptions import ex as mEx  # noqa: N812

if TYPE_CHECKING:
    from ooodev.calc import CalcDoc, CalcSheetView
    from oxt.pythonpath.libre_pythonista_lib.sheet.listen.sheet_activation_listener import SheetActivationListener
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.cmd.cmd_t import CmdT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind
else:
    from libre_pythonista_lib.sheet.listen.sheet_activation_listener import SheetActivationListener
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.cmd.cmd_t import CmdT
    from libre_pythonista_lib.kind.calc_cmd_kind import CalcCmdKind


class CmdSheetActivation(LogMixin, CmdT):
    """Adds new modifier listeners for new sheets"""

    def __init__(self) -> None:
        LogMixin.__init__(self)
        self._doc = cast("CalcDoc", Lo.current_doc)
        self._success = False

    def _get_view(self) -> CalcSheetView | None:
        try:
            view = self._doc.get_view()
            if view.view_controller_name == "Default":
                self.log.debug("View controller is Default.")
                return view
            else:
                # this could mean that the print preview has been activated.
                # Print Preview view controller Name: PrintPreview
                self.log.debug(
                    "'%s' is not the default view controller. Returning.",
                    view.view_controller_name,
                )
            return None

        except mEx.MissingInterfaceError as e:
            self.log.debug("Error getting view from document. %s", e)
            return None

    def execute(self) -> None:
        self._success = False
        view = self._get_view()
        if view is None:
            self.log.debug("View is None. May be print preview. Returning.")
            return
        try:
            sheet_act_listener = SheetActivationListener()  # singleton
            sheet_act_listener.set_trigger_state(True)
            view.component.removeActivationEventListener(sheet_act_listener)
            view.component.addActivationEventListener(sheet_act_listener)

            if view.is_form_design_mode():
                try:
                    self.log.debug("Setting form design mode to False")
                    view.set_form_design_mode(False)
                    self.log.debug("Form design mode set to False")
                    # doc.toggle_design_mode()
                except Exception:
                    self.log.warning("Unable to set form design mode", exc_info=True)
            else:
                self.log.debug("Form design mode is False. Toggling on and off.")
                view.set_form_design_mode(True)
                time.sleep(0.1)
                view.set_form_design_mode(False)
        except Exception:
            self.log.exception("Error initializing sheet activation listener")
            return
        self.log.debug("Successfully executed command.")
        self._success = True

    def undo(self) -> None:
        if self._success:
            view = self._get_view()
            try:
                if view is not None:
                    sheet_act_listener = SheetActivationListener()  # singleton
                    sheet_act_listener.set_trigger_state(False)
                    view.component.removeActivationEventListener(sheet_act_listener)
                    self.log.debug("Successfully executed undo command.")
            except Exception:
                self.log.exception("Error removing sheet activation listener")
        else:
            self.log.debug("Undo not needed.")

    @property
    def success(self) -> bool:
        return self._success

    @property
    def kind(self) -> CalcCmdKind:
        return CalcCmdKind.SIMPLE
