from __future__ import annotations
import ast
import types
from ooodev.utils.helper.dot_dict import DotDict
from ...utils import str_util


class CodeEmpty:
    """
    A class to get the last function only call of a module.
    Expected to match ``sum(1, 2)``.
    """

    def __init__(self) -> None:
        pass

    def set_values(self, mod: types.ModuleType, code: str, ast_mod: ast.Module | None) -> None:
        """
        Set the values for the class.

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.
            ast_mod (ast.Module, None): AST module.
        """
        self.mod = mod
        self.code = code
        self.ast_mod = ast_mod

    def get_is_match(self) -> bool:
        """Check if rules is a match."""
        # if there is no code yet then this is a new cell and thus empty is a match.
        if not self.code:
            return True

        code = str_util.clean_string(self.code)
        if not self.code:
            return True

        return code == ""

    def get_value(self) -> DotDict:
        """Get the list of versions. In this case it will be a single version, unless vstr is invalid in which case it will be an empty list."""
        return DotDict(data=None)

    def reset(self) -> None:
        """Reset the rule releasing any resource it is holding on to."""
        self.mod = None
        self.code = None
        self.ast_mod = None

    def __repr__(self) -> str:
        return "<CodeEmpty()>"
