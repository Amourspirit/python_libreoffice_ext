from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING
import os
import sys
import uno
import unohelper
from com.github.amourspirit.extensions.librepythonista import XPy  # type: ignore


def _conditions_met() -> bool:
    try:
        import ooodev
        import verr
        import sortedcontainers
    except ImportError:
        return False
    return True


if TYPE_CHECKING:
    _CONDITIONS_MET = True
else:
    _CONDITIONS_MET = _conditions_met()

if _CONDITIONS_MET:
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.exceptions import ex as mEx


def add_local_path_to_sys_path() -> None:
    # add the path of this module to the sys.path
    this_pth = os.path.dirname(__file__)
    if this_pth not in sys.path:
        sys.path.append(this_pth)


add_local_path_to_sys_path()

from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from pythonpath.libre_pythonista_lib.dialog.py.dialog_python import DialogPython
    from pythonpath.libre_pythonista_lib.code.py_code import PythonCode
    from pythonpath.libre_pythonista_lib.code.py_source_mgr import PyInstance

    # from pythonpath.libre_pythonista_lib.code.py_cell import PyCell
    from pythonpath.libre_pythonista_lib.code.cell_cache import CellCache
else:
    if _CONDITIONS_MET:
        from libre_pythonista_lib.dialog.py.dialog_python import DialogPython
        from libre_pythonista_lib.code.py_code import PythonCode
        from libre_pythonista_lib.code.py_source_mgr import PyInstance

        # from libre_pythonista_lib.code.py_cell import PyCell
        from libre_pythonista_lib.code.cell_cache import CellCache

implementation_name = "com.github.amourspirit.extension.librepythonista.PyImpl"
implementation_services = ("com.sun.star.sheet.AddIn",)


class PyImpl(unohelper.Base, XPy):
    def __init__(self, ctx):
        self.ctx = ctx
        self._logger = OxtLogger(log_name=self.__class__.__name__)
        # PyInstance.reset_instance()
        # CellCache.reset_instance()
        # it seems init is only call when the functions is first called.
        # ctx is com.sun.star.uno.XComponentContext

    def pyc(self, sheet_num: int, cell_address: str, *args) -> tuple:
        # CellCache should really only be used in this function.
        # It tracks the current cell and the previous cell and has listings for all code cells.
        if not _CONDITIONS_MET:
            self._logger.error("pyc - Conditions not met")
            return ((sheet_num, cell_address),)
        self._logger.debug("pyc entered")
        try:
            _ = Lo.current_doc
        except mEx.MissingInterfaceError:
            self._logger.warning("pyc - MissingInterfaceError from Lo.current_doc. Returning and expecting a recalculation to take place when document is fully loaded.")
            return ((sheet_num, cell_address),)
        result = None
        try:
            
            self._logger.debug(f"pyc - sheet_num: arg {sheet_num}")
            self._logger.debug(f"pyc - cell_address: arg {cell_address}")
            if args:
                self._logger.debug(f"pyc -args: {args}")
            doc = CalcDoc.from_current_doc()
            sheet_idx = sheet_num - 1
            sheet = doc.sheets[sheet_idx]
            xcell = sheet.component.getCellRangeByName(cell_address)
            cell = sheet.get_cell(xcell)
            self._logger.debug(
                f"pyc - Cell {cell.cell_obj} has custom properties: {cell.has_custom_properties()}"
            )

            # py_cell = PyCell(cell)
            cc = CellCache(doc)
            cc_len = len(cc.code_cells[sheet_idx])
            if cc_len == 0:
                CellCache.reset_instance(doc)
                cc = CellCache(doc)
            self._logger.debug(f"pyc - Length of cc: {len(cc.code_cells[sheet_idx])}")
            py_inst = PyInstance(doc)
            # cc_prop = cc.code_prop
            cc.current_sheet_index = sheet_idx
            cc.current_cell = cell.cell_obj
            self._logger.debug(f"CellCache index: {cc.current_sheet_index}")
            self._logger.debug(f"CellCache cell: {cc.current_cell}")
            if not cc.has_cell(cell=cell.cell_obj, sheet_idx=sheet_idx):
                # if not py_cell.has_code():
                self._logger.debug("Py: py cell has no code")
                # prompt for code
                code = self._get_code()
                if code:
                    # py_cell.save_code(code)
                    py_inst.add_source(code=code, cell=cell.cell_obj)
                    # cc.insert(cell=cell.cell_obj, props={cc_prop}, sheet_idx=sheet_idx)
                    # CellCache.reset_instance()
                    # cc = CellCache(doc)
                    cc.current_sheet_index = sheet_idx
                    cc.current_cell = cell.cell_obj
                    PyInstance.reset_instance()
                    py_inst = PyInstance(doc)
                    py_inst.update_all()
            else:
                self._logger.debug("Py: py cell has code")
            self._logger.debug(f"Is First Cell: {cc.is_first_cell()}")
            self._logger.debug(f"Is Last Cell: {cc.is_last_cell()}")
            self._logger.debug(f"Current Cell Index: {cc.get_cell_index()}")

            self._logger.debug(f"Py: py sheet_num: {sheet_num}, cell_address: {cell_address}")
            py_inst = PyInstance(doc)
            if cc.is_first_cell():
                PyInstance.reset_instance()
                py_inst = PyInstance(doc)
                py_inst.update_all()
            py_src = py_inst[cc.current_cell]
            if isinstance(py_src.value, tuple):
                result = py_src.value
            else:
                result = ((py_src.value,),)

        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)
        self._logger.debug("pyc exiting")
        # return ((sheet_idx, cell_address),)
        return result

    def _get_code(self) -> str | None:
        dlg = DialogPython(self.ctx)
        self._logger.debug("Py: py displaying dialog")
        result = None
        if dlg.show():
            self._logger.debug("Py: py dialog returned with OK")
            txt = dlg.text.strip()
            if txt:
                result = dlg.text

            # if code_str:
            # inst = PyInstances(doc.get_active_sheet())
            # self._logger.debug(f"Py: py saving code")
            # code = PythonCode(ctx=self.ctx, verify_is_formula=False)
            # code.save_code(code_str)
            # self._logger.debug(f"Py: py code saved")

        else:
            self._logger.debug("Py: py dialog returned with Cancel")
        return result


def createInstance(ctx):
    return PyImpl(ctx)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(createInstance, implementation_name, implementation_services)
