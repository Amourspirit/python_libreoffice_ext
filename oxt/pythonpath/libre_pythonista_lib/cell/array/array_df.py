from __future__ import annotations
from typing import cast, List, TYPE_CHECKING

try:
    # python 3.12+
    from typing import override  # type: ignore
except ImportError:
    from typing_extensions import override

import uno

from ooodev.calc import CalcCell

from ...utils.pandas_util import PandasUtil
from ...cell.state.ctl_state import CtlState
from .array_base import ArrayBase


if TYPE_CHECKING:
    import pandas as pd


class ArrayDF(ArrayBase):
    """Manages Formula and Array for DataFrame."""

    def __init__(self, cell: CalcCell) -> None:
        """
        Constructor

        Args:
            cell (CalcCell): Calc Cell
        """
        ArrayBase.__init__(self, cell)
        self._ctl_state = CtlState(cell)

    @override
    def get_rows_cols(self) -> List[int]:
        """
        Gets the number of rows and columns for a DataFrame.

        Returns:
            List[int]: Number of rows and columns
        """
        with self.log.indent(True):
            dd = self.get_data()

            df = cast("pd.DataFrame", dd.dd_data.data)
            has_headers = bool(dd.dd_data.get("headers", False))
            if has_headers is False:
                has_headers = PandasUtil.has_headers(df)
            has_index_names = PandasUtil.has_index_names(df)
            if self.log.is_debug:
                self.log.debug("get_rows_cols() - Has Headers: %s", has_headers)
                self.log.debug("get_rows_cols() - Has Index Names: %s", has_index_names)

            if self.log.is_debug:
                self.log.debug("DataFrame Shape: %s", df.shape)
            shape = df.shape
            shape_len = len(shape)
            lst = [0, 0]
            if shape_len == 0:
                return lst

            if shape_len == 1:
                lst[0] = shape[0]
            else:
                lst[0] = shape[0]
                lst[1] = shape[1]
            if has_headers:
                lst[0] += 1

            if has_index_names:
                lst[1] += 1
            return lst
