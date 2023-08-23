# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import os
import pickle
import numpy as np
import pandas as pd
import joblib
from math import ceil
from pathlib import Path
from sklearn.model_selection import train_test_split
from preprocess import load_and_reformat
from feature_extraction import compute_mel_spectrogram, get_patches
from dataset_utils.fsd50k.unsmear_labels import generate_ranked_vocabulary, filter_labels, unsmear_labels, make_model_zoo_compatible

def _load_audio_sample(filepath,
                       patch_length,
                       n_mels,
                       target_rate,
                       overlap,
                       n_fft,
                       spec_hop_length,
                       min_length=1, 
                       max_length=10, 
                       top_db=30,
                       frame_length=2048,
                       hop_length=512,
                       trim_last_second=False,
                       include_last_patch=False,
                       win_length=None,
                       window='hann',
                       center=True,
                       pad_mode='constant',
                       power=2.0,
                       fmin=20,
                       fmax=20000,
                       power_to_db_ref = np.max,
                       norm="slaney",
                       htk=False,
                       to_db=True,
                       **kwargs
                       ):
    '''Internal utility to load an audio sample'''

    # Hate having to do this
    if norm == "None":
        norm = None
    wave, sr = load_and_reformat(wave_path=filepath,
                                 min_length=min_length,
                                 max_length=max_length,
                                 target_rate=target_rate,
                                 top_db=top_db,
                                 frame_length=frame_length,
                                 hop_length=hop_length,
                                 trim_last_second=trim_last_second)
        
    patches = get_patches(wave=wave,
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


def _esc10_csv_to_tf_dataset(cfg, esc_csv, audio_path,string_lookup_layer,
                             to_cache=True, return_clip_labels=False,
                             return_arrays=False):
    
    esc_csv['filename'] = esc_csv['filename'].astype('str')
    # Determine if we need to add file extension to file names
    add_file_extension = str(cfg.dataset.file_extension) not in esc_csv['filename'].iloc[0]

    # Load training data
    X = []
    y= []
    if return_clip_labels:
        clip_labels = []

    n_patches_generated = 0
    for i in range(len(esc_csv)):
        if add_file_extension:
            fname = esc_csv['filename'].iloc[i] + str(cfg.dataset.file_extension)
        else:
            fname = esc_csv['filename'].iloc[i]

        label = esc_csv['category'].iloc[i]
        filepath = Path(audio_path, fname)
        patches = _load_audio_sample(filepath=filepath,
                                     patch_length=cfg.feature_extraction.patch_length,
                                     n_mels=cfg.feature_extraction.n_mels,
                                     target_rate=cfg.pre_processing.target_rate,
                                     overlap=cfg.feature_extraction.overlap,
                                     n_fft=cfg.feature_extraction.n_fft,
                                     spec_hop_length=cfg.feature_extraction.hop_length,
                                     min_length=cfg.pre_processing.min_length,
                                     max_length=cfg.pre_processing.max_length,
                                     top_db=cfg.pre_processing.top_db,
                                     frame_length=cfg.pre_processing.frame_length,
                                     hop_length=cfg.pre_processing.hop_length,
                                     trim_last_second=cfg.pre_processing.trim_last_second,
                                     include_last_patch=cfg.feature_extraction.include_last_patch,
                                     win_length=cfg.feature_extraction.window_length,
                                     window=cfg.feature_extraction.window,
                                     center=cfg.feature_extraction.center,
                                     pad_mode=cfg.feature_extraction.pad_mode,
                                     power=cfg.feature_extraction.power,
                                     fmin=cfg.feature_extraction.fmin,
                                     fmax=cfg.feature_extraction.fmax,
                                     norm=cfg.feature_extraction.norm,
                                     htk=cfg.feature_extraction.htk,
                                     to_db=cfg.feature_extraction.to_db)
        n_patches_generated += len(patches)
        X.extend(patches)
        y.extend([label] * len(patches))
        if return_clip_labels :
            clip_labels.extend([i] * len(patches))
    # Concatenate X_train into a single array
    X = np.stack(X, axis=0)
    if cfg.model.expand_last_dim:
        X = np.expand_dims(X, axis=-1)
    print("[INFO] Generated {} patches".format(n_patches_generated))

    
    # One-hot encode label vectors

    y = np.array(string_lookup_layer(y))


    ds = tf.data.Dataset.from_tensor_slices((X, y))
    ds = ds.batch(cfg.train_parameters.batch_size)
    if to_cache:
        ds = ds.cache()
    ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    
    if return_arrays:
        ds = (X, y)
    if return_clip_labels:
        return ds, np.array(clip_labels)
    else:
        return ds

def _add_garbage_class_to_df(dataframe,
                             classes_to_keep,
                             n_samples_per_other_class,
                             seed=42,
                             shuffle=True):
    '''
    Takes a dataframe, a list of classes, subsamples classes not in said list, 
    and changes their label to "other".
    
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
                                                                    random_state=seed)
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

    

def load_ESC_10(cfg, to_cache=True):
    '''Load ESC-10 dataset'''

    audio_path = cfg.dataset.audio_path
    csv_path = cfg.dataset.csv_path

    # If user provides no class subset, use all ESC-10 classes
    if cfg.dataset.class_names is None:
        used_classes = ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain',
       'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves']
    else:
        used_classes = cfg.dataset.class_names
    
    esc_csv = pd.read_csv(csv_path)
    if cfg.dataset.use_other_class:
        
        if cfg.dataset.n_samples_per_other_class:
            n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
        else:
            # If user doesn't provide this arg, determine automatically.
            num_ind_samples = esc_csv['category'].isin(used_classes).sum()
            num_other_class = len(set(esc_csv['category'].unique()).difference(set(used_classes)))
            n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
        
        esc_csv = _add_garbage_class_to_df(dataframe=esc_csv,
                                           classes_to_keep=used_classes,
                                           n_samples_per_other_class=n_samples_per_other_class,
                                           seed=42,
                                           shuffle=True)
        
        num_other_samples = len(esc_csv[esc_csv['category'] == "other"])
        print('[INFO] Loading ESC-10 dataset. Using {} classes out of 10. \n Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Lumping all other classes into "other" class. \n \
               Number of samples assigned to "other" class : {}'.format(num_other_samples))
        print('[INFO] Loading {} samples.'.format(len(esc_csv)))

    else:
        esc_csv = esc_csv[esc_csv['esc10']]

        # Keep only user-provided classes
        esc_csv = esc_csv[esc_csv['category'].isin(used_classes)]
        print('[INFO] Loading ESC-10 dataset. Using {} classes out of 10. Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Loading {} samples.'.format(len(esc_csv)))
    if cfg.dataset.test_split is not None:
        test_split = cfg.dataset.test_split
    else:
        test_split = 0.2
    
    if cfg.dataset.validation_split is not None:
        validation_split = cfg.dataset.validation_split
    else:
        validation_split = 0.1
    
    if cfg.dataset.test_path is None:
        # Split into train and test sets
        # Using seed 133 because it seems like that's what's used for the image classification datasets.
        train_esc_csv, test_esc_csv = train_test_split(esc_csv, test_size=test_split,
                                                    random_state=133, stratify=esc_csv['category'])

        train_esc_csv, validation_esc_csv = train_test_split(train_esc_csv, test_size=validation_split,
                                                            random_state=42, stratify=train_esc_csv['category'])

        print("[INFO] Training set size : {} samples \n Validation test size : {} \n Test set size : {} samples".format(
            len(train_esc_csv), len(validation_esc_csv), len(test_esc_csv)
        ))
    else:
        train_esc_csv, validation_esc_csv = train_test_split(esc_csv, test_size=validation_split,
                                                             random_state=133, stratify=train_esc_csv['category'])
        
        print("[INFO] Training set size : {} samples \n Validation test size : {}".format(
            len(train_esc_csv), len(validation_esc_csv)
        ))
        
        test_esc_csv = pd.read_csv(cfg.dataset.test_path)
        # Handle "other class" stuff
        if cfg.dataset.use_other_class:
        
            if cfg.dataset.n_samples_per_other_class:
                n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
            else:
                # If user doesn't provide this arg, determine automatically.
                num_ind_samples = test_esc_csv['category'].isin(used_classes).sum()
                num_other_class = len(set(test_esc_csv['category'].unique()).difference(set(used_classes)))
                n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
            
            # Scale n_samples_per_other_class to size of test set

            print("[INFO] Scaling number of samples per unused class assigned to other class")
            n_samples_per_other_class = min(1, ceil(n_samples_per_other_class * len(test_esc_csv) / len(esc_csv)))
            print("[INFO] Assigning {} sample per unused class".format(n_samples_per_other_class))
            
            test_esc_csv = _add_garbage_class_to_df(dataframe=test_esc_csv,
                                                    classes_to_keep=used_classes,
                                                    n_samples_per_other_class=n_samples_per_other_class,
                                                    seed=42,
                                                    shuffle=True)
            
            num_other_samples = len(test_esc_csv[test_esc_csv['category'] == "other"])
            print('[INFO] Loading User specified test set. Using {} classes. \n Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Lumping all other classes into "other" class. \n \
                Number of samples assigned to "other" class : {}'.format(num_other_samples))
            print('[INFO] Loading {} samples.'.format(len(test_esc_csv)))
        else:
            # Keep only user-provided classes
            test_esc_csv = test_esc_csv[test_esc_csv['category'].isin(used_classes)]
            print('[INFO] Loading user-specified test set. Using {} classes out of 10. Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Loading {} samples.'.format(len(test_esc_csv)))

    
    # One-hot encode label vectors
    vocab = train_esc_csv['category'].unique()
    string_lookup_layer = tf.keras.layers.StringLookup(
        vocabulary=sorted(list(vocab)),
        num_oov_indices=0,
        output_mode='one_hot')

    train_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=train_esc_csv,
                                        audio_path=audio_path,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)



    # Load validation data 
    valid_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=validation_esc_csv,
                                        audio_path=audio_path,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)

    # Load test data 
    test_ds, clip_labels = _esc10_csv_to_tf_dataset(cfg=cfg,
                                       esc_csv=test_esc_csv,
                                       audio_path=audio_path,
                                       string_lookup_layer=string_lookup_layer,
                                       to_cache=to_cache,
                                       return_clip_labels=True,
                                       return_arrays=True)
    return train_ds, valid_ds, test_ds, clip_labels
    
def load_custom_esc_like_multiclass(cfg, to_cache=True):
    '''Loads custom dataset provided in ESC-like format (see readme for details).
       Data must be multiclass / mono-label, i.e. only one label per sample.
       A function to load a custom dataset with multilabel support will be provided separately'''
    audio_path = cfg.dataset.audio_path
    csv_path = cfg.dataset.csv_path
    csv = pd.read_csv(csv_path)
    # If user provides no class subset, use all available classes
    if cfg.dataset.class_names is None:
        used_classes = pd.unique(csv['category']).to_list()
    else:
        used_classes = cfg.dataset.class_names
    
    if cfg.dataset.use_other_class:
            
            if cfg.dataset.n_samples_per_other_class:
                n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
            else:
                # If user doesn't provide this arg, determine automatically.
                num_ind_samples = csv['category'].isin(used_classes).sum()
                num_other_class = len(set(csv['category'].unique()).difference(set(used_classes)))
                n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
            
            csv = _add_garbage_class_to_df(dataframe=csv,
                                               classes_to_keep=used_classes,
                                               n_samples_per_other_class=n_samples_per_other_class,
                                               seed=42,
                                               shuffle=True)
            
            num_other_samples = len(csv[csv['category'] == "other"])
            print('[INFO] Loading Custom dataset using ESC-like format. \n \
            Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Lumping all other classes into "other" class. \n \
                Number of samples assigned to "other" class : {}'.format(num_other_samples))
            print('[INFO] Loading {} samples.'.format(len(csv)))



    else:
        # Keep only user-provided classes
        csv = csv[csv['category'].isin(used_classes)]
        print('[INFO] Loading Custom dataset using ESC-like format. \n \
        Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Loading {} samples.'.format(len(csv)))

    if cfg.dataset.test_split is not None:
        test_split = cfg.dataset.test_split
    else:
        test_split = 0.2
    
    if cfg.dataset.validation_split is not None:
        validation_split = cfg.dataset.validation_split
    else:
        validation_split = 0.1
    
    if cfg.dataset.test_path is None:
        # Split into train and test sets
        # Using seed 133 because it seems like that's what's used for the image classification datasets.
        train_csv, test_csv = train_test_split(csv, test_size=test_split,
                                            random_state=133, stratify=csv['category'])

        train_csv, validation_csv = train_test_split(train_csv, test_size=validation_split,
                                                    random_state=133, stratify=train_csv['category'])

        print("[INFO] Training set size : {} samples \n Validation test size : {} \n Test set size : {} samples".format(
            len(train_csv), len(validation_csv), len(test_csv)
        ))

    else:
        train_csv, validation_csv = train_test_split(csv, test_size=validation_split,
                                                                random_state=133, stratify=csv['category'])
        
        print("[INFO] Training set size : {} samples \n Validation test size : {}".format(
            len(train_csv), len(validation_csv)
        ))
        
        test_csv = pd.read_csv(cfg.dataset.test_path)

        # Handle "other class" stuff
        if cfg.dataset.use_other_class:
        
            if cfg.dataset.n_samples_per_other_class:
                n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
            else:
                # If user doesn't provide this arg, determine automatically.
                num_ind_samples = test_csv['category'].isin(used_classes).sum()
                num_other_class = len(set(test_csv['category'].unique()).difference(set(used_classes)))
                n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
            
            # Scale n_samples_per_other_class to size of test set

            print("[INFO] Scaling number of samples per unused class assigned to other class")
            n_samples_per_other_class = min(1, ceil(n_samples_per_other_class * len(test_csv) / len(csv)))
            print("[INFO] Assigning {} sample per unused class".format(n_samples_per_other_class))
            
            test_csv = _add_garbage_class_to_df(dataframe=test_csv,
                                                    classes_to_keep=used_classes,
                                                    n_samples_per_other_class=n_samples_per_other_class,
                                                    seed=42,
                                                    shuffle=True)
            
            num_other_samples = len(test_csv[test_csv['category'] == "other"])
            print('[INFO] Loading User specified test set. Using {} classes. \n Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Lumping all other classes into "other" class. \n \
                Number of samples assigned to "other" class : {}'.format(num_other_samples))
            print('[INFO] Loading {} samples.'.format(len(test_csv)))

        else:
            # Keep only user-provided classes
            test_csv = test_csv[test_csv['category'].isin(used_classes)]
            print('[INFO] Loading user-specified test set. Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Loading {} samples.'.format(len(test_csv)))
    
    # One-hot encode label vectors
    vocab = train_csv['category'].unique()
    string_lookup_layer = tf.keras.layers.StringLookup(
        vocabulary=sorted(list(vocab)),
        num_oov_indices=0,
        output_mode='one_hot')

    train_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=train_csv,
                                        audio_path=audio_path,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)


    # Load validation data 
    valid_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=validation_csv,
                                        audio_path=audio_path,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)


    # Load test data 
    test_ds, clip_labels = _esc10_csv_to_tf_dataset(cfg=cfg,
                                       esc_csv=test_csv,
                                       audio_path=audio_path,
                                       string_lookup_layer=string_lookup_layer,
                                       to_cache=to_cache,
                                       return_clip_labels=True,
                                       return_arrays=True)


    return train_ds, valid_ds, test_ds, clip_labels

def _prepare_fsd50k_csvs(cfg):
    csv_folder = cfg.dataset_specific.fsd50k.csv_folder
    audioset_ontology_path = cfg.dataset_specific.fsd50k.audioset_ontology_path
    only_keep_monolabel = cfg.dataset_specific.fsd50k.only_keep_monolabel
    collapse_to_monolabel = cfg.dataset_specific.fsd50k.collapse_to_monolabel
    preferred_collapse_classes = cfg.dataset.class_names
    classes_to_keep = cfg.dataset.class_names
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
    print("Successfully generated model zoo-compatible CSV for testset at {}".format(output_file))

    print("Done preparing FSD50K csv files !")


def load_FSD50K(cfg, to_cache=True):
    '''Loads FSD50K dataset.'''

    dev_audio_folder = cfg.dataset_specific.fsd50k.dev_audio_folder
    eval_audio_folder = cfg.dataset_specific.fsd50k.eval_audio_folder
    csv_folder = cfg.dataset_specific.fsd50k.csv_folder

    # Run FSD50K preprocessing

    _prepare_fsd50k_csvs(cfg)

    dev_csv_path = os.path.join(csv_folder, "model_zoo_unsmeared_dev.csv")
    eval_csv_path = os.path.join(csv_folder, "model_zoo_unsmeared_eval.csv")

    train_csv = pd.read_csv(dev_csv_path)
    test_csv = pd.read_csv(eval_csv_path) 

    # If user provides no class subset, use all available classes
    if cfg.dataset.class_names is None:
        used_classes = pd.unique(train_csv['category']).to_list()
    else:
        used_classes = cfg.dataset.class_names

    if cfg.dataset.use_other_class:
            
            if cfg.dataset.n_samples_per_other_class:
                n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
            else:
                # If user doesn't provide this arg, determine automatically.
                num_ind_samples = train_csv['category'].isin(used_classes).sum()
                num_other_class = len(set(train_csv['category'].unique()).difference(set(used_classes)))
                n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
            
            train_csv = _add_garbage_class_to_df(dataframe=train_csv,
                                                classes_to_keep=used_classes,
                                                n_samples_per_other_class=n_samples_per_other_class,
                                                seed=42,
                                                shuffle=True)
            print(train_csv['category'])
            
            num_other_samples = len(train_csv[train_csv['category'] == "other"])
            print('[INFO] Loading FSD50K training dataset \n \
            Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
            print('[INFO] Lumping all other classes into "other" class. \n \
                Number of samples assigned to "other" class : {}'.format(num_other_samples))
            print('[INFO] Loading {} samples.'.format(len(train_csv)))



    else:
        # Keep only user-provided classes
        train_csv = train_csv[train_csv['category'].isin(used_classes)]
        print('[INFO] Loading FSD50K training dataset. \n \
        Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Loading {} samples.'.format(len(train_csv)))

    if cfg.dataset.test_split is not None:
        print("Using FSD50K eval set as test set. Ignoring test split.")
    else:
        print("Using FSD50K eval set as test set")

    if cfg.dataset.validation_split is not None:
        validation_split = cfg.dataset.validation_split
    else:
        validation_split = 0.1


    train_csv, validation_csv = train_test_split(train_csv, test_size=validation_split,
                                                            random_state=133, stratify=train_csv['category'])
    
    print("[INFO] Training set size : {} samples \n Validation test size : {}".format(
        len(train_csv), len(validation_csv)
    ))

    # Handle "other class" stuff
    if cfg.dataset.use_other_class:
    
        if cfg.dataset.n_samples_per_other_class:
            n_samples_per_other_class = cfg.dataset.n_samples_per_other_class
        else:
            # If user doesn't provide this arg, determine automatically.
            num_ind_samples = test_csv['category'].isin(used_classes).sum()
            num_other_class = len(set(test_csv['category'].unique()).difference(set(used_classes)))
            n_samples_per_other_class = ceil(num_ind_samples / num_other_class)
        
        # Scale n_samples_per_other_class to size of test set

        print("[INFO] Scaling number of samples per unused class assigned to other class")
        n_samples_per_other_class = min(1, ceil(n_samples_per_other_class * len(test_csv) / len(train_csv)))
        print("[INFO] Assigning {} sample per unused class".format(n_samples_per_other_class))
        
        test_csv = _add_garbage_class_to_df(dataframe=test_csv,
                                            classes_to_keep=used_classes,
                                            n_samples_per_other_class=n_samples_per_other_class,
                                            seed=42,
                                            shuffle=True)
        
        num_other_samples = len(test_csv[test_csv['category'] == "other"])
        print('[INFO] Loading FSD50K eval set. Using {} classes. \n Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Lumping all other classes into "other" class. \n \
            Number of samples assigned to "other" class : {}'.format(num_other_samples))
        print('[INFO] Loading {} samples.'.format(len(test_csv)))

    else:
        # Keep only user-provided classes
        test_csv = test_csv[test_csv['category'].isin(used_classes)]
        print('[INFO] Loading FSD50K eval set. Using {} classes. Classes used : {}'.format(len(used_classes), used_classes))
        print('[INFO] Loading {} samples.'.format(len(test_csv)))

    # One-hot encode label vectors
    vocab = train_csv['category'].unique()
    string_lookup_layer = tf.keras.layers.StringLookup(
        vocabulary=sorted(list(vocab)),
        num_oov_indices=0,
        output_mode='one_hot')

    train_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=train_csv,
                                        audio_path=dev_audio_folder,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)


    # Load validation data 
    valid_ds = _esc10_csv_to_tf_dataset(cfg=cfg,
                                        esc_csv=validation_csv,
                                        audio_path=dev_audio_folder,
                                        string_lookup_layer=string_lookup_layer,
                                        to_cache=to_cache)


    # Load test data 
    test_ds, clip_labels = _esc10_csv_to_tf_dataset(cfg=cfg,
                                                    esc_csv=test_csv,
                                                    audio_path=eval_audio_folder,
                                                    string_lookup_layer=string_lookup_layer,
                                                    to_cache=to_cache,
                                                    return_clip_labels=True,
                                                    return_arrays=True)
    
    return train_ds, valid_ds, test_ds, clip_labels