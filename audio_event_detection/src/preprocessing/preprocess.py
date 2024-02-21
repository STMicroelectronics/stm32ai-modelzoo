# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from omegaconf import DictConfig
from tensorflow import keras
import os
from re import A
import numpy as np
import tensorflow as tf
from typing import Tuple
# from tensorflow.keras import layers # Don't think this one is needed
from data_loader import load_dataset

def preprocess(cfg: DictConfig = None) -> tuple: # OK
    """
    Preprocesses the data based on the provided configuration.

    Args:
        cfg (DictConfig): Configuration object containing the settings.

    Returns:
        tuple: A tuple containing the following:
            - train_ds (object): Training dataset.
            - valid_ds (object): Validation dataset.
            - val_clip_labels : np.ndarray, Clip labels associated to the validation dataset
            - quantization_ds (object) : Quantization dataset
            - test_ds (object) : Test dataset
            - test_clip_labels : np.ndarray, Clip labels associated to the test dataset
    """

    # Check for batch size both in training & general section
    # Have to do nested ifs again unfortunately
    if cfg.training:
        if cfg.training.batch_size:
            batch_size = cfg.training.batch_size
    elif cfg.general.batch_size:
        batch_size = cfg.general.batch_size
    else:
        batch_size = 32

    # Check if we have a dataset-specific section
    if cfg.dataset_specific:
        train_ds, val_ds, val_clip_labels, quantization_ds, test_ds, test_clip_labels = load_dataset(
            dataset_name=cfg.dataset.name,
            training_csv_path=cfg.dataset.training_csv_path,
            training_audio_path=cfg.dataset.training_audio_path,
            validation_csv_path=cfg.dataset.validation_csv_path,
            validation_audio_path=cfg.dataset.validation_audio_path,
            validation_split=cfg.dataset.validation_split,
            quantization_csv_path=cfg.dataset.quantization_csv_path,
            quantization_audio_path=cfg.dataset.quantization_audio_path,
            test_csv_path=cfg.dataset.test_csv_path,
            test_audio_path=cfg.dataset.test_audio_path,
            class_names=cfg.dataset.class_names,
            patch_length=cfg.feature_extraction.patch_length,
            n_mels=cfg.feature_extraction.n_mels,
            target_rate=cfg.preprocessing.target_rate,
            overlap=cfg.feature_extraction.overlap,
            n_fft=cfg.feature_extraction.n_fft,
            spec_hop_length=cfg.feature_extraction.hop_length,
            min_length=cfg.preprocessing.min_length, 
            max_length=cfg.preprocessing.max_length, 
            top_db=cfg.preprocessing.top_db,
            frame_length=cfg.preprocessing.frame_length,
            hop_length=cfg.preprocessing.hop_length,
            trim_last_second=cfg.preprocessing.trim_last_second,
            include_last_patch=cfg.feature_extraction.include_last_patch,
            win_length=cfg.feature_extraction.window_length,
            window=cfg.feature_extraction.window,
            center=cfg.feature_extraction.center,
            pad_mode=cfg.feature_extraction.pad_mode,
            power=cfg.feature_extraction.power,
            fmin=cfg.feature_extraction.fmin,
            fmax=cfg.feature_extraction.fmax,
            power_to_db_ref=np.max, # Might let the user choose this param later
            norm=cfg.feature_extraction.norm,
            htk=cfg.feature_extraction.htk,
            to_db=cfg.feature_extraction.to_db,
            use_garbage_class=cfg.dataset.use_garbage_class,
            n_samples_per_garbage_class=cfg.dataset.n_samples_per_garbage_class,
            expand_last_dim=cfg.dataset.expand_last_dim,
            file_extension=cfg.dataset.file_extension,
            batch_size=batch_size,
            to_cache=cfg.dataset.to_cache,
            shuffle=cfg.dataset.shuffle,
            seed=cfg.dataset.seed,
            fsd50k_dev_audio_folder=cfg.dataset_specific.fsd50k.dev_audio_folder,
            fsd50k_eval_audio_folder=cfg.dataset_specific.fsd50k.eval_audio_folder,
            fsd50k_csv_folder=cfg.dataset_specific.fsd50k.csv_folder,
            fsd50k_audioset_ontology_path=cfg.dataset_specific.fsd50k.audioset_ontology_path,
            fsd50k_keep_only_monolabel=cfg.dataset_specific.fsd50k.only_keep_monolabel,
            )
    else:
        train_ds, val_ds, val_clip_labels, quantization_ds, test_ds, test_clip_labels = load_dataset(
            dataset_name=cfg.dataset.name,
            training_csv_path=cfg.dataset.training_csv_path,
            training_audio_path=cfg.dataset.training_audio_path,
            validation_csv_path=cfg.dataset.validation_csv_path,
            validation_audio_path=cfg.dataset.validation_audio_path,
            validation_split=cfg.dataset.validation_split,
            quantization_csv_path=cfg.dataset.quantization_csv_path,
            quantization_audio_path=cfg.dataset.quantization_audio_path,
            test_csv_path=cfg.dataset.test_csv_path,
            test_audio_path=cfg.dataset.test_audio_path,
            class_names=cfg.dataset.class_names,
            patch_length=cfg.feature_extraction.patch_length,
            n_mels=cfg.feature_extraction.n_mels,
            target_rate=cfg.preprocessing.target_rate,
            overlap=cfg.feature_extraction.overlap,
            n_fft=cfg.feature_extraction.n_fft,
            spec_hop_length=cfg.feature_extraction.hop_length,
            min_length=cfg.preprocessing.min_length, 
            max_length=cfg.preprocessing.max_length, 
            top_db=cfg.preprocessing.top_db,
            frame_length=cfg.preprocessing.frame_length,
            hop_length=cfg.preprocessing.hop_length,
            trim_last_second=cfg.preprocessing.trim_last_second,
            include_last_patch=cfg.feature_extraction.include_last_patch,
            win_length=cfg.feature_extraction.window_length,
            window=cfg.feature_extraction.window,
            center=cfg.feature_extraction.center,
            pad_mode=cfg.feature_extraction.pad_mode,
            power=cfg.feature_extraction.power,
            fmin=cfg.feature_extraction.fmin,
            fmax=cfg.feature_extraction.fmax,
            power_to_db_ref=np.max, # Might let the user choose this param later
            norm=cfg.feature_extraction.norm,
            htk=cfg.feature_extraction.htk,
            to_db=cfg.feature_extraction.to_db,
            use_garbage_class=cfg.dataset.use_garbage_class,
            n_samples_per_garbage_class=cfg.dataset.n_samples_per_garbage_class,
            expand_last_dim=cfg.dataset.expand_last_dim,
            file_extension=cfg.dataset.file_extension,
            batch_size=batch_size,
            to_cache=cfg.dataset.to_cache,
            shuffle=cfg.dataset.shuffle,
            seed=cfg.dataset.seed
        )

    return train_ds, val_ds, val_clip_labels, quantization_ds, test_ds, test_clip_labels

def preprocess_input(patch: np.ndarray, input_details: dict) -> tf.Tensor: # OK
    """
    Quantizes a patch according to input details.

    Args:
        patch : Input patch as a NumPy array.
        input_details: Dictionary containing input details, including quantization and dtype.

    Returns:
        Quantized patch as a TensorFlow tensor.
    """
    if input_details['dtype'] in [np.uint8, np.int8]:
        patch_processed = (patch / input_details['quantization'][0]) + input_details['quantization'][1]
        patch_processed = np.clip(np.round(patch_processed), np.iinfo(input_details['dtype']).min,
                                  np.iinfo(input_details['dtype']).max)
    else:
        # I would use an actual warning here but they are silenced in the main scripts...
        print("[WARNING] : Quantization dtype isn't one of 'int8', 'uint8'. \n \
               Input patches have not been quantized, this may lead to wrong results.")
        patch_processed = patch
    patch_processed = tf.cast(patch_processed, dtype=input_details['dtype'])
    # Should not need this since we are batching
    # patch_processed = tf.expand_dims(patch_processed, 0)

    return patch_processed


def postprocess_output(output: np.ndarray,
                       multi_label: bool = None,
                       multilabel_threshold: float = 0.5) -> np.ndarray: # OK
    """
    Postprocesses the model output to obtain the predicted label.

    Args:
        output (np.ndarray): The output tensor from the model.

    Returns:
        predicted_label : np.ndarray, the predicted label.
    """
    if not multi_label:
        predicted_label = np.argmax(output, axis=1)
    else:
        predicted_label = np.where(output < multilabel_threshold, 0, 1)

    return predicted_label
