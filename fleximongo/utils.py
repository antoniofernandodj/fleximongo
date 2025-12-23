
from typing import Dict


def register_strategy(
        strategy_name: str,
        mapping: Dict[str, type]
    ):

    def decorator(StrategyClass: type):

        mapping[strategy_name] = StrategyClass
        print(mapping)

    return decorator