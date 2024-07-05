from __future__ import annotations
from typing import Dict, TYPE_CHECKING
import pandas as pd
from typing import List
import uno
from ooodev.calc import CalcCellRange
from ooodev.utils.gen_util import Util as OdUtil
from .tbl_data_obj import TblDataObj
from ..utils.pandas_util import PandasUtil

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class PandasDataObj:
    def __init__(self, cell_rng: CalcCellRange, col_types: Dict[str | int, str] | None = None):
        """
        Constructor

        Args:
            cell_rng (CalcCellRange): The cell range to get the table information from.
            col_types (Dict[str | int, str] | None): A dictionary of column names or indexes and their types.
                Currently only "date" column type is supported.
        """
        self._sheet = cell_rng.calc_sheet
        self._doc = cell_rng.calc_doc
        self._cell_rng = cell_rng
        self._date_column_names: List[str] = []
        self._date_column_indexes: List[int] = []
        self._log = OxtLogger(log_name=self.__class__.__name__)
        if self._log.is_debug:
            self._log.debug(f"init: {cell_rng.range_obj}")
        self._data_info = TblDataObj(cell_rng)
        if col_types:
            self._process_column_types(col_types)
        self._log.debug("init complete.")

    def _process_column_types(self, col_types: Dict[str | int, str]):
        names: Dict[str, str] = {}
        indexes: Dict[int, str] = {}
        for key, value in col_types.items():
            if isinstance(key, str):
                names[key] = value
            elif isinstance(key, int):
                indexes[key] = value

        for key, value in names.items():
            if value == "date":
                self._log.debug(f"_process_column_types() - Added Date Column Name: {key}")
                self._date_column_names.append(key)

        for key, value in indexes.items():
            if value == "date":
                self._log.debug(f"_process_column_types() - Added Date Column index: {key}")
                self._date_column_indexes.append(key)

    def _get_data(self):
        return self._sheet.get_array(range_obj=self._cell_rng.range_obj)

    def _process_df_with_headers(self, df: pd.DataFrame):
        self._log.debug("_process_df_with_headers() Entered.")
        date_col_names = set(self._data_info.get_date_column_names())
        if self._log.is_debug:
            self._log.debug(f"_process_df_with_headers() - Date Column Names Set: {date_col_names}")
        for name in self._date_column_names:
            date_col_names.add(name)
        for index in self._date_column_indexes:
            name = self.get_column_name(index)
            date_col_names.add(name)
        actual_columns = set(self._data_info.headers)
        if self._log.is_debug:
            self._log.debug(f"_process_df_with_headers() - Actual Columns: {actual_columns}")
        # if any name in date_col_names is not in the actual columns then remove it
        names = [name for name in date_col_names if name in actual_columns]
        if names:
            self._log.debug(f"_process_df_with_headers() - Converting to Date Columns: {names}")
            PandasUtil.convert_lo_to_pandas_date_columns(df, *names)
        else:
            self._log.debug("_process_df_with_headers() - No Date Columns to Convert.")
        self._log.debug("_process_df_with_headers() Exiting.")
        return df

    def _process_df_no_headers(self, df: pd.DataFrame):
        self._log.debug("_process_df_no_headers() Entered.")
        dc = self._data_info.date_columns
        count = self._data_info.col_count

        for i in self._date_column_indexes:
            try:
                self._log.debug(f"_process_df_no_headers() - Date Column Index: {i}")
                idx = OdUtil.get_index(i, count)
            except IndexError:
                self._log.warning(f"_process_df_no_headers() Index out of range: {i}. Will not be included")
                continue
            if idx not in dc:
                self._log.debug(f"_process_df_no_headers() - Adding Date Column Index: {idx}")
                dc.append(idx)
        if dc:
            self._log.debug(f"_process_df_no_headers() - Converting to Date Columns: {dc}")
            PandasUtil.convert_lo_to_pandas_date_columns(df, *dc)
        self._log.debug("_process_df_no_headers() Exiting.")
        return df

    def get_data_frame(self) -> pd.DataFrame:
        """
        Gets the dataframe for the instance.
        The DataFrame Frame will have Date columns converted to Pandas Date columns.

        Returns:
            pd.DataFrame: The DataFrame.
        """
        self._log.debug("get_data_frame() Entered.")
        try:
            data = self._get_data()
            data_len = len(data)
            if data_len == 0:
                return pd.DataFrame()

            if self._data_info.has_headers:
                if data_len == 1:
                    self._log.debug("get_data_frame() Exiting. No data. Only Headers")
                    return pd.DataFrame([], columns=data[0])
                df = pd.DataFrame(data[1:], columns=data[0])
                self._process_df_with_headers(df)
            else:
                df = pd.DataFrame(data)
                self._process_df_no_headers(df)
            self._log.debug("get_data_frame() Exiting.")
            return df
        except Exception:
            self._log.exception("get_data_frame()")
            raise

    def get_column_name(self, idx: int) -> str:
        """
        Gets the column name at the given index.

        Args:
            idx (int): The index of the column. Can be a negative index to get from the end.

        Raises:
            IndexError: If the index is out of range.

        Returns:
            str: The name of the column.
        """
        index = OdUtil.get_index(idx=idx, count=len(self._data_info.headers))
        return self._data_info.headers[index]

    # region Properties

    @property
    def has_headers(self) -> bool:
        """Check if the range has header columns."""
        return self._data_info.has_headers

    @property
    def has_date_columns(self) -> bool:
        """Check if the range has date columns."""
        return self._data_info.has_date_columns

    # endregion Properties