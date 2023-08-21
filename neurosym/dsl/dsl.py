from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..programs.hole import Hole
from ..programs.s_expression import InitializedSExpression, SExpression
from ..types.type import Type

from .production import Production


@dataclass
class DSL:
    productions: List[Production]
    # variable_system: VariableSystem TODO(KG) add this

    def __post_init__(self):
        symbols = set()
        for production in self.productions:
            assert (
                production.symbol() not in symbols
            ), f"Duplicate symbol {production.symbol()}"
            symbols.add(production.symbol())
        self._production_by_symbol = {
            production.symbol(): production for production in self.productions
        }

    def arity(self, sym: str) -> int:
        """
        Returns the arity of the production with the given symbol.
        """
        return self.get_production(sym).type_signature().arity()

    def expansions_for_type(self, type: Type) -> List[SExpression]:
        """
        Possible expansions for the given type.

        An expansion is an SExpression with holes in it. The holes can be filled in with
        other SExpressions to produce a complete SExpression.
        """
        result = []
        for production in self.productions:
            arg_types = production.type_signature().unify_return(type)
            if arg_types is not None:
                result.append(
                    SExpression(
                        production.symbol(),
                        tuple(Hole.of(t) for t in arg_types),
                    )
                )
        return result

    def get_production(self, symbol: str) -> Production:
        """
        Return the production with the given symbol.
        """
        return self._production_by_symbol[symbol]

    def initialize(
        self, program: SExpression, hole_callback=None
    ) -> InitializedSExpression:
        """
        Initializes all the productions in the given program.

        Returns a new program with the same structure, but with all the productions
        initialized.
        """
        if isinstance(program, Hole):
            assert hole_callback is not None
            return hole_callback(program)
        prod = self.get_production(program.symbol)
        return InitializedSExpression(
            program.symbol,
            tuple(self.initialize(child) for child in program.children),
            prod.initialize(self),
        )

    def compute_on_pytorch(self, program: InitializedSExpression):
        prod = self.get_production(program.symbol)
        return prod.compute_on_pytorch(
            self,
            program.state,
            *[self.compute_on_pytorch(child) for child in program.children],
        )

    def all_rules(self, *target_types) -> Dict[Type, List[Tuple[str, List[Type]]]]:
        """
        Returns a dictionary of all the rules in the DSL, where the keys are the types
        that can be expanded, and the values are a list of tuples of the form
        (symbol, types), where symbol is the symbol of the production, and types is a
        list of types that can be used to expand the given type.

        This is useful for generating a PCFG.
        """
        types_to_expand = list(target_types)
        rules = {}
        while len(types_to_expand) > 0:
            type = types_to_expand.pop()
            if type in rules:
                continue
            rules[type] = []
            for production in self.productions:
                types = production.type_signature().unify_return(type)
                if types is None:
                    continue
                rules[type].append((production.symbol(), types))
                types_to_expand.extend(types)
        return rules

    def validate_all_rules_reachable(self, *target_types):
        """
        Checks that all the rules in the DSL are reachable from at least one of the
        target types.
        """
        symbols = set()
        rules = self.all_rules(*target_types)
        for rule in rules.values():
            symbols.update([symbol for symbol, _ in rule])
        for production in self.productions:
            assert production.symbol() in symbols, (
                f"Production {production.symbol()} is unreachable from target types "
                f"{target_types}"
            )

    def compute_type(self, program: SExpression) -> Type:
        """
        Computes the type of the given program.
        """
        child_types = [self.compute_type(child) for child in program.children]
        prod = self.get_production(program.symbol)
        return prod.type_signature().unify_arguments(child_types)

    def children_types(self, program_type: Type, program: SExpression) -> List[Type]:
        """
        Returns the types of the children of the given program.
        """
        prod = self.get_production(program.symbol)
        return prod.type_signature().unify_return(program_type)

    def collect_types_of_unknown_productions(
        self, program_type: Type, program: SExpression
    ) -> List[Tuple[SExpression, Type]]:
        """
        Returns a list of (program, type) pairs, where each program
            does not have a production in the DSL, and the type is the type of the
            program, as inferred by the signatures of the productions in the DSL
            that surround it.
        """
        if program.symbol not in self._production_by_symbol:
            return [(program, program_type)]
        prod = self.get_production(program.symbol)
        child_types = prod.type_signature().unify_return(program_type)
        assert child_types is not None
        result = []
        for child_type, child in zip(child_types, program.children):
            result.extend(self.collect_types_of_unknown_productions(child_type, child))
        return result
