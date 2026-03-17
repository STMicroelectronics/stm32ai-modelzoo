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


class QuantizerRegistry(Registry):
    """
    Registry for quantizer classes.

    Each entry is uniquely identified by a tuple:
        (quantizer_name, framework, use_case)

    Quantizers should accept: dataloader, model, cfg
    """

    def __init__(self):
        super().__init__()
        self._registry_key = namedtuple(
            'QuantizerKey', ['quantizer_name', 'framework', 'use_case']
        )

    def register(self, quantizer_name, framework, use_case):
        """
        Decorator to register a quantizer class.
        """
        def wrap(cls):
            key = self._registry_key(
                quantizer_name=quantizer_name or cls.__name__,
                framework=framework,
                use_case=use_case
            )
            if key in self._registry_dict:
                raise KeyError(f"Quantizer {key} is already registered.")
            self._registry_dict[key] = cls
            return cls
        return wrap

    def get(self, quantizer_name, framework, use_case):
        """
        Return the quantizer class (not instantiated).
        """
        key = self._registry_key(
            quantizer_name=quantizer_name,
            framework=framework,
            use_case=use_case
        )
        if key not in self._registry_dict:
            raise KeyError(
                f"Quantizer {quantizer_name} for use_case {use_case} with framework {framework} not found."
            )
        return self._registry_dict[key]

# ---------------------------
# Global registry instance
QUANTIZER_WRAPPER_REGISTRY = QuantizerRegistry()
