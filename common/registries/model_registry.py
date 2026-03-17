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


class ModelWrapperRegistry(Registry):
    """
    Specialized registry for model wrapper classes.

    Each entry is uniquely identified by a tuple of:
        (model_name, dataset_name, use_case, framework)

    Additionally, it stores:
        - A mapping of keys to their use case.
        - A list of pretrained models available in the registry.

    Attributes:
        _use_case_map (dict): Maps registry keys to use cases.
        _registry_key (namedtuple): Defines the key fields for the registry.
        _registry_pretrained_models (dict): Maps keys to pretrained model objects.
    """

    def __init__(self):
        """Initialize the model wrapper registry with internal mappings."""
        super().__init__()
        self._use_case_map = {}
        self._registry_key = namedtuple(
            'RegistryKey', ['model_name', 'use_case', 'framework']
        )
        self._registry_pretrained_models = {}

    @property
    def use_case_map(self):
        """dict: Mapping of registered models to their use cases."""
        return self._use_case_map

    @property
    def pretrained_models(self):
        """dict: Mapping of registered keys to pretrained model objects."""
        return self._registry_pretrained_models

    def register(self, model_name, use_case, framework, has_checkpoint=True):
        """
        Decorator to register a model wrapper.

        Args:
            model_name (str): Name of the model architecture.
            #dataset_name (str): Name of the dataset.
            use_case (str): The use case for the model (e.g., image_classification, object_detection).
            framework (str): ML framework used (e.g., Torch, TensorFlow).
            has_checkpoint (bool): Whether this model has an available pretrained checkpoint.

        Returns:
            function: Decorator that registers the object.

        Raises:
            KeyError: If the key is already registered.
        """
        def _register(obj_name, obj, use_case):
            if obj_name in self._registry_dict:
                raise KeyError(
                    f'{obj_name} is already registered in the model wrapper registry'
                )
            self._registry_dict[obj_name] = obj
            if has_checkpoint:
                self._registry_pretrained_models[obj_name] = obj
            self._use_case_map[obj_name] = use_case

        def wrap(obj):
            cls_name = model_name if model_name is not None else obj.__name__
            cls_name = self._registry_key(
                model_name=cls_name,
                use_case=use_case, framework=framework
            )
            _register(cls_name, obj, use_case)
            return obj

        return wrap

    def get(self, model_name, use_case, framework):
        """
        Retrieve a registered model wrapper.

        Args:
            model_name (str): Name of the model.
            #dataset_name (str): Name of the dataset.
            use_case (str): The use case for the model.
            framework (str): The ML framework used.

        Returns:
            object: The registered model wrapper.

        Raises:
            KeyError: If the model is not found.
        """
        key = self._registry_key(
            model_name=model_name,
            use_case=use_case, framework=framework
        )
        if key not in self._registry_dict:
            raise KeyError(
                f'Model {model_name} on use_case {use_case} '
                f'on framework {framework} was not found in the model wrapper registry'
            )
        return self._registry_dict[key]

    # def get_use_case(self, model_name):
    #     """
    #     Retrieve the use case for a given model and dataset.

    #     Note:
    #         This method may remap some dataset names to generic formats internally.

    #     Args:
    #         model_name (str): Name of the model.

    #     Returns:
    #         str: The use case associated with the model and dataset.

    #     Raises:
    #         KeyError: If no entry matches the given model and dataset.
    #     """
    #     GENERIC_DATASET_USE_CASE_MAP = {
    #         'voc_format_dataset': 'voc',
    #     }
    #     if dataset_name in GENERIC_DATASET_USE_CASE_MAP:
    #         dataset_name = GENERIC_DATASET_USE_CASE_MAP.get(dataset_name)
    #     key = self._registry_key(model_name=model_name, dataset_name=dataset_name)
    #     if key not in self._registry_dict:
    #         raise KeyError(
    #             f'Model {model_name} on dataset {dataset_name} was not found '
    #             'in the model wrapper registry'
    #         )
    #     return self._use_case_map[key]


# class EvaluatorWrapperRegistry(Registry):
#     """
#     Specialized registry for evaluator wrapper classes.

#     Each entry is uniquely identified by:
#         (dataset_type, model_type, use_case)

#     This allows for flexible retrieval of evaluators for different combinations
#     of models, datasets, and use cases.
#     """

#     def __init__(self):
#         """Initialize the evaluator wrapper registry with a key structure."""
#         super().__init__()
#         self._use_case_map = {}
#         self._registry_key = namedtuple(
#             'RegistryKey', ['dataset_type', 'model_type', 'use_case']
#         )

#     def register(self, use_case, model_type=None, dataset_type=None):
#         """
#         Decorator to register an evaluator wrapper.

#         Args:
#             use_case (str): The use case for the evaluator (e.g., classification, detection).
#             model_type (str, optional): Type of model the evaluator supports.
#             dataset_type (str, optional): Type of dataset the evaluator supports.

#         Returns:
#             function: Decorator that registers the object.

#         Raises:
#             KeyError: If the key is already registered.
#         """
#         def _register(obj_name, obj):
#             if obj_name in self._registry_dict:
#                 raise KeyError(
#                     f'{obj_name} is already registered in the evaluator wrapper registry'
#                 )
#             self._registry_dict[obj_name] = obj

#         def wrap(obj):
#             cls_name = use_case if use_case is not None else obj.__name__
#             cls_name = self._registry_key(
#                 use_case=cls_name, model_type=model_type, dataset_type=dataset_type
#             )
#             _register(cls_name, obj)
#             return obj

#         return wrap

#     def get(self, use_case, model_name, dataset_name):
#         """
#         Retrieve a registered evaluator wrapper.

#         The retrieval logic tries multiple fallback key patterns:
#         1. Exact match (use_case, dataset_type, model_type)
#         2. Fallback with dataset_type=None
#         3. Fallback with model_type=None and dataset_type=None

#         Args:
#             use_case (str): The use case for the evaluator.
#             model_name (str): Model type.
#             dataset_name (str): Dataset type.

#         Returns:
#             object: The registered evaluator wrapper.

#         Raises:
#             KeyError: If no matching evaluator is found.
#         """
#         key = self._registry_key(
#             use_case=use_case, dataset_type=dataset_name, model_type=model_name
#         )
#         if key not in self._registry_dict:
#             key = self._registry_key(
#                 use_case=use_case, model_type=model_name, dataset_type=None
#             )
#         if key not in self._registry_dict:
#             key = self._registry_key(
#                 use_case=use_case, model_type=None, dataset_type=None
#             )

#         if key not in self._registry_dict:
#             raise KeyError(
#                 f'{use_case} model {model_name} on dataset {dataset_name} was not found '
#                 'in the evaluator wrapper registry'
#             )

#         return self._registry_dict[key]


# class RegistryStorage:
#     """
#     Stores and manages multiple registry instances.

#     Ensures that registry names are unique within the storage.
#     Allows retrieval of a registry by its name.
#     """

#     def __init__(self, registry_list):
#         """
#         Initialize registry storage.

#         Args:
#             registry_list (list): A list of Registry objects.

#         Raises:
#             RuntimeError: If more than one registry with the same name is found.
#         """
#         regs = [r for r in registry_list if isinstance(r, Registry)]
#         self.registries = {}
#         for r in regs:
#             if r.name in self.registries:
#                 raise RuntimeError(
#                     f'There are more than one registry with the name "{r.name}"'
#                 )
#             self.registries[r.name] = r

#     def get(self, registry_name: str) -> Registry:
#         """
#         Retrieve a registry by name.

#         Args:
#             registry_name (str): Name of the registry.

#         Returns:
#             Registry: The matching registry object.

#         Raises:
#             RuntimeError: If no registry with the given name exists.
#         """
#         if registry_name not in self.registries:
#             raise RuntimeError(
#                 f'Cannot find registry with registry_name "{registry_name}"'
#             )
#         return self.registries[registry_name]


MODEL_WRAPPER_REGISTRY = ModelWrapperRegistry()

