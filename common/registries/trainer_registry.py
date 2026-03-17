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


class TrainerRegistry(Registry):
    """
    Registry for trainer classes.

    Each entry is uniquely identified by a tuple:
        (trainer_name, framework, use_case)

    Trainers should accept: dataloader, model, cfg
    """

    def __init__(self):
        super().__init__()
        self._registry_key = namedtuple(
            'TrainerKey', ['trainer_name', 'framework', 'use_case']
        )

    def register(self, trainer_name, framework, use_case):
        """
        Decorator to register a trainer class.
        """
        def wrap(cls):
            key = self._registry_key(
                trainer_name=trainer_name or cls.__name__,
                framework=framework,
                use_case=use_case
            )
            if key in self._registry_dict:
                raise KeyError(f"Trainer {key} is already registered.")
            self._registry_dict[key] = cls
            return cls
        return wrap

    def get(self, trainer_name, framework, use_case):
        """
        Return the trainer class (not instantiated).
        """
        key = self._registry_key(
            trainer_name=trainer_name,
            framework=framework,
            use_case=use_case
        )
        if key not in self._registry_dict:
            raise KeyError(
                f"Trainer {trainer_name} for use_case {use_case} with framework {framework} not found."
            )
        return self._registry_dict[key]

# ---------------------------
# Global registry instance
TRAINER_WRAPPER_REGISTRY = TrainerRegistry()
