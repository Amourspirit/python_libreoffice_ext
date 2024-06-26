from __future__ import annotations
import time
from typing import Any, cast, TYPE_CHECKING, Tuple

import uno
import unohelper
from com.sun.star.awt import XTopWindowListener
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import TOP
from com.sun.star.frame import XFrame

from ooodev.loader import Lo

# from ooo.dyn.awt.window_attribute import WindowAttributeEnum
from ooo.dyn.awt.rectangle import Rectangle
from ooodev.utils.partial.the_dictionary_partial import TheDictionaryPartial
from ooodev.events.args.event_args import EventArgs
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.dialog.dl_control import CtlButton
from ooodev.dialog import BorderKind


if TYPE_CHECKING:
    from com.sun.star.awt import MenuBar
    from com.sun.star.awt import MenuEvent
    from com.sun.star.lang import EventObject
    from ooodev.dialog.dl_control.ctl_base import DialogControlBase
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ..window_type import WindowType
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

com_sun_star_awt_WindowAttribute_SHOW = uno.getConstantByName("com.sun.star.awt.WindowAttribute.SHOW")
com_sun_star_awt_WindowAttribute_BORDER = uno.getConstantByName("com.sun.star.awt.WindowAttribute.BORDER")
com_sun_star_awt_WindowAttribute_SIZEABLE = uno.getConstantByName("com.sun.star.awt.WindowAttribute.SIZEABLE")
com_sun_star_awt_WindowAttribute_MOVEABLE = uno.getConstantByName("com.sun.star.awt.WindowAttribute.MOVEABLE")
com_sun_star_awt_VclWindowPeerAttribute_CLIPCHILDREN = uno.getConstantByName(
    "com.sun.star.awt.VclWindowPeerAttribute.CLIPCHILDREN"
)


class DialogMb(TheDictionaryPartial, XTopWindowListener, unohelper.Base):
    FONT = "DejaVu Sans Mono"
    MARGIN = 3
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 26
    WIDTH = 600
    NB_TAB = 4
    HEADER = 30  # can create space for menus at the top
    FOOTER = 40
    HEIGHT = 310
    MIN_HEIGHT = HEADER + FOOTER + 30
    MIN_WIDTH = 225

    def __init__(self) -> None:
        TheDictionaryPartial.__init__(self)
        XTopWindowListener.__init__(self)
        # XTerminateListener.__init__(self)
        unohelper.Base.__init__(self)
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._disposed = False
        self._width = DialogMb.WIDTH
        self._height = DialogMb.HEIGHT
        self._border_kind = BorderKind.BORDER_3D
        self._current_tab_index = 1
        if self._border_kind != BorderKind.BORDER_3D:
            self._padding = 10
        else:
            self._padding = 14
        self._width = DialogMb.WIDTH
        self._height = DialogMb.HEIGHT
        self._btn_width = DialogMb.BUTTON_WIDTH
        self._btn_height = DialogMb.BUTTON_HEIGHT
        self._margin = DialogMb.MARGIN
        self._frame = None

        self._mb = cast("MenuBar", None)
        try:
            self.parent = self.get_parent()
            self.tk = self.parent.Toolkit  # type: ignore
            self._init_handlers()
            self._init_dialog()
            self._add_frame()
            self._add_menu_bar()
            self._init_buttons()
            self._dialog.addTopWindowListener(self)

        except Exception:
            self._log.exception(f"Error in DialogMb.__init__:")

    def _init_handlers(self) -> None:

        self._fn_on_btn_ok_click = self.on_btn_ok_click
        self._fn_on_btn_cancel_click = self.on_btn_cancel_click

    def _init_dialog(self) -> None:
        """Create dialog and add controls."""
        rect = Rectangle()
        rect.Width = self._width
        rect.Height = self._height

        ps = self.parent.getPosSize()
        rect.X = int((ps.Width - self._width) / 2 - 50)
        rect.Y = int((ps.Height - self._height) / 2 - 100)

        desc = WindowDescriptor()
        desc.Type = TOP
        desc.WindowServiceName = "window"
        desc.ParentIndex = -1
        desc.Parent = None  # type: ignore
        desc.Bounds = rect

        desc.WindowAttributes = (
            com_sun_star_awt_WindowAttribute_SHOW
            + com_sun_star_awt_WindowAttribute_BORDER
            + com_sun_star_awt_WindowAttribute_SIZEABLE
            # + WindowAttributeEnum.CLOSEABLE.value
            + com_sun_star_awt_WindowAttribute_MOVEABLE
            + com_sun_star_awt_VclWindowPeerAttribute_CLIPCHILDREN
        )

        dialog_peer = self.tk.createWindow(desc)

        # create new empty frame and set window on it

        self._dialog = cast("WindowType", dialog_peer)

    def _add_frame(self) -> None:
        """Add frame to dialog"""
        frame = Lo.create_instance_mcf(XFrame, "com.sun.star.frame.Frame", raise_err=True)
        frame.setName("DialogMb_Frame")
        frame.initialize(self._dialog)

        self._frame = frame

    # region Misc Methods

    def _set_tab_index(self, ctl: DialogControlBase) -> None:
        ctl.tab_index = self._current_tab_index
        self._current_tab_index += 1

    def get_parent(self):
        """Returns parent frame"""
        try:
            window = Lo.desktop.get_active_frame().getContainerWindow()
            if window is None:
                raise Exception("Window is None")
            return window
        except Exception:
            self._log.error("Error in get_parent", exc_info=True)
            return None

    # endregion Misc Methods

    # region Controls
    def _init_buttons(self) -> None:
        """Add OK, Cancel and Info buttons to dialog control"""
        sz = self._dialog.getPosSize()

        btn_y = sz.Height - DialogMb.BUTTON_HEIGHT - self._padding - DialogMb.HEADER
        btn_x = sz.Width - DialogMb.BUTTON_WIDTH - self._padding

        self._ctl_btn_cancel = CtlButton.create(
            self._dialog,
            x=btn_x,
            y=btn_y,
            width=DialogMb.BUTTON_WIDTH,
            height=DialogMb.BUTTON_HEIGHT,
            Label="Cancel",
        )
        self._set_tab_index(self._ctl_btn_cancel)
        sz = self._ctl_btn_cancel.view.getPosSize()
        self._ctl_btn_ok = CtlButton.create(
            self._dialog,
            x=sz.X - sz.Width - self._margin,
            y=sz.Y,
            width=self._btn_width,
            height=self._btn_height,
            Label="OK",
            DefaultButton=True,
        )
        self._set_tab_index(self._ctl_btn_ok)
        self._ctl_btn_ok.add_event_action_performed(self._fn_on_btn_ok_click)  # type: ignore
        self._ctl_btn_cancel.add_event_action_performed(self._fn_on_btn_cancel_click)  # type: ignore

    # endregion Controls

    # endregion button handlers
    def on_btn_ok_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        if self._frame is not None:
            self._frame.dispose()

    def on_btn_cancel_click(self, source: Any, event: EventArgs, control_src: CtlButton) -> None:
        if self._frame is not None:
            self._frame.dispose()

    # endregion Event Handlers

    # region XTopWindowListener
    def windowOpened(self, event: EventObject) -> None:
        """is invoked when a window is activated."""
        self._log.debug("Window Opened")

    def windowActivated(self, event: EventObject) -> None:
        """is invoked when a window is activated."""

        self._log.debug("Window Activated")

    def windowDeactivated(self, event: EventObject) -> None:
        """is invoked when a window is deactivated."""
        self._log.debug("Window De-activated")

    def windowMinimized(self, event: EventObject) -> None:
        """Is invoked when a window is iconified."""
        self._log.debug("Window Minimized")

    def windowNormalized(self, event: EventObject) -> None:
        """is invoked when a window is deiconified."""
        self._log.debug("Window Normalized")

    def windowClosing(self, event: EventObject) -> None:
        """
        is invoked when a window is in the process of being closed.

        The close operation can be overridden at this point.
        """
        self._log.debug("Window Closing")
        self._is_shown = False

    def windowClosed(self, event: EventObject) -> None:
        """is invoked when a window has been closed."""
        self._log.debug("Window Closed")

    def disposing(self, event: EventObject) -> None:

        self._log.debug("Disposing")
        if not self._disposed:
            try:
                self._disposed = True
                self._dialog.removeTopWindowListener(self)
                self._dialog.setMenuBar(None)  # type: ignore
                self._mb = None
                self._dialog.dispose()
            except Exception:
                self._log.error("Error in disposing", exc_info=True)

    # endregion XTopWindowListener

    # region Menubar
    def _get_popup_menu(self):
        from ooodev.gui.menu.popup.popup_creator import PopupCreator

        creator = PopupCreator()
        new_menu = [{"text": "About", "command": ".uno:About"}]
        pm = creator.create(new_menu)
        pm.add_event_item_selected(on_menu_select)
        return pm

    def _add_menu_bar(self) -> None:
        from com.sun.star.awt import XMenuBar
        from com.sun.star.awt import MenuItemStyle

        mb = Lo.create_instance_mcf(XMenuBar, "com.sun.star.awt.MenuBar", raise_err=True)
        mb.insertItem(1, "~First MenuBar Item", MenuItemStyle.AUTOCHECK, 0)
        mb.insertItem(2, "~Second MenuBar Item", MenuItemStyle.AUTOCHECK, 1)
        pm = self._get_popup_menu()
        mb.setPopupMenu(1, pm.component)
        self._mb = mb
        self._dialog.setMenuBar(mb)

    # endregion Menubar


def on_menu_select(src: Any, event: EventArgs, menu: PopupMenu) -> None:
    print("Menu Selected")
    me = cast("MenuEvent", event.event_data)
    command = menu.get_command(me.MenuId)
    if command:
        # check if command is a dispatch command
        if menu.is_dispatch_cmd(command):
            menu.execute_cmd(command)
