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


class DatasetWrapperRegistry(Registry):
    """
    Specialized registry for dataset wrapper classes.

    Each entry is uniquely identified by:
        (dataset_name, use_case, framework)

    This registry is useful for dynamically associating datasets with their
    wrappers, enabling retrieval based on dataset name, the use case it serves,
    and the ML framework it targets.
    """

    def __init__(self):
        """Initialize the dataset wrapper registry with an internal key structure."""
        super().__init__()
        self._use_case_map = {}
        self._registry_key = namedtuple(
            'RegistryKey', ['dataset_name', 'use_case', 'framework']
        )

    def register(self, dataset_name, use_case, framework):
        """
        Decorator to register a dataset wrapper.

        Args:
            dataset_name (str): The name of the dataset (e.g., 'COCO', 'imagenet').
            use_case (str): The use case for which this dataset is intended 
                            (e.g., 'image_classification', 'object_detection').
            framework (str): The ML framework this dataset wrapper supports 
                             (e.g., 'Torch', 'TensorFlow').

        Returns:
            function: A decorator that registers the dataset wrapper.

        Raises:
            KeyError: If the dataset key is already registered.
        """
        def _register(obj_name, obj):
            if obj_name in self._registry_dict:
                raise KeyError(
                    f'{obj_name} is already registered in the dataset registry'
                )
            self._registry_dict[obj_name] = obj

        def wrap(obj):
            cls_name = dataset_name if dataset_name is not None else obj.__name__
            cls_name = self._registry_key(
                dataset_name=cls_name, use_case=use_case, framework=framework
            )
            _register(cls_name, obj)
            return obj

        return wrap

    def get(self, dataset_name, use_case, framework):
        """
        Retrieve a registered dataset wrapper.

        Args:
            dataset_name (str): The dataset name to retrieve.
            use_case (str): The use case associated with the dataset.
            framework (str): The ML framework for the dataset wrapper.

        Returns:
            object: The registered dataset wrapper object.

        Raises:
            KeyError: If no dataset wrapper matches the given parameters.
        """
        key = self._registry_key(
            dataset_name=dataset_name, use_case=use_case, framework=framework
        )
        if key not in self._registry_dict:
            registered_dataset_names = [key.dataset_name for key in self.registry_dict]
            raise KeyError(
                f'Dataset {dataset_name} was not found in the dataset registry. '
                f'Registered datasets: {registered_dataset_names}'
            )
        return self._registry_dict[key]


DATASET_WRAPPER_REGISTRY = DatasetWrapperRegistry()
