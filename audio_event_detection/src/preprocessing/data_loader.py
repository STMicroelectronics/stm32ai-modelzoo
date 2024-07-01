# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from tensorflow import keras
import os
import pickle
from re import A
import scipy.io
import numpy as np
import tensorflow as tf
import pandas as pd
from math import ceil
from typing import Tuple, List
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from pathlib import Path

from time_domain_preprocessing import load_and_reformat
from feature_extraction import get_patches
from dataset_utils.fsd50k.unsmear_labels import unsmear_labels, make_model_zoo_compatible


def _load_audio_sample(filepath,
                       patch_length: int,
                       n_mels: int,
                       target_rate: int,
                       overlap: float,
                       n_fft: int,
                       spec_hop_length: int,
                       min_length: int = 1, 
                       max_length: int = 10, 
                       top_db: int = 30,
                       frame_length: int = 2048,
                       hop_length: int = 512,
                       trim_last_second: bool = False,
                       include_last_patch: bool = False,
                       win_length: int = None,
                       window: str = 'hann',
                       center: bool = True,
                       pad_mode: bool = 'constant',
                       power: float = 2.0,
                       fmin: int = 20,
                       fmax: int = 20000,
                       power_to_db_ref = np.max,
                       norm: str = "slaney",
                       htk: bool = False,
                       to_db: bool = True,
                       **kwargs
                       ):
    '''Internal utility to load an audio sample

    Inputs
    -------
    filepath : str or PosixPath, path to waveform file
    patch_length : int, number of spectrogram frames per patch.
                    Note that the length is specified in frames, e.g. if each frame in 
                    the spectrogram represents 50 ms, a patch of 1s would need 20 frames. 
    n_mels : int, number of mel bands. passed to librosa.feature.melspectrogram
    target_rate : int, Sample rate of output waveform
    overlap : float between 0 and 1.0, proportion of overlap between consecutive spectrograms.
        For example, with an overlap of 0.25 and a patch length of 20, 
        patch number n would share its 5 first frames with patch (n-1),
        and its 5 last frames with patch (n+1). 
    n_fft : int, length of FFT, passed to librosa.feature.melspectrogram
    spec_hop_length : int, hop length between windows, passed to librosa.feature.melspectrogram
    min_length : int,  Minimum length of output waveform in seconds. 
        If input waveform is below this duration, it will be repeated to reach min_length.
    max_length : int, Maximum length of output waveform in seconds.
        If input waveform is longer, it will be cut from the end.

    top_db : int, Passed to librosa.split. Frames below -top_db will be considered as silence and cut.
        Higher values induce more tolerance to silence.
    frame_length : int, frame length used for silence removal
    hop_length : int, hop length used for silence removal
    trim_last_second : bool. Set to True to cut the output waveform to an integer number of seconds.
        For example, if the output waveform is 7s and 350 ms long, this option will cut the last 350 ms.
    include_last_patch : bool. If set to False, the last spectrogram frames 
        will be discarded if they are not enough to build a new patch with.
        If set to True, they will be kept in a new patch which will more heavily overlap with the previous one.
        For example, with a patch length of 20 frames, and overlap of 0.25 (thus 5 frames),
        and an overall clip length of 127 frames, the last 7 frames would not be enough to build a new patch,
        since we'd need 20 - 5 = 15 new frames. If include_last_patch is set to False,
        these last 7 frames will be discarded. If it is set to True, 
        they will be included in a new patch along with the 13 previous frames.

    win_length : int, STFT window length, passed to librosa.feature.melspectrogram. If None default to n_fft
    window : str, window type, passed to librosa.feature.melspectrogram
    center : bool, set to True to center frames, passed to librosa.feature.melspectrogram 
    pad_mode : str, padding type, passed to librosa.feature.melspectrogram
    power : float, 1.0 or 2.0 only are allowed. Set to 2.O for power melspectrogram, 
        and 1.0 for amplitude melspectrogram

    fmin : int, min freq of spectrogram, passed to librosa.feature.melspectrogram
    fmax : int, max freq of spectrogram, passed to librosa.feature.melspectrogram
    power_to_db_ref, : func, reference used to convert linear scale mel spectrogram to db scale. 
            Passed to passed to librosa.power_to_db or librosa.amplitude_to_db
    norm : str, normalization used for triangular mel weights. Passer to librosa.feature.melspectrogram
    Defaults to "slaney", in which case the triangular mel weights are divided by the width of the mel band.
    htk : bool, if True use the HTK formula to compute mel weights, else use Slaney's.
            Passed to librosa.feature.melspectrogram
    to_db : bool, if True convert the output spectrogram to decibel scale.
            if False we just take log(spec + 1e-4)
    Outputs
    -------
    Patches : list of 2D ndarrays of shape (n_mels, patch_length). 
    List of patches extracted from input audio
    
    '''
    # Hate having to do this
    # And now I shouldn't have to anymore !
    # if norm == "None":
    #    norm = None
    wave, sr = load_and_reformat(
        wave_path=filepath,
        min_length=min_length,
        max_length=max_length,
        target_rate=target_rate,
        top_db=top_db,
        frame_length=frame_length,
        hop_length=hop_length,
        trim_last_second=trim_last_second)
        
    patches = get_patches(
        wave=wave,
        sr=sr,
        patch_length=patch_length,
        overlap=overlap,
        n_fft=n_fft,
        hop_length=spec_hop_length,
        include_last_patch=include_last_patch,
        win_length=win_length,
        window=window,
        center=center,
        pad_mode=pad_mode,
        power=power,
        n_mels=n_mels,
        fmin=fmin,
        fmax=fmax,
        power_to_db_ref=power_to_db_ref,
        norm=norm,
        htk=htk,
        to_db=to_db,
        **kwargs)

    return patches

def _add_garbage_class_to_df(dataframe: pd.DataFrame,
                             classes_to_keep: List[str] = None,
                             n_samples_per_other_class: int = 2,
                             seed: int = 42,
                             shuffle: bool = True):
    '''
    Takes a dataframe, a list of classes, subsamples classes not in said list, 
    and changes their label to "other".
    NOTE : We expect the labels to be in a column named "category" (ESC format)
    
    Inputs
    ------
    dataframe : Pandas Dataframe. Initial dataframe.
    classes_to_keep : list of str. List of classes which should not
        be subsampled and have their label changed
    n_samples_per_other_class : int. How many samples of each class 
        NOT in classes_to_keep to keep after filtering.
    seed : int or numpy RandomGenerator : Seed for the random subsampling
    shuffle : bool. Set to true to shuffle the output dataframe. 
        If set to False, all the "other" samples will be at the bottom of the output dataframe.

    Outputs
    -------
    kept_samples : Pandas Dataframe. Dataframe which contains all samples of the classes
        in classes_to_keep, and the specified number of samples for the other classes.
        These samples have their labels changed to "other"
    '''
    # Determine which classes should be treated as "other" (i.e. ood classes)
    other_classes = set(dataframe['category'].unique()).difference(set(classes_to_keep))
    # Start by keeping samples of ind classes
    kept_samples = dataframe[dataframe['category'].isin(classes_to_keep)]
    # Keep only a certain amount of samples per ood class, 
    # and concatenate with the previous dataframe
    for ood_class in other_classes:
        sample = dataframe[dataframe['category'] == ood_class].sample(n=n_samples_per_other_class,
                                                                      random_state=seed,
                                                                      replace=True)
        # We don't check for duplicates because it slows stuff down 
        # and this should not introduce duplicates anyways
        kept_samples = pd.concat([kept_samples, sample], axis=0)

    # Finally, update the category column with the "other" label for anything not in
    # classes_to_keep.
    replacer = lambda s : "other" if (s in other_classes) else s
    kept_samples['category'] = kept_samples['category'].apply(replacer)

    if shuffle:
        kept_samples = kept_samples.sample(frac=1)

    return kept_samples

def _get_ds(df: pd.DataFrame,
            audio_path: str,
            used_classes: List[str],
            patch_length: int,
            n_mels: int,
            target_rate: int,
            overlap: float,
            n_fft: int,
            spec_hop_length: int,
            min_length: int, 
            max_length: int, 
            top_db: int,
            frame_length: int,
            hop_length: int,
            trim_last_second: bool,
            include_last_patch: bool,
            win_length: int,
            window: str,
            center: bool,
            power: float,
            fmin: int,
            fmax: int,
            norm: str,
            htk: bool,
            to_db: bool,
            use_garbage_class: bool,
            file_extension: str,
            batch_size: int,
            to_cache: bool,
            shuffle: bool, 
            return_clip_labels: bool,
            return_arrays: bool,
            power_to_db_ref = np.max,
            pad_mode: bool = 'constant',
            n_samples_per_garbage_class: int = None,
            expand_last_dim: bool = True,
            seed: int = 133):
    
    '''
    Takes as input a csv, a folder with audio files,
    a string lookup Tensorflow layers (to convert classes to one-hot vectors),
    and all the parameters needed to compute spectrogram patches,
    and returns a tf.data.Dataset of spectrogram patches & one-hot vectors

    Inputs
    -------
    sd : pandas DataFrame of the dataset.
    audio_path : str, Posixpath or pathlib.Path object, path to folder containing audio files
    patch_length : int, number of spectrogram frames per patch.
                    Note that the length is specified in frames, e.g. if each frame in 
                    the spectrogram represents 50 ms, a patch of 1s would need 20 frames. 
    n_mels : int, number of mel filters. passed to librosa.feature.melspectrogram
    target_rate : int, Sample rate of output waveform
    overlap : float between 0 and 1.0, proportion of overlap between consecutive spectrograms.
        For example, with an overlap of 0.25 and a patch length of 20, 
        patch number n would share its 5 first frames with patch (n-1),
        and its 5 last frames with patch (n+1). 
    n_fft : int, length of FFT window, passed to librosa.feature.melspectrogram
    spec_hop_length : int, hop length between FFTs, passed to librosa.feature.melspectrogram
    min_length : int,  Minimum length of output waveform in seconds. 
        If input waveform is below this duration, it will be repeated to reach min_length.
    max_length : int, Maximum length of output waveform in seconds.
        If input waveform is longer, it will be cut from the end.

    top_db : int, Passed to librosa.split. Frames below -top_db will be considered as silence and cut.
        Higher values induce more tolerance to silence.
    frame_length : int, frame length used for silence removal
    hop_length : int, hop length used for silence removal
    trim_last_second : bool. Set to True to cut the output waveform to an integer number of seconds.
        For example, if the output waveform is 7s and 350 ms long, this option will cut the last 350 ms.
    include_last_patch : bool. If set to False, the last spectrogram frames 
        will be discarded if they are not enough to build a new patch with.
        If set to True, they will be kept in a new patch which will more heavily overlap with the previous one.
        For example, with a patch length of 20 frames, and overlap of 0.25 (thus 5 frames),
        and an overall clip length of 127 frames, the last 7 frames would not be enough to build a new patch,
        since we'd need 20 - 5 = 15 new frames. If include_last_patch is set to False,
        these last 7 frames will be discarded. If it is set to True, 
        they will be included in a new patch along with the 13 previous frames.

    win_length : int, passed to librosa.feature.melspectrogram. If None default to n_fft
    window : str, passed to librosa.feature.melspectrogram
    center : bool, passed to librosa.feature.melspectrogram 
    pad_mode : str, passed to librosa.feature.melspectrogram
    power : float, 1.0 or 2.0 only are allowed. Set to 2.O for power melspectrogram, 
        and 1.0 for amplitude melspectrogram

    fmin : int, min freq of spectrogram, passed to librosa.feature.melspectrogram
    fmax : int, max freq of spectrogram, passed to librosa.feature.melspectrogram
    power_to_db_ref, : func, reference used to convert linear scale mel spectrogram to db scale. 
        Passed to passed to librosa.power_to_db or librosa.amplitude_to_db
    norm : str, normalization used for triangular mel weights. Passer to librosa.feature.melspectrogram
    Defaults to "slaney", in which case the triangular mel weights are divided by the width of the mel band.
    htk : bool, if True use the HTK formula to compute mel weights, else use Slaney's.
        Passed to librosa.feature.melspectrogram
    to_db : bool, if True convert the output spectrogram to decibel scale.
        if False we just take log(spec + 1e-4)
    use_garbage_class : bool, set to True to pool samples from all classes not included in class_names
        into an additional "garbage" (i.e. "other") class.
    n_samples_per_garbage_class : int, number of samples per unused class 
        to pool into the "garbage" class. If None, gets automatically determined 
        trying to keep a balanced dataset.
    expand_last_dim : bool, if True expand the last dim of each spectrogram patch
        (i.e. shape of patches becomes (n_mels, n_patches, 1))
    file_extension : str, file extension of audio files, e.g. ".wav". 
    batch_size : int, batch size of the output dataset
    to_cache : bool, if True cache output dataset
    shuffle : bool, if True shuffle output dataset
    return_clip_labels : bool, if True returns an additional numpy array 
                            containing labels linking each patch to its origin audio clip
    return_arrays : bool, if True returns a tuple (X, y) of numpy arrays
                    instead of a tf.data.Dataset
    seed : seed used for shuffling the dataset, and sampling data for the "garbage" class if asked.
    Outputs
    -------
    ds : tf.data.Dataset or tuple of np.ndarrays containing the spectrogram patches and labels.
         is a tf.data.Dataset is return_arrays is set to False, and a tuple of np.ndarrays
         if return_arrays is set to True.
    clip_labels : optional, np.ndarray containing labels linking each patch to its origin audio clip.
                  only returned if return_clip_labels is set to True.
    '''
    
    df['filename'] = df['filename'].astype('str')
    # Determine if we need to add file extension to file names
    add_file_extension = str(file_extension) not in df['filename'].iloc[0]

    # Raise error if some requested classes are not actually present in the DF
    available_classes = df["category"].unique()
    if not set(used_classes).issubset(set(available_classes)):
        raise ValueError(f"""Some classes in class_names were not found
        in the csv file associated with your dataset.
        Please check the class_names argument of the config file. 
        Classes that were not found in csv : {set(used_classes).difference(set(available_classes))}""")

    # If used_classes is not provided, warn and use all available classes
    if not used_classes:
        raise ValueError("Did not recieve any classes to use. Please check the class_names arg in your config file")
         
        
    # Handle all the "garbage class" stuff
    if use_garbage_class:
        if n_samples_per_garbage_class:
            pass
        else:
            # If user doesn't provide this arg, determine automatically.
            num_ind_samples = df['category'].isin(used_classes).sum()
            num_other_class = len(set(df['category'].unique()).difference(set(used_classes)))
            n_samples_per_garbage_class = ceil(num_ind_samples / num_other_class)
        
        df = _add_garbage_class_to_df(
            dataframe=df,
            classes_to_keep=used_classes,
            n_samples_per_other_class=n_samples_per_garbage_class,
            seed=seed,
            shuffle=True)
        
        num_other_samples = len(df[df['category'] == "other"])
    else:
        # Keep only user-provided classes
        df = df[df['category'].isin(used_classes)]

    num_samples = len(df)
    print("[INFO] : Loading dataset.")
    print(f"[INFO] : Using {len(used_classes)} classes.")
    print(f"[INFO] : Classes used : {used_classes}")
    print(f"[INFO] : Loaded {num_samples} audio clips.")
    if use_garbage_class:
        print('[INFO] : Using the additional "garbage" class.')
        print(f'[INFO] : Added {num_other_samples} samples to the "garbage" class.')

    # Load data
    X = []
    y= []
    if return_clip_labels:
        clip_labels = []

    n_patches_generated = 0
    for i in range(len(df)):
        if add_file_extension:
            fname = df['filename'].iloc[i] + str(file_extension)
        else:
            fname = df['filename'].iloc[i]

        label = df['category'].iloc[i]
        filepath = Path(audio_path, fname)
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
        n_patches_generated += len(patches)
        X.extend(patches)
        y.extend([label] * len(patches))
        if return_clip_labels :
            clip_labels.extend([i] * len(patches))

    # Concatenate X_train into a single array
    X = np.stack(X, axis=0)
    if expand_last_dim:
        X = np.expand_dims(X, axis=-1)
    print(f"[INFO] : Generated {n_patches_generated} patches")
    
    # One-hot encode label vectors
    vocab = df['category'].unique()
    string_lookup_layer = tf.keras.layers.StringLookup(
        vocabulary=sorted(list(vocab)), # Note we're sorting classes alphabetically here
        num_oov_indices=0,
        output_mode='one_hot')
    
    y = np.array(string_lookup_layer(y))

    ds = tf.data.Dataset.from_tensor_slices((X, y))
    ds = ds.batch(batch_size)
    if shuffle:
        if return_clip_labels:
            # Can't use actual warnings because they are silenced in the main script
            print("[WARNING] Tried to shuffle a dataset which has associated clip labels. \n \
                  This would break the clip labels. Skipping shuffle...")
            pass
        else:
            ds = ds.shuffle(len(ds), reshuffle_each_iteration=True, seed=seed)
    if to_cache:
        ds = ds.cache()
    ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    
    if return_arrays:
        ds = (X, y)
    if return_clip_labels:
        return ds, np.array(clip_labels)
    else:
        return ds
    

def load_ESC_10(csv: str,
                audio_path: str,
                class_names: List[str],
                patch_length: int,
                n_mels: int,
                target_rate: int,
                overlap: float,
                n_fft: int,
                spec_hop_length: int,
                min_length: int = 1, 
                max_length: int = 10, 
                top_db: int = 30,
                frame_length: int = 2048,
                hop_length: int = 512,
                trim_last_second: bool = False,
                include_last_patch: bool = False,
                win_length: int = None,
                window: str = 'hann',
                center: bool = True,
                pad_mode: bool = 'constant',
                power: float = 2.0,
                fmin: int = 20,
                fmax: int = 20000,
                power_to_db_ref = np.max,
                norm: str = "slaney",
                htk: bool = False,
                to_db: bool = True,
                use_garbage_class: bool = False,
                n_samples_per_garbage_class: int = None,
                validation_csv_path: str = None,
                validation_audio_path: str = None,
                validation_split: float = None,
                expand_last_dim: bool = True,
                file_extension: str = '.wav',
                batch_size: int = 32,
                to_cache: bool = True,
                shuffle: bool = True,
                seed: int = 133):
    '''Load ESC-10 dataset
    
    Inputs
    ------
    csv : str, posixpath or pathlib.Path object. Path to the training set .csv file.
    audio_path : str, posixpath or pathlib.Path object. Path to the folder containing 
        training audio files.
    class_names : List of str, List of the classes the user wishes to use.
        If None, use all ESC10 classes by default.
        Classes are sorted alphabetically inside the _get_ds() function.
    use_garbage_class : bool, set to True to pool samples from all classes not included in class_names
        into an additional "garbage" (i.e. "other") class.
    n_samples_per_garbage_class : int, number of samples per unused class 
        to pool into the "garbage" class.
        If None, gets automatically determined trying to keep a balanced dataset.
    validation_csv_path : str, posixpath or pathlib.Path object. 
        Path to the validation set .csv file. If None, the training set is split into
        training and validation sets if validation_split is not None. 
        If both are None, fold 5 of the dataset is used as a validation set.
    validation_audio_path : str, posixpath or pathlib.Path object.
        Path to the folder containing validation audio files. 
        Unused if validation_csv_path is None.
    validation_split : float. If validation_csv_path is None, and this arg isn't, split the training set
        into training/validation set according to the value of this arg.
    seed : seed used for train/val split & dataset shuffling.
    Other args : See the docstring of _get_ds()

    Output
    ------
    train_ds : tf.data.Dataset, training dataset
    val_ds : tf.data.Dataset, validation dataset
    val_clip_labels : np.ndarray, clip labels for each patch in the validation dataset.
    '''
    # If user provides no class subset, use all ESC-10 classes
    if not class_names:
        raise ValueError("Argument class_names was not provided ! \
                         Please provide at least one class in class_names")
    else:
        used_classes = class_names
    
    esc_df = pd.read_csv(csv)

    # If a validation path is provided, use it
    # If a validation split is provided, use it
    # If none of these are provided, use fold 5 as validation set.
    if  validation_csv_path is not None:
        train_esc_df = esc_df
        val_esc_df = pd.read_csv(validation_csv_path)

    elif validation_split is not None:
        train_esc_df, val_esc_df = train_test_split(esc_df, test_size=validation_split,
                                                    random_state=seed, stratify=esc_df['category'])

    else:
        # Use fold 5
        train_esc_df, val_esc_df = esc_df[esc_df["fold"] != 5], esc_df[esc_df["fold"] == 5]
    print("[INFO] : Loading training dataset")
    train_ds = _get_ds(
        df=train_esc_df,
        audio_path=audio_path,
        used_classes=used_classes,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=False,
        return_arrays=False,
        seed=seed)



    # Load validation data 
    # Use the validation dataset path if provided
    if validation_audio_path is not None:
        audio_path = validation_audio_path
    print("[INFO] : Loading validation dataset")
    val_ds, val_clip_labels =_get_ds(
        df=val_esc_df,
        audio_path=audio_path,
        used_classes=used_classes,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=True,
        return_arrays=False,
        seed=seed)

    return train_ds, val_ds, val_clip_labels

def load_custom_multiclass(csv: str,
                        audio_path: str,
                        class_names: List[str],
                        patch_length: int,
                        n_mels: int,
                        target_rate: int,
                        overlap: float,
                        n_fft: int,
                        spec_hop_length: int,
                        min_length: int = 1, 
                        max_length: int = 10, 
                        top_db: int = 30,
                        frame_length: int = 2048,
                        hop_length: int = 512,
                        trim_last_second: bool = False,
                        include_last_patch: bool = False,
                        win_length: int = None,
                        window: str = 'hann',
                        center: bool = True,
                        pad_mode: bool = 'constant',
                        power: float = 2.0,
                        fmin: int = 20,
                        fmax: int = 20000,
                        power_to_db_ref = np.max,
                        norm: str = "slaney",
                        htk: bool = False,
                        to_db: bool = True,
                        use_garbage_class: bool = False,
                        n_samples_per_garbage_class: int = None,
                        validation_csv_path: str = None,
                        validation_audio_path: str = None,
                        validation_split: float = None,
                        expand_last_dim: bool = True,
                        file_extension: str = '.wav',
                        batch_size: int = 32,
                        to_cache: bool = True,
                        shuffle: bool = True,
                        seed: int = 133):
    '''Load custom dataset in ESC format
    Inputs
    ------
    csv : str, posixpath or pathlib.Path object. Path to the training set .csv file.
    audio_path : str, posixpath or pathlib.Path object. Path to the folder containing 
        training audio files.
    class_names : List of str, List of the classes the user wishes to use.
        If None, use all classes present in the dataset.
        Classes are sorted alphabetically inside the _get_ds() function.
    use_garbage_class : bool, set to True to pool samples from all classes not included in class_names
        into an additional "garbage" (i.e. "other") class.
    n_samples_per_garbage_class : int, number of samples per unused class 
        to pool into the "garbage" class.
        If None, gets automatically determined trying to keep a balanced dataset.
    validation_csv_path : str, posixpath or pathlib.Path object. 
        Path to the validation set .csv file. If None, the training set is split into
        training and validation sets if validation_split is not None. 
        If both are None, fold 5 of the dataset is used as a validation set.
    validation_audio_path : str, posixpath or pathlib.Path object.
        Path to the folder containing validation audio files. 
        Unused if validation_csv_path is None.
    validation_split : float. If validation_csv_path is None, and this arg isn't, split the training set
        into training/validation set according to the value of this arg.
    seed : seed used for train/val split & dataset shuffling.
    Other args : See the docstring of _get_ds()

    Output
    ------
    train_ds : tf.data.Dataset, training dataset
    val_ds : tf.data.Dataset, validation dataset
    val_clip_labels : np.ndarray, clip labels for each patch in the validation dataset.
    '''

    esc_df = pd.read_csv(csv)
    if class_names is None:
        class_names = esc_df["category"].unique().tolist()

    # If a validation path is provided, use it
    # If a validation split is provided, use it
    # If none of these are provided, use fold 5 as validation set.
    if  validation_csv_path is not None:
        train_esc_df = esc_df
        val_esc_df = pd.read_csv(validation_csv_path)

    elif validation_split is not None:
        train_esc_df, val_esc_df = train_test_split(esc_df, test_size=validation_split,
                                                    random_state=seed, stratify=esc_df['category'])
        
    train_ds = _get_ds(
        df=train_esc_df,
        audio_path=audio_path,
        used_classes=class_names,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=False,
        return_arrays=False,
        seed=seed)

    # Load validation data 
    # Use the validation dataset path if provided
    if validation_audio_path is not None:
        audio_path = validation_audio_path

    val_ds, val_clip_labels =_get_ds(
        df=val_esc_df,
        audio_path=audio_path,
        used_classes=class_names,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=True,
        return_arrays=False,
        seed=seed)

    return train_ds, val_ds, val_clip_labels


def _prepare_fsd50k_csvs(csv_folder: str,
                         audioset_ontology_path: str,
                         class_names : List[str],
                         only_keep_monolabel: bool = True,
                         ):
    '''Converts FSD50K dataset to an ESC-like format expected by the model zoo.
    Unsmears labels, and discards samples belonging to classes not specified in class_names.
    Can additionally discard multilabel samples.
    Writes csvs compatible with the model zoo format to 
    csv_folder/unsmeared_dev.csv and csv_folder/unsmeared_eval.csv

    Inputs
    ------
    csv_folder : str or Path, path to the folder containing the FSD50K csv files.
      Default is FSD50K.ground_truth
    audioset_ontology_path : str or Path, path to the audioset ontology json file.
    class_names : List[str] : list of class names to keep
    only_keep_monolabel : if set to True, multilabel samples are discarded.

    Outputs
    -------
    None
    '''
    preferred_collapse_classes = class_names
    vocabulary_path = os.path.join(csv_folder, 'vocabulary.csv')
    dev_csv_path = os.path.join(csv_folder, 'dev.csv')
    eval_csv_path = os.path.join(csv_folder, 'eval.csv')

    unsmeared_dev_csv_path = os.path.join(csv_folder, "unsmeared_dev.csv")
    unsmeared_eval_csv_path = os.path.join(csv_folder, "unsmeared_eval.csv")
    # Unsmear labels
    print("Unsmearing labels for training set.")
    unsmear_labels(dev_csv_path,
                   vocabulary_path,
                   audioset_ontology_path,
                   output_file=unsmeared_dev_csv_path,
                   save=True)
    print("Unsmearing labels for test set")
    unsmear_labels(eval_csv_path,
                   vocabulary_path,
                   audioset_ontology_path,
                   output_file=unsmeared_eval_csv_path,
                   save=True)
    
    print("Generating model zoo-compatible CSV for training set.")
    output_file = os.path.join(csv_folder, "model_zoo_unsmeared_dev.csv")
    make_model_zoo_compatible(unsmeared_dev_csv_path,
                              classes_to_keep=None,
                              only_keep_monolabel=only_keep_monolabel,
                              collapse_to_monolabel=False,
                              preferred_collapse_classes=preferred_collapse_classes,
                              output_file=output_file,
                              save=True,
                              quick_hack=False)
    print("Successfully generated model zoo-compatible CSV for training set at {}".format(output_file))
    print("Generating model zoo-compatible CSV for test set.")
    output_file = os.path.join(csv_folder, "model_zoo_unsmeared_eval.csv")
    make_model_zoo_compatible(unsmeared_eval_csv_path,
                              classes_to_keep=None,
                              only_keep_monolabel=only_keep_monolabel,
                              collapse_to_monolabel=False,
                              preferred_collapse_classes=preferred_collapse_classes,
                              output_file=output_file,
                              save=True,
                              quick_hack=False)
    print("Successfully generated model zoo-compatible CSV for test set at {}".format(output_file))

    print("Done preparing FSD50K csv files !")

def load_FSD50K(dev_audio_folder: str ,
                eval_audio_folder: str ,
                audioset_ontology_path: str, 
                csv_folder: str,
                class_names: List[str],
                only_keep_monolabel: bool,
                patch_length: int,
                n_mels: int,
                target_rate: int,
                overlap: float,
                n_fft: int,
                spec_hop_length: int,
                min_length: int = 1, 
                max_length: int = 10, 
                top_db: int = 30,
                frame_length: int = 2048,
                hop_length: int = 512,
                trim_last_second: bool = False,
                include_last_patch: bool = False,
                win_length: int = None,
                window: str = 'hann',
                center: bool = True,
                pad_mode: bool = 'constant',
                power: float = 2.0,
                fmin: int = 20,
                fmax: int = 20000,
                power_to_db_ref = np.max,
                norm: str = "slaney",
                htk: bool = False,
                to_db: bool = True,
                use_garbage_class: bool = False,
                n_samples_per_garbage_class: int = None,
                expand_last_dim: bool = True,
                file_extension: str = '.wav',
                batch_size: int = 32,
                to_cache: bool = True,
                shuffle: bool = True,
                seed: int = 133):
    ''' 
    Load FSD50K dataset. Uses the dev split for the training set,
    and the eval split for the validation set.

    Inputs
    ------
    dev_audio_folder : Folder containing audio files for the dev split of FSD50K.
        Default is FSD50K/FSD50K.dev_audio
    eval_audio_folder : Folder containing audio files for the eval split of FSD50K.
        Default is FSD50K/FSD50K.eval_audio
    csv_folder : str or Path, path to the folder containing the FSD50K csv files.
        Default is FSD50K.ground_truth
    audioset_ontology_path : str or Path, path to the audioset ontology json file.
    class_names : List of str, List of the classes the user wishes to use.
        If None, throws an error.
        Classes are sorted alphabetically inside the _get_ds() function.
    only_keep_monolabel : if set to True, multilabel samples are discarded.
    use_garbage_class : bool, set to True to pool samples from all classes not included in class_names
        into an additional "garbage" (i.e. "other") class.
    n_samples_per_garbage_class : int, number of samples per unused class 
        to pool into the "garbage" class.
        If None, gets automatically determined trying to keep a balanced dataset.
    validation_csv_path : str, posixpath or pathlib.Path object. 
        Path to the validation set .csv file. If None, the training set is split into
        training and validation sets if validation_split is not None. 
        If both are None, fold 5 of the dataset is used as a validation set.
    validation_audio_path : str, posixpath or pathlib.Path object.
        Path to the folder containing validation audio files. 
        Unused if validation_csv_path is None.
    validation_split : float. If validation_csv_path is None, and this arg isn't, split the training set
        into training/validation set according to the value of this arg.
    seed : seed used for train/val split & dataset shuffling.
    Other args : See the docstring of _get_ds()

    Outputs
    -------
    train_ds : tf.data.Dataset, training dataset. 
        Consists of all the samples in the dev split of FSD50K.
    valid_ds : tf.data.Dataset, validation dataset. 
        Consists of all the samples in the eval split of FSD50K.
    valid_clip_labels : np.ndarray, Clip labels associated with the validation dataset.
    '''
    
    print("[INFO] : Loading FSD50K. The dev set will be used as the training set")
    print("and the eval set will be used as the validation set.")
    print("[INFO] : The dataset.training_*, and dataset.validation_* args in your config file will be ignored.")
    if not class_names:
        raise ValueError("Argument class_names was not provided ! \
                         Please provide at least one class in class_names")
    else:
        used_classes = class_names
    
    _prepare_fsd50k_csvs(csv_folder=csv_folder,
                         audioset_ontology_path=audioset_ontology_path,
                         class_names=class_names,
                         only_keep_monolabel=only_keep_monolabel)
    
    dev_csv_path = os.path.join(csv_folder, "model_zoo_unsmeared_dev.csv")
    eval_csv_path = os.path.join(csv_folder, "model_zoo_unsmeared_eval.csv")

    train_df = pd.read_csv(dev_csv_path)
    val_df = pd.read_csv(eval_csv_path) 
    # If a validation path is provided, use it
    # If a validation split is provided, use it
    # If none of these are provided, use fold 5 as validation set.
   
    print("[INFO] : Loading training dataset")
    train_ds = _get_ds(
        df=train_df,
        audio_path=dev_audio_folder,
        used_classes=used_classes,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=False,
        return_arrays=False,
        seed=seed)
    
    # Load validation data 
    # Use the eval set
    print("[INFO] : Loading validation dataset, using FSD50K's eval set as validation dataset.")
    val_ds, val_clip_labels =_get_ds(
        df=val_df,
        audio_path=eval_audio_folder,
        used_classes=used_classes,
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
        to_db=to_db,
        use_garbage_class=use_garbage_class,
        n_samples_per_garbage_class=n_samples_per_garbage_class,
        expand_last_dim=expand_last_dim,
        file_extension=file_extension,
        batch_size=batch_size,
        to_cache=to_cache,
        shuffle=shuffle,
        return_clip_labels=True,
        return_arrays=False,
        seed=seed)

    return train_ds, val_ds, val_clip_labels

def load_dataset(dataset_name: str = None,
                 training_csv_path: str = None,
                 training_audio_path: str = None,
                 validation_csv_path: str = None,
                 validation_audio_path: str = None,
                 validation_split: float = None,
                 quantization_csv_path: str = None,
                 quantization_audio_path: str = None,
                 test_csv_path: str = None,
                 test_audio_path: str = None,
                 class_names: List[str] = None,
                 patch_length: int = None,
                 n_mels: int = None,
                 target_rate: int = None,
                 overlap: float = None,
                 n_fft: int = None,
                 spec_hop_length: int = None,
                 min_length: int = None, 
                 max_length: int = None, 
                 top_db: int = None,
                 frame_length: int = None,
                 hop_length: int = None,
                 trim_last_second: bool = False,
                 include_last_patch: bool = False,
                 win_length: int = None,
                 window: str = None,
                 center: bool = None,
                 pad_mode: bool = 'constant',
                 power: float = None,
                 fmin: int = None,
                 fmax: int = None,
                 power_to_db_ref = np.max,
                 norm: str = None,
                 htk: bool = None,
                 to_db: bool = None,
                 use_garbage_class: bool = None,
                 n_samples_per_garbage_class: int = None,
                 expand_last_dim: bool = None,
                 file_extension: str = None,
                 batch_size: int = None,
                 to_cache: bool = None,
                 shuffle: bool = None,
                 seed: int = 133,
                 fsd50k_dev_audio_folder: str = None,
                 fsd50k_eval_audio_folder: str = None,
                 fsd50k_csv_folder: str = None,
                 fsd50k_audioset_ontology_path: str = None,
                 fsd50k_keep_only_monolabel: str = True,
                 ) -> Tuple[tf.data.Dataset, tf.data.Dataset, np.ndarray,
                            tf.data.Dataset, tf.data.Dataset, np.ndarray]:
    """ Loads a dataset. Returns a training dataset, validation dataset and optionally a quantization
    and test dataset. Also returns validation and test clip labels.
    Calls different loading functions depending on the given dataset_name.

    Inputs
    ------
    dataset_name : str, must be one of "esc10", "fsd50k" or "custom".
    training_csv_path : str, posixpath or pathlib.Path object. Path to the training set .csv file.
    training_audio_path : str, posixpath or pathlib.Path object. Path to the folder containing 
        training audio files.
    validation_csv_path : str, posixpath or pathlib.Path object. 
        Path to the validation set .csv file. If None, the training set is split into
        training and validation sets if validation_split is not None. 
        If both are None, fold 5 of the dataset is used as a validation set.
    validation_audio_path : str, posixpath or pathlib.Path object.
        Path to the folder containing validation audio files. 
        Unused if validation_csv_path is None.
    validation_split : float. If validation_csv_path is None, and this arg isn't,
        split the training set into training/validation set according to the value of this arg.
    quantization_csv_path : str, posixpath or pathlib.Path object. Path to the quantization set .csv file.
        If None, no quantization dataset is returned.
    quantization_audio_path : str, posixpath or pathlib.Path object. Path to the folder containing 
        quantization audio files.
    test_csv_path : str, posixpath or pathlib.Path object. Path to the test set .csv file.
        If None, no test dataset is returned.
    test_audio_path : str, posixpath or pathlib.Path object. Path to the folder containing 
        test audio files.
    For other args, see the docstrings of load_ESC_10(), load_custom_multiclass() 
        or load_FSD50K() respectively
    
    Outputs
    -------
    train_ds : tf.data.Dataset, training dataset
    val_ds : tf.data.Dataset, validation dataset
    val_clip_labels : np.ndarray, validation set clip labels 
        (each patch has 1 label denoting which clip it belongs to)
    quantization_ds : tf.data.Dataset, optional. Quantization dataset, 
        is None if quantization_csv_path is None.
    test_ds : tf.data.Dataset, optional. Test dataset, is None if test_csv_path is None.
    test_clip_labels : np.ndarray, optional, test set clip labels 
        (each patch has 1 label denoting which clip it belongs to)
        Is None if test_csv_path is None.
    """

    if dataset_name.lower() == "fsd50k":
        # Load FSD50K
        train_ds, val_ds, val_clip_labels= load_FSD50K(
            dev_audio_folder=fsd50k_dev_audio_folder,
            eval_audio_folder=fsd50k_eval_audio_folder,
            audioset_ontology_path=fsd50k_audioset_ontology_path, 
            csv_folder=fsd50k_csv_folder,
            class_names=class_names,
            only_keep_monolabel=fsd50k_keep_only_monolabel,
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
            power_to_db_ref = np.max,
            norm=norm,
            htk=htk,
            to_db=to_db,
            use_garbage_class=use_garbage_class,
            n_samples_per_garbage_class=n_samples_per_garbage_class,
            expand_last_dim=expand_last_dim,
            file_extension=file_extension,
            batch_size=batch_size,
            to_cache=to_cache,
            shuffle=shuffle,
            seed=seed)
    elif training_csv_path:
        if dataset_name.lower() == "esc10":
            # Load ESC-10
            train_ds, val_ds, val_clip_labels = load_ESC_10(
                csv=training_csv_path,
                audio_path=training_audio_path,
                class_names=class_names,
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
                to_db=to_db,
                use_garbage_class=use_garbage_class,
                n_samples_per_garbage_class=n_samples_per_garbage_class,
                validation_csv_path=validation_csv_path,
                validation_audio_path=validation_audio_path,
                validation_split=validation_split,
                expand_last_dim=expand_last_dim,
                file_extension=file_extension,
                batch_size=batch_size,
                to_cache=to_cache,
                shuffle=shuffle,
                seed=seed
            )

        elif dataset_name.lower() == "custom":
            # Load custom dataset with ESC format
            train_ds, val_ds, val_clip_labels = load_custom_multiclass(
                csv=training_csv_path,
                audio_path=training_audio_path,
                class_names=class_names,
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
                to_db=to_db,
                use_garbage_class=use_garbage_class,
                n_samples_per_garbage_class=n_samples_per_garbage_class,
                validation_csv_path=validation_csv_path,
                validation_audio_path=validation_audio_path,
                validation_split=validation_split,
                expand_last_dim=expand_last_dim,
                file_extension=file_extension,
                batch_size=batch_size,
                to_cache=to_cache,
                shuffle=shuffle,
                seed=seed
            )
        else:
            raise ValueError("Dataset name must be one of the following : \n \
                            'esc10', 'fsd50k', or 'custom' for a custom dataset")
    else:
        train_ds = None
        val_ds = None
        val_clip_labels = None

    if quantization_csv_path:
        quant_df = pd.read_csv(quantization_csv_path)
        if class_names is None:
            quant_class_names = quant_df["category"].unique().tolist()
        else:
            quant_class_names = class_names

        quantization_ds = _get_ds(
            df=quant_df,
            audio_path=quantization_audio_path,
            used_classes=quant_class_names,
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
            to_db=to_db,
            use_garbage_class=use_garbage_class,
            n_samples_per_garbage_class=n_samples_per_garbage_class,
            expand_last_dim=expand_last_dim,
            file_extension=file_extension,
            batch_size=batch_size,
            to_cache=to_cache,
            shuffle=shuffle,
            return_clip_labels=False,
            return_arrays=False,
            seed=seed)
    else:
        quantization_ds = None

    if test_csv_path:
        test_df = pd.read_csv(test_csv_path)
        if class_names is None:
            test_class_names = test_df["category"].unique().tolist()
        else:
            test_class_names = class_names

        test_ds, test_clip_labels = _get_ds(
            df=test_df,
            audio_path=test_audio_path,
            used_classes=test_class_names,
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
            to_db=to_db,
            use_garbage_class=use_garbage_class,
            n_samples_per_garbage_class=n_samples_per_garbage_class,
            expand_last_dim=expand_last_dim,
            file_extension=file_extension,
            batch_size=batch_size,
            to_cache=to_cache,
            shuffle=shuffle,
            return_clip_labels=True,
            return_arrays=False,
            seed=seed)
    else:
        test_ds = None
        test_clip_labels = None

    return train_ds, val_ds, val_clip_labels, quantization_ds, test_ds, test_clip_labels