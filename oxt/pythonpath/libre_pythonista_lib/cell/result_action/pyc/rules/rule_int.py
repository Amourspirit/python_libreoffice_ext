from __future__ import annotations
from typing import Any

from .rule_base import RuleBase


class RuleInt(RuleBase):
    def _get_data_type_name(self) -> str:
        return self.key_maker.rule_names.cell_data_type_int

    def get_is_match(self) -> bool:
        result = self.data.get("data", None)
        if result is None:
            return False
        if isinstance(result, int):
            return True
        if not isinstance(result, str):
            return False
        if self._get_is_value_int(result):
            self.data["data"] = int(result)
            return True
        return False

    def _get_is_value_int(self, value: str) -> bool:
        try:
            if "." in value:
                # don't allow floats
                return False
            int(value)
            return True
        except ValueError:
            return False

    def action(self) -> Any:  # noqa: ANN401
        self._update_properties(
            **{
                self.key_maker.cell_array_ability_key: False,
                self.cell_prop_key: self.data_type_name,
                self.cell_pyc_rule_key: self.data_type_name,
            }
        )
        return ((self.data.data,),)
