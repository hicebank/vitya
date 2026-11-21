from typing import Any, Dict, Iterable, List

import pytest


def parametrize_with_dict(argnames: List[str], cases: Iterable[Dict[str, Any]]):
    def decorator(func):
        return pytest.mark.parametrize(
            argnames,
            [
                pytest.param(*[case[arg_name] for arg_name in argnames], id=str(case.get('case_id') or idx))
                for idx, case in enumerate(cases)
            ],
        )(func)

    return decorator


def first_validation_cause(error):
    if hasattr(error, 'raw_errors'):
        return error.raw_errors[0].exc
    return error.errors()[0]['ctx']['error']
