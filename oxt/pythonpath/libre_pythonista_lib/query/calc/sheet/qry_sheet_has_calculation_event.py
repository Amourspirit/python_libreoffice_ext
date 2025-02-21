from __future__ import annotations


from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from ooodev.calc import CalcSheet
    from oxt.pythonpath.libre_pythonista_lib.sheet import calculate
    from oxt.pythonpath.libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from oxt.pythonpath.libre_pythonista_lib.log.log_mixin import LogMixin
    from oxt.pythonpath.libre_pythonista_lib.const.cache_const import SHEET_HAS_CALCULATION_EVENT
    from oxt.pythonpath.libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind

else:
    from libre_pythonista_lib.sheet import calculate
    from libre_pythonista_lib.log.log_mixin import LogMixin
    from libre_pythonista_lib.query.calc.sheet.qry_sheet_cache_t import QrySheetCacheT
    from libre_pythonista_lib.const.cache_const import SHEET_HAS_CALCULATION_EVENT
    from libre_pythonista_lib.kind.calc_qry_kind import CalcQryKind


# this class should be call in:
# libre_pythonista_lib.query.calc.sheet.qry_handler_sheet_cache.QryHandlerSheetCache
class QrySheetHasCalculationEvent(LogMixin, QrySheetCacheT[bool]):
    def __init__(self, sheet: CalcSheet) -> None:
        LogMixin.__init__(self)
        self._kind = CalcQryKind.SHEET_CACHE
        self._sheet = sheet

    def execute(self) -> bool:
        """
        Executes the query to check if the sheet has a calculation event.

        Returns:
            bool: True if the sheet has a calculation event, False otherwise.
        """

        try:
            return calculate.sheet_has_calculate_event(self._sheet)
        except Exception:
            self.log.exception("Error executing query")
        return False

    @property
    def sheet(self) -> CalcSheet:
        return self._sheet

    @property
    def cache_key(self) -> str:
        """Gets the cache key."""
        return SHEET_HAS_CALCULATION_EVENT

    @property
    def kind(self) -> CalcQryKind:
        """
        Gets/Sets the kind of the query. Defaults to ``CalcQryKind.SHEET_CACHE``.
        """
        return self._kind

    @kind.setter
    def kind(self, value: CalcQryKind) -> None:
        self._kind = value
