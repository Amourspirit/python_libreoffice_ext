from __future__ import annotations
from typing import List, TYPE_CHECKING
import ast
import types
import re
from .underscore import Underscore

# from .regex_last_line import RegexLastLine
from .assign import Assign
from .expr import Expr
from .lp_fn_plot_expr import LpFnPlotExpr
from .lp_fn_plot_assign import LpFnPlotAssign
from .code_empty import CodeEmpty
from .lp_fn_expr import LpFnExpr
from .lp_fn_assign import LpFnAssign


if TYPE_CHECKING:
    from .code_rule_t import CodeRuleT
    from .....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from .....___lo_pip___.debug.break_mgr import BreakMgr

    break_mgr = BreakMgr()
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    from ___lo_pip___.debug.break_mgr import BreakMgr

    break_mgr = BreakMgr()
    break_mgr.add_breakpoint("libre_pythonista_lib.code.rules.code_rules.get_matched_rule")


class CodeRules:
    """Manages rules for Versions"""

    def __init__(self, auto_register: bool = True) -> None:
        """
        Initialize CodeRules

        Args:
            auto_register (bool, optional): Determines if know rules are automatically registered. Defaults to True.
        """
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._rules: List[CodeRuleT] = []
        if auto_register:
            self._register_known_rules()

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule: CodeRuleT) -> bool:
        return rule in self._rules

    # region Methods

    def get_index(self, rule: CodeRuleT) -> int:
        """
        Get index of rule

        Args:
            rule (CodeRuleT): Rule to get index

        Returns:
            int: Index of rule
        """
        return self._rules.index(rule)

    def add_rule(self, rule: CodeRuleT) -> None:
        """
        Register rule

        Args:
            rule (CodeRuleT): Rule to register
        """
        with self._log.indent(True):
            if rule in self._rules:
                self._log.debug("CodeRules - add_rule() Rule Already added: %s", rule)
                return
            self._log.debug("CodeRules - add_rule() Adding Rule %s", rule)
            self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: CodeRuleT) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (CodeRuleT): Rule to register
        """
        with self._log.indent(True):
            if rule in self._rules:
                self._log.debug("CodeRules - add_rule_at() Rule Already added: %s", rule)
                return
            self._log.debug("CodeRules - add_rule_at() Inserting : %s at index: %i", rule, index)
            self._rules.insert(index, rule)

    def remove_rule(self, rule: CodeRuleT) -> None:
        """
        Unregister Rule

        Args:
            rule (CodeRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        with self._log.indent(True):
            try:
                self._rules.remove(rule)
                self._log.debug("CodeRules - remove_rule() Removed rule: %s", rule)
            except ValueError as e:
                msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
                self._log.error(msg)
                raise ValueError(msg) from e

    def remove_rule_at(self, index: int) -> None:
        """
        Unregister Rule at index

        Args:
            index (int): Index to remove rule

        Raises:
            ValueError: If an error occurs
        """
        with self._log.indent(True):
            try:
                del self._rules[index]
                self._log.debug("CodeRules - remove_rule() Removed rule at index: %i", index)
            except IndexError as e:
                msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
                self._log.error(msg)
                raise ValueError(msg) from e

    def _reg_rule(self, rule: CodeRuleT) -> None:
        self._rules.append(rule)

    def _register_known_rules(self) -> None:
        # re.compile(r"^(\w+)\s*=")
        self._reg_rule(rule=CodeEmpty())
        self._reg_rule(rule=LpFnPlotExpr())
        self._reg_rule(rule=LpFnPlotAssign())
        self._reg_rule(rule=LpFnExpr())
        self._reg_rule(rule=LpFnAssign())
        self._reg_rule(rule=Expr())
        self._reg_rule(rule=Assign())
        self._reg_rule(rule=Underscore())

    def get_matched_rule(self, mod: types.ModuleType, code: str, ast_mod: ast.Module | None) -> CodeRuleT:
        """
        Get matched rules

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.

        Returns:
            List[CodeRuleT]: List of matched rules
        """
        break_mgr.check_breakpoint("libre_pythonista_lib.code.rules.code_rules.get_matched_rule")
        with self._log.indent(True):
            found_rule = None
            for rule in self._rules:
                rule.set_values(mod, code, ast_mod)
                if rule.get_is_match():
                    self._log.debug("CodeRules - get_matched_rule() found match rule: %s", rule)
                    found_rule = rule
                    break
                rule.reset()
            if found_rule:
                return found_rule
            # this should never happen LastDict is always a match
            raise ValueError(f"No rule matched for code: {code}")

    def __repr__(self) -> str:
        return "<CodeRules()>"

    # endregion Methods
