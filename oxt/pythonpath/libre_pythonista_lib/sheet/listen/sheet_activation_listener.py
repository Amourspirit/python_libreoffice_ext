from __future__ import annotations
from typing import Any, TYPE_CHECKING
import contextlib

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import unohelper
from com.sun.star.sheet import XActivationEventListener
from ooodev.events.args.event_args import EventArgs
from ooodev.utils.helper.dot_dict import DotDict

from ...const.event_const import SHEET_ACTIVATION
from ...event.shared_event import SharedEvent

if TYPE_CHECKING:
    from com.sun.star.lang import EventObject
    from com.sun.star.sheet import ActivationEvent
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.log.log_mixin import LogMixin

# is added when document view is complete.
_SHEET_ACTIVATION_LISTENER_KEY = "libre_pythonista_lib.sheet.listen.sheet_activation_listener.SheetActivationListener"


class SheetActivationListener(XActivationEventListener, LogMixin, unohelper.Base):
    """Singleton Class for Sheet Activation Listener."""

    def __new__(cls) -> SheetActivationListener:
        gbl_cache = DocGlobals.get_current()
        if _SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_SHEET_ACTIVATION_LISTENER_KEY]

        inst = super().__new__(cls)
        inst._is_init = False

        gbl_cache.mem_cache[_SHEET_ACTIVATION_LISTENER_KEY] = inst
        return inst

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        XActivationEventListener.__init__(self)
        LogMixin.__init__(self)
        unohelper.Base.__init__(self)
        self._trigger_events = True
        self._is_init = True

    def set_trigger_state(self, trigger: bool) -> None:
        """
        Sets the state of the trigger events.

        Args:
            trigger (bool): The state to set for the trigger events. If True,
                trigger events will be enabled. If False, they will be disabled.
        Returns:
            None
        """
        # removing this listener from the document does not seem to work.
        # by setting the trigger to False, we can prevent the listener from firing.
        self._trigger_events = trigger

    def get_trigger_state(self) -> bool:
        """
        Returns the current state of the trigger events.

        Returns:
            bool: The state of the trigger events.
        """

        return self._trigger_events

    @override
    def activeSpreadsheetChanged(self, aEvent: ActivationEvent) -> None:  # noqa: N803
        """
        Is called whenever data or a selection changed.

        This interface must be implemented by components that wish to get notified of changes of the active Spreadsheet. They can be registered at an XSpreadsheetViewEventProvider component.

        **since**

            OOo 2.0
        """
        if not self._trigger_events:
            self.log.debug("Trigger events is False. Not raising SHEET_ACTIVATION event.")
            return

        self.log.debug("activeSpreadsheetChanged")
        eargs = EventArgs(self)
        eargs.event_data = DotDict(sheet=aEvent.ActiveSheet, event=aEvent)
        se = SharedEvent()
        se.trigger_event(SHEET_ACTIVATION, eargs)

    @override
    def disposing(self, Source: EventObject) -> None:  # noqa: N803
        """
        gets called when the broadcaster is about to be disposed.

        All listeners and all other objects, which reference the broadcaster
        should release the reference to the source. No method should be invoked
        anymore on this object ( including XComponent.removeEventListener() ).

        This method is called for every listener registration of derived listener
        interfaced, not only for registrations at XComponent.
        """
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_SHEET_ACTIVATION_LISTENER_KEY]

    def __del__(self) -> None:
        with contextlib.suppress(Exception):
            gbl_cache = DocGlobals.get_current()
            if _SHEET_ACTIVATION_LISTENER_KEY in gbl_cache.mem_cache:
                del gbl_cache.mem_cache[_SHEET_ACTIVATION_LISTENER_KEY]
