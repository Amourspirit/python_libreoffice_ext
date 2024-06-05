from __future__ import annotations
from typing import List, TYPE_CHECKING
import types
import re
from .last_dict import LastDict
from .regex_last_line import RegexLastLine
from .eval_code import EvalCode

if TYPE_CHECKING:
    from .code_rule_t import CodeRuleT


class CodeRules:
    """Manages rules for Versions"""

    def __init__(self, auto_register: bool = True) -> None:
        """
        Initialize VerRules

        Args:
            auto_register (bool, optional): Determines if know rules are automatically registered. Defaults to True.
        """
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
        if rule in self._rules:
            return
        self._reg_rule(rule=rule)

    def add_rule_at(self, index: int, rule: CodeRuleT) -> None:
        """
        Register rule at index

        Args:
            index (int): Index to insert rule
            rule (CodeRuleT): Rule to register
        """
        if rule in self._rules:
            return
        self._rules.insert(index, rule)

    def remove_rule(self, rule: CodeRuleT):
        """
        Unregister Rule

        Args:
            rule (CodeRuleT): Rule to unregister

        Raises:
            ValueError: If an error occurs
        """
        try:
            self._rules.remove(rule)
        except ValueError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def remove_rule_at(self, index: int):
        """
        Unregister Rule at index

        Args:
            index (int): Index to remove rule

        Raises:
            ValueError: If an error occurs
        """
        try:
            del self._rules[index]
        except IndexError as e:
            msg = f"{self.__class__.__name__}.unregister_rule() Unable to unregister rule."
            raise ValueError(msg) from e

    def _reg_rule(self, rule: CodeRuleT):
        self._rules.append(rule)

    def _register_known_rules(self):
        # re.compile(r"^(\w+)\s*=")
        self._reg_rule(rule=RegexLastLine())
        self._reg_rule(rule=RegexLastLine(re.compile(r"^(\w+)$")))
        self._reg_rule(rule=EvalCode())
        self._reg_rule(rule=LastDict())

    def get_matched_rule(self, mod: types.ModuleType, code: str) -> CodeRuleT:
        """
        Get matched rules

        Args:
            mod (types.ModuleType): Module
            code (str): Code string.

        Returns:
            List[CodeRuleT]: List of matched rules
        """

        for rule in self._rules:
            rule.set_values(mod, code)
            if rule.get_is_match():
                return rule
            rule.reset()
        # this should never happen LastDict is always a match
        raise ValueError(f"No rule matched for code: {code}")

    # endregion Methods