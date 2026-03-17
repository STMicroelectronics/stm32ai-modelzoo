# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
class Registry:
    """
    A simple registry to store and retrieve objects (e.g., classes, functions) by name.

    This is useful for dynamically registering implementations or components
    so they can be retrieved later by string identifiers instead of hardcoding imports.

    Attributes:
        _registry_dict (dict): Internal mapping from registered names to objects.
        _name (str): Optional name for the registry (used in error messages).
        _error_on_same_key (bool): Whether to raise an error if registering an existing key.
    """

    def __init__(self, name=None, error_on_same_key=True):
        """
        Initialize the registry.

        Args:
            name (str, optional): Name of the registry. Defaults to ''.
            error_on_same_key (bool, optional): Whether to raise an error when attempting 
                                                to register the same key twice. Defaults to True.
        """
        self._registry_dict = {}
        self._name = name if name is not None else ''
        self._error_on_same_key = error_on_same_key

    def register(self, name=None, **kwargs):
        """
        Decorator to register an object (e.g., class or function) in the registry.

        Args:
            name (str, optional): Custom name for the registered object.
                                  Defaults to the object's __name__ attribute.
            **kwargs: Additional parameters that will be part of the registry key tuple.

        Returns:
            function: A decorator that registers the object and returns it unchanged.

        Raises:
            KeyError: If the key already exists in the registry (and error_on_same_key=True).
        """
        def _register(obj_name, obj):
            if self._error_on_same_key and obj_name in self._registry_dict:
                raise KeyError(f'{obj_name} is already registered')
            self._registry_dict[obj_name] = obj

        def wrap(obj):
            cls_name = name
            if cls_name is None:
                cls_name = obj.__name__
            if kwargs:
                cls_name = (cls_name, *kwargs)
            _register(cls_name, obj)
            return obj

        return wrap

    def get(self, name):
        """
        Retrieve a registered object by name.

        Args:
            name (str or tuple): The key under which the object was registered.

        Returns:
            object: The registered object.

        Raises:
            KeyError: If the key is not found in the registry.
        """
        if name not in self._registry_dict:
            raise KeyError(f'{name} was not found in the {self._name} registry')
        return self._registry_dict[name]

    @property
    def registry_dict(self):
        """dict: The internal dictionary mapping names to registered objects."""
        return self._registry_dict

    @property
    def name(self):
        """str: The name of the registry."""
        return self._name

    def __add__(self, other_registry):
        """
        Merge this registry with another Registry object.

        Args:
            other_registry (Registry): Another registry instance to merge with.

        Returns:
            Registry: A new registry containing entries from both registries.

        Raises:
            ValueError: If both registries contain the same key.
        """
        res = type(self)(self._name)
        if self._registry_dict.keys() & other_registry.registry_dict.keys():
            raise ValueError('Trying to add two registries with overlapping keys')
        res._registry_dict.update(self._registry_dict)
        res._registry_dict.update(other_registry.registry_dict)
        return res
