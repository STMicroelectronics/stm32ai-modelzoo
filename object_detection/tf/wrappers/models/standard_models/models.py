# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from common.registries.model_registry import MODEL_WRAPPER_REGISTRY
from object_detection.tf.src.models import *



TF_MODEL_FNS = {
 'yolov2t': (get_yolov2t, {}),}



def register_tf_model_wrapper(model_fn, model_name, **model_init_kwargs):
    """
    Register a TensorFlow model wrapper in the global registry.

    Args:
        model_fn (callable): The model-building function.
        model_name (str): Name to register the model under.
        **model_init_kwargs: Static keyword arguments for the model_fn.

    Returns:
        function: The registered build_model_fn function.
    """
    def build_model_fn(cfg):
        """
        Build and return the model instance for the registry.

        Args:
            cfg (dict): top level config

        Returns:
            keras.Model: The constructed model.
        """
        model_kwargs = prepare_kwargs_for_model(cfg)
        merged_kwargs = {**model_kwargs, **model_init_kwargs}
        return model_fn( **merged_kwargs)
    # Register the model in the global registry
    build_model_fn = MODEL_WRAPPER_REGISTRY.register(
        framework='tf',
        model_name=model_name,
        use_case='object_detection',
    )(build_model_fn)
    # Set a unique function name for clarity
    build_model_fn.__name__ = f'{model_name}_tf'
    return build_model_fn

# Register all models defined in TF_MODEL_FNS
for _model_name, (_model_fn, _model_kwargs) in TF_MODEL_FNS.items():
    wrapper_fn = register_tf_model_wrapper(_model_fn, _model_name, **_model_kwargs)
    # Expose the wrapper in the module's global namespace
    globals()[wrapper_fn.__name__] = wrapper_fn
