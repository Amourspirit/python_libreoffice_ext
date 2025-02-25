from __future__ import annotations
from typing import Any, List
from ooodev.gui.menu.popup_menu import PopupMenu
from ooodev.gui.menu.popup.popup_creator import PopupCreator
from ooodev.loader.inst.doc_type import DocType


class DialogLogMenu:
    def __init__(self, dlg: Any) -> None:  # noqa: ANN401
        self._dlg = dlg
        self._doc = dlg.doc
        self._is_calc_doc = self._doc.DOC_TYPE == DocType.CALC

    def get_file_menu(self) -> PopupMenu:
        menu_data = self._get_file_data()
        popup_creator = PopupCreator()
        popup_menu = popup_creator.create(menu_data)
        return popup_menu

    def _get_file_data(self) -> List[dict]:
        rr = self._dlg.res_resolver.resolve_string

        new_menu = [
            {
                "text": rr("mnuClearData"),
                "command": ".uno:lp.rest_data",
            },
            {
                "text": "-",
            },
            {
                "text": rr("mnuClose"),
                "command": ".uno:lp.close",
            },
        ]
        return new_menu

    def get_view_menu(self) -> PopupMenu:
        menu_data = self._get_view_data()
        popup_creator = PopupCreator()
        popup_menu = popup_creator.create(menu_data)
        return popup_menu

    def _get_view_data(self) -> List[dict]:
        rr = self._dlg.res_resolver.resolve_string

        new_menu = [
            {
                "text": rr("mnuHideWindow"),
                "command": ".uno:lp.hide_window",
            },
        ]
        return new_menu

    def get_settings_menu(self) -> PopupMenu:
        menu_data = self._get_settings_data()
        popup_creator = PopupCreator()
        popup_menu = popup_creator.create(menu_data)
        return popup_menu

    def _get_settings_data(self) -> List[dict]:
        rr = self._dlg.res_resolver.resolve_string

        new_menu = [
            {
                "text": rr("mnuLogSettings"),
                "command": ".uno:lp.log_settings",
            },
        ]
        return new_menu
