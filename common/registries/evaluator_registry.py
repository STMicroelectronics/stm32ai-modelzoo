# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from collections import namedtuple
from common.registries.registry import Registry


class EvaluatorRegistry(Registry):
    """
    Registry for evaluator classes.

    Each entry is uniquely identified by a tuple:
        (evaluator_name, framework, use_case)

    Evaluators should accept: dataloader, model, cfg
    """

    def __init__(self):
        super().__init__()
        self._registry_key = namedtuple(
            'EvaluatorKey', ['evaluator_name', 'framework', 'use_case']
        )

    def register(self, evaluator_name, framework, use_case):
        """
        Decorator to register an evaluator class.
        """
        def wrap(cls):
            key = self._registry_key(
                evaluator_name=evaluator_name or cls.__name__,
                framework=framework,
                use_case=use_case
            )
            if key in self._registry_dict:
                raise KeyError(f"Evaluator {key} is already registered.")
            self._registry_dict[key] = cls
            return cls
        return wrap

    def get(self, evaluator_name, framework, use_case):
        """
        Return the evaluator class (not instantiated).
        """
        key = self._registry_key(
            evaluator_name=evaluator_name,
            framework=framework,
            use_case=use_case
        )
        if key not in self._registry_dict:
            raise KeyError(
                f"Evaluator {evaluator_name} for use_case {use_case} with framework {framework} not found."
            )
        return self._registry_dict[key]

# ---------------------------
# Global registry instance
EVALUATOR_WRAPPER_REGISTRY = EvaluatorRegistry()
