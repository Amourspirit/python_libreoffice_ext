from typing import Any, cast, TYPE_CHECKING, Tuple
import contextlib

from ooo.dyn.ui.context_menu_interceptor_action import (
    ContextMenuInterceptorAction as ContextMenuAction,
)
from ooodev.adapter.ui.context_menu_interceptor import ContextMenuInterceptor
from ooodev.adapter.ui.context_menu_interceptor_event_data import (
    ContextMenuInterceptorEventData,
)
from ooodev.calc import CalcDoc, CalcSheetView
from ooodev.events.args.event_args_generic import EventArgsGeneric
from ooodev.gui.menu.context.action_trigger_item import ActionTriggerItem
from ooodev.gui.menu.context.action_trigger_sep import ActionTriggerSep
from ooodev.gui.menu.context.action_trigger_container import ActionTriggerContainer
from ooodev.loader.inst.doc_type import DocType
from .dispatch_provider_interceptor import DispatchProviderInterceptor
from .cell_dispatch_state import CellDispatchState
from ..log.log_inst import LogInst
from ..res.res_resolver import ResResolver
from ..const import (
    UNO_DISPATCH_CODE_EDIT_MB,
    UNO_DISPATCH_CODE_DEL,
    UNO_DISPATCH_CELL_SELECT,
    UNO_DISPATCH_CELL_SELECT_RECALC,
)
from ..cell.props.key_maker import KeyMaker
from ..cell.state.ctl_state import CtlState
from ..cell.state.state_kind import StateKind

if TYPE_CHECKING:
    from com.sun.star.table import CellAddress


def on_menu_intercept(
    src: ContextMenuInterceptor,
    event: EventArgsGeneric[ContextMenuInterceptorEventData],
    view: CalcSheetView,
) -> None:
    """Event Listener for the context menu intercept."""
    global UNO_DISPATCH_CODE_EDIT_MB

    log = None

    def log_debug(msg: str):
        nonlocal log
        if log is None:
            return
        with log.indent(True):
            log.debug(msg)

    with contextlib.suppress(Exception):
        # don't block other menus if there is an issue.

        container = event.event_data.event.action_trigger_container

        # The default action is ContextMenuAction.IGNORED.
        # In Linux as least (Ubuntu 20.04) the default will crash LibreOffice.
        # This is not the case in Windows, so this seems to be a bug.
        # Setting the action to ContextMenuAction.CONTINUE_MODIFIED will prevent the crash and
        # all seems to work well.
        event.event_data.action = ContextMenuAction.CONTINUE_MODIFIED

        first_cmd = container[0].CommandURL  # type: ignore
        last_cmd = container[-1].CommandURL  # type: ignore
        fl = (first_cmd, last_cmd)

        with contextlib.suppress(Exception):
            log = LogInst()
            log.debug(f"First Command: {first_cmd}")
            log.debug(f"Last Command: {last_cmd}")

        # check the first and last items in the container
        if fl == (".uno:Cut", ".uno:FormatCellDialog"):
            # get the current selection
            selection = event.event_data.event.selection.get_selection()

            if selection.getImplementationName() == "ScCellObj":
                # current selection is a cell.

                key_maker = KeyMaker()  # singleton
                addr = cast("CellAddress", selection.getCellAddress())
                doc = CalcDoc.from_current_doc()
                sheet = doc.get_active_sheet()
                cell_obj = doc.range_converter.get_cell_obj_from_addr(addr)
                cell = sheet[cell_obj]
                if not cell.has_custom_property("libre_pythonista_codename"):
                    if log is not None:
                        with log.indent(True):
                            log.debug(
                                f"Cell {cell_obj} does not have libre_pythonista_codename custom property."
                            )
                    return

                # insert a new menu item.
                # it's command is a custom .uno: command. Note that the command is not a built-in command.
                # The command also contains args for the sheet and cell.
                # A custom dispatch interceptor will be used to handle the command.
                try:
                    log_debug("Getting Resource for mnuEditCode")
                    items = ActionTriggerContainer()
                    rr = ResResolver()
                    edit_mnu = rr.resolve_string("mnuEditCode")
                    del_mnu = rr.resolve_string("mnuDeletePyCell")
                    menu_main_sub = ResResolver().resolve_string(
                        "mnuMainSub"
                    )  # Pythoninsta
                    cps = CellDispatchState(cell=cell)
                    item = None
                    if cps.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT_MB):
                        log_debug(
                            "CellDispatchState.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT_MB) is True"
                        )
                        this_cmd = f"{UNO_DISPATCH_CODE_EDIT_MB}?sheet={sheet.name}&cell={cell_obj}&in_thread=0"
                        log_debug(
                            f"Adding ActionTriggerItem: Label = {edit_mnu}; Command = {this_cmd}"
                        )
                        items.append(ActionTriggerItem(this_cmd, edit_mnu))  # type: ignore

                        this_cmd = f"{UNO_DISPATCH_CODE_DEL}?sheet={sheet.name}&cell={cell_obj}"
                        log_debug(
                            f"Adding ActionTriggerItem: Label = {del_mnu}; Command = {this_cmd}"
                        )
                        items.append(ActionTriggerItem(this_cmd, del_mnu))  # type: ignore

                        # container.insert_by_index(4, ActionTriggerItem(f".uno:libre_pythonista.calc.menu.reset.orig?sheet={sheet.name}&cell={cell_obj}", "Rest to Original"))  # type: ignore
                        items.append(ActionTriggerSep())  # type: ignore
                        item = ActionTriggerItem(
                            menu_main_sub, menu_main_sub, sub_menu=items
                        )
                    else:
                        log_debug(
                            "CellDispatchState.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT_MB) is False"
                        )
                    recalc_name = rr.resolve_string("mnuRecalcCell")  # Select Cell
                    items.append(
                        ActionTriggerItem(
                            f"{UNO_DISPATCH_CELL_SELECT_RECALC}?sheet={sheet.name}&cell={cell_obj}",
                            recalc_name,
                        )
                    )  # type: ignore

                    # is this a DataFrame or similar?
                    dp_cmd = cps.get_rule_dispatch_cmd()
                    log_debug(f"Rule Dispatch Command: {dp_cmd}")
                    if dp_cmd and cell.get_custom_property(
                        key_maker.cell_array_ability_key, False
                    ):
                        log_debug("Cell has array ability.")
                        items.append(ActionTriggerSep())  # type: ignore
                        state = CtlState(cell).get_state()
                        if state == StateKind.ARRAY:
                            log_debug("State is ARRAY")
                            py_obj = rr.resolve_string("mnuViewPyObj")  # Python Object
                            items.append(
                                ActionTriggerItem(
                                    f"{dp_cmd}?sheet={sheet.name}&cell={cell_obj}",
                                    py_obj,
                                )
                            )  # type: ignore
                        else:
                            log_debug("State is not ARRAY")
                            array = rr.resolve_string("mnuViewArray")  # Array
                            items.append(
                                ActionTriggerItem(
                                    f"{dp_cmd}?sheet={sheet.name}&cell={cell_obj}",
                                    array,
                                )
                            )  # type: ignore

                    if item is not None and items.getCount() > 0:
                        container.insert_by_index(4, item)  # type: ignore
                    event.event_data.action = ContextMenuAction.CONTINUE_MODIFIED
                except Exception:
                    if log is not None:
                        log.error("Error inserting context menu item.", exc_info=True)
        else:
            # check for Plot Figure
            if _mi_plot_figure(container, fl, event):
                event.event_data.action = ContextMenuAction.CONTINUE_MODIFIED
                return


def _mi_plot_figure(container: Any, fl: Tuple[str, str], event: Any) -> bool:
    """
    Menu Item for Plot Figure.
    """
    if not fl == (".uno:Cut", ".uno:EditQrCode"):
        return False
    # get the current selection
    selection = event.event_data.event.selection.get_selection()
    if selection.getImplementationName() != "com.sun.star.drawing.SvxShapeCollection":
        return False
    if len(selection) != 1:
        return False

    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        log.debug("Plot Figure Match.")
        try:
            # get the anchor cell
            shape = selection[0]
            cell = shape.Anchor
            if cell.getImplementationName() != "ScCellObj":
                return False

            addr = cast("CellAddress", cell.getCellAddress())
            doc = CalcDoc.from_current_doc()
            sheet = doc.get_active_sheet()
            cell_obj = doc.range_converter.get_cell_obj_from_addr(addr)
            cell = sheet[cell_obj]
            if not cell.has_custom_property("libre_pythonista_codename"):
                if log is not None:
                    with log.indent(True):
                        log.debug(
                            f"Cell {cell_obj} does not have libre_pythonista_codename custom property."
                        )
                return False

            items = ActionTriggerContainer()
            rr = ResResolver()
            edit_mnu = rr.resolve_string("mnuEditCode")
            del_mnu = rr.resolve_string("mnuDeletePyCell")
            menu_main_sub = ResResolver().resolve_string("mnuMainSub")  # Pythoninsta
            cps = CellDispatchState(cell=cell)
            item = None
            if cps.is_dispatch_enabled(UNO_DISPATCH_CODE_EDIT_MB):
                items.append(
                    ActionTriggerItem(
                        f"{UNO_DISPATCH_CODE_EDIT_MB}?sheet={sheet.name}&cell={cell_obj}&in_thread=0",
                        edit_mnu,
                    )
                )  # type: ignore
                items.append(
                    ActionTriggerItem(
                        f"{UNO_DISPATCH_CODE_DEL}?sheet={sheet.name}&cell={cell_obj}",
                        del_mnu,
                    )
                )  # type: ignore
                # container.insert_by_index(4, ActionTriggerItem(f".uno:libre_pythonista.calc.menu.reset.orig?sheet={sheet.name}&cell={cell_obj}", "Rest to Original"))  # type: ignore
                items.append(ActionTriggerSep())  # type: ignore
                item = ActionTriggerItem(menu_main_sub, menu_main_sub, sub_menu=items)

            sel_name = rr.resolve_string("mnuSelCell")  # Select Cell
            items.append(
                ActionTriggerItem(
                    f"{UNO_DISPATCH_CELL_SELECT}?sheet={sheet.name}&cell={cell_obj}",
                    sel_name,
                )
            )  # type: ignore
            recalc_name = rr.resolve_string("mnuRecalcCell")  # Select Cell
            items.append(
                ActionTriggerItem(
                    f"{UNO_DISPATCH_CELL_SELECT_RECALC}?sheet={sheet.name}&cell={cell_obj}",
                    recalc_name,
                )
            )  # type: ignore

            if item is not None and items.getCount() > 0:
                container.insert_by_index(4, item)  # type: ignore

            return True
        except Exception:
            if log:
                log.exception("Plot Figure Error.")

    return False


def register_interceptor(doc_comp: Any):
    """
    Registers the dispatch provider interceptor.

    This interceptor will be used to handle the custom .uno: command.

    Args:
        doc (doc_comp): CalcDoc or Uno Calc Component Document.
    """
    if doc_comp is None:
        raise ValueError("doc_comp is None")
    dt = getattr(doc_comp, "DOC_TYPE", None)
    if dt is None:
        # logger.debug(CalcDoc.DOC_TYPE.get_service())
        # logger.debug(f"Is Doc Type {Info.is_doc_type(doc_comp, CalcDoc.DOC_TYPE.get_service())}")
        doc = cast(CalcDoc, CalcDoc.get_doc_from_component(doc_comp))  # type: ignore
    else:
        doc = cast(CalcDoc, doc_comp)
    if doc.DOC_TYPE != DocType.CALC:
        raise ValueError("Not a CalcDoc")

    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        with log.indent(True):
            log.debug("Registering Dispatch Provider Interceptor")

    if DispatchProviderInterceptor.has_instance(doc):
        if log:
            with log.indent(True):
                log.debug("Dispatch Provider Interceptor already registered.")
        return
    inst = DispatchProviderInterceptor(doc)  # singleton
    frame = doc.get_frame()
    frame.registerDispatchProviderInterceptor(inst)  # type: ignore
    view = doc.get_view()
    view.add_event_notify_context_menu_execute(on_menu_intercept)  # type: ignore
    if log:
        with log.indent(True):
            log.debug("Dispatch Provider Interceptor registered.")


def unregister_interceptor(doc_comp: Any):
    """
    Un-registers the dispatch provider interceptor.

    Args:
        doc (doc_comp): CalcDoc or Uno Calc Component Document.
    """
    if doc_comp is None:
        raise ValueError("doc_comp is None")
    dt = getattr(doc_comp, "DOC_TYPE", None)
    if dt is None:
        CalcDoc.DOC_TYPE.get_service()
        doc = cast(CalcDoc, CalcDoc.get_doc_from_component(doc_comp))  # type: ignore
    else:
        doc = cast(CalcDoc, doc_comp)
    if doc.DOC_TYPE != DocType.CALC:
        raise ValueError("Not a CalcDoc")
    log = None
    with contextlib.suppress(Exception):
        log = LogInst()
        with log.indent(True):
            log.debug("UnRegistering Dispatch Provider Interceptor")

    if not DispatchProviderInterceptor.has_instance(doc):
        if log:
            with log.indent(True):
                log.debug("Dispatch Provider Interceptor was not registered.")
        return
    inst = DispatchProviderInterceptor(doc)  # singleton
    frame = doc.get_frame()
    frame.releaseDispatchProviderInterceptor(inst)  # type: ignore
    view = doc.get_view()
    view.remove_event_notify_context_menu_execute(on_menu_intercept)  # type: ignore
    inst.dispose()
    if log:
        with log.indent(True):
            log.debug("Dispatch Provider Interceptor unregistered.")
