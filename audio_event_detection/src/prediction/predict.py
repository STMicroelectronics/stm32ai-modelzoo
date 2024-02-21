# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from pathlib import Path
from omegaconf import DictConfig
from tabulate import tabulate
import numpy as np
import tensorflow as tf

import warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../preprocessing'))
sys.path.append(os.path.abspath('../evaluation'))

from preprocess import preprocess_input
from data_loader import _load_audio_sample
from evaluate import _aggregate_predictions

def predict(cfg: DictConfig = None) -> None:
    """
    Predicts a class for all the audio files that are inside a given directory.
    The model used for the predictions can be either a .h5 or .tflite file.

    Args:
        cfg (dict): A dictionary containing the entire configuration file.

    Returns:
        None
    
    Errors:
        The directory containing the files cannot be found.
        The directory does not contain any file.
        No audio files can be loaded.
    """
    
    model_path = cfg.general.model_path
    class_names = cfg.dataset.class_names
    test_files_dir = cfg.prediction.test_files_path
    # _, model_input_shape = get_model_name_and_its_input_shape(model_path)
    
    # Preproc and feature extraction parameters
    patch_length = cfg.feature_extraction.patch_length
    n_mels = cfg.feature_extraction.n_mels
    target_rate = cfg.preprocessing.target_rate
    overlap = cfg.feature_extraction.overlap
    n_fft = cfg.feature_extraction.n_fft
    spec_hop_length = cfg.feature_extraction.hop_length
    min_length = cfg.preprocessing.min_length
    max_length = cfg.preprocessing.max_length
    top_db = cfg.preprocessing.top_db
    frame_length = cfg.preprocessing.frame_length
    hop_length = cfg.preprocessing.hop_length
    trim_last_second = cfg.preprocessing.trim_last_second
    include_last_patch = cfg.feature_extraction.include_last_patch
    win_length = cfg.feature_extraction.window_length
    window = cfg.feature_extraction.window
    center = cfg.feature_extraction.center
    pad_mode = cfg.feature_extraction.pad_mode
    power = cfg.feature_extraction.power
    fmin = cfg.feature_extraction.fmin
    fmax = cfg.feature_extraction.fmax
    power_to_db_ref = np.max
    norm = cfg.feature_extraction.norm
    if norm == "None":
        norm = None
    htk = cfg.feature_extraction.htk
    to_db = cfg.feature_extraction.to_db

    expand_last_dim = cfg.dataset.expand_last_dim
    multi_label = cfg.dataset.multi_label

    print("[INFO] Making predictions using:")
    print("  model:", model_path)
    print("  files directory:", test_files_dir)
    # Sort classes alphabetically
    class_names = sorted(class_names)
    print("[INFO] : Class names sorted alphabetically. \n \
           If the model you are using has been trained using the model zoo, \n \
           there will be no issue. Otherwise, the predicted class' name might not correspond to the \n \
           predicted one-hot vector.")
    print(f"Class names : {class_names}")
    # Load the test images
    filenames = []
    X = []
    clip_labels = []
    for i, fn in enumerate(os.listdir(test_files_dir)):
        filepath = os.path.join(test_files_dir, fn)
        # Skip subdirectories if any
        if os.path.isdir(filepath): continue
        filenames.append(fn)
        # Load the audio sample and split into patches
        patches = _load_audio_sample(
            filepath=filepath,
            patch_length=patch_length,
            n_mels=n_mels,
            target_rate=target_rate,
            overlap=overlap,
            n_fft=n_fft,
            spec_hop_length=spec_hop_length,
            min_length=min_length,
            max_length=max_length,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length,
            trim_last_second=trim_last_second,
            include_last_patch=include_last_patch,
            win_length=win_length,
            window=window,
            center=center,
            pad_mode=pad_mode,
            power=power,
            fmin=fmin,
            fmax=fmax,
            power_to_db_ref=power_to_db_ref,
            norm=norm,
            htk=htk,
            to_db=to_db)
    
        X.extend(patches)
        clip_labels.extend([i] * len(patches))
    
    if not filenames:
        raise ValueError("Unable to make predictions, could not find any audio file in the "
                         f"files directory.\nReceived directory path {test_files_dir}")
    # Concatenate X into a single array
    X = np.stack(X, axis=0)
    if expand_last_dim:
        X = np.expand_dims(X, axis=-1)
    # Convert clip labels into array this is critical
    clip_labels = np.array(clip_labels)


    results_table = []
    file_extension = Path(model_path).suffix
    if file_extension == ".h5":
        # Load the .h5 model
        model = tf.keras.models.load_model(model_path)
        
        # Get results
        preds = model.predict(X)
        aggregated_probas = _aggregate_predictions(preds,
                                                  clip_labels=clip_labels,
                                                  multi_label=multi_label,
                                                  is_truth=False,
                                                  return_proba=True)
        aggregated_preds = _aggregate_predictions(preds,
                                                  clip_labels=clip_labels,
                                                  multi_label=multi_label,
                                                  is_truth=False,
                                                  return_proba=False)
        # Add result to the table
        for i in range(aggregated_preds.shape[0]):
            results_table.append([class_names[np.argmax(aggregated_preds[i])],
                                  aggregated_preds[i],
                                  aggregated_probas[i].round(decimals=2),
                                  filenames[i]])

    elif file_extension == ".tflite":
        # Load the Tflite model and allocate tensors
        interpreter_quant = tf.lite.Interpreter(model_path=model_path)
        input_details = interpreter_quant.get_input_details()[0]
        input_index_quant = input_details["index"]
        output_index_quant = interpreter_quant.get_output_details()[0]["index"]

        interpreter_quant.resize_tensor_input(input_index_quant, X.shape)
        interpreter_quant.allocate_tensors()

        patches_processed = preprocess_input(X, input_details)
        interpreter_quant.set_tensor(input_index_quant, patches_processed)
        interpreter_quant.invoke()
        preds = interpreter_quant.get_tensor(output_index_quant)

        aggregated_probas = _aggregate_predictions(preds,
                                                  clip_labels=clip_labels,
                                                  multi_label=multi_label,
                                                  is_truth=False,
                                                  return_proba=True)
        aggregated_preds = _aggregate_predictions(preds,
                                                  clip_labels=clip_labels,
                                                  multi_label=multi_label,
                                                  is_truth=False,
                                                  return_proba=False)
        # Add result to the table
        for i in range(aggregated_preds.shape[0]):
            results_table.append([class_names[np.argmax(aggregated_preds[i])],
                                  aggregated_preds[i],
                                  aggregated_probas[i].round(decimals=2),
                                  filenames[i]])

    else:
        raise TypeError(f"Unknown or unsupported model type. Received path {model_path}")

    # Display the results table
    print(tabulate(results_table, headers=["Prediction", "One-hot prediction", "Score", "Audio file"]))
