# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import pandas as pd
import os
import json
import numpy as np

def generate_ranked_vocabulary(vocabulary,
                               audioset_ontology,
                               output_file=None):
    '''Takes as input the vocabulary.csv file of FSD50K and adds a "ranking" column
       indicating whether each class is a leaf or intermediate node according to the ontology

       Inputs
       ------
       vocabulary : str or PosixPath : Path to the vocabulary.csv file contained in the FSD50K dataset
       audioset_ontology : str or Posixpath : Path to the audioset ontology json file. 
            Download here : https://github.com/audioset/ontology/blob/master/ontology.json
       output_file : str or PosixPath : Path to write the output csv file.
       
       Outputs
       -------
       vocabulary_ranked.csv : The vocabulary.csv file with an extra ranking column added 
            indicating whether each class is a leaf or intermediate node.'''

            
    fsd_vocab = pd.read_csv(vocabulary, header=None,
                            names= ['id', 'name', 'mids'])
                            
    with open(audioset_ontology, 'r') as f:
        audioset_ontology = json.load(f)

    ranks = []
    set_of_mids = set(fsd_vocab['mids'].tolist())
    for i in range(len(fsd_vocab)):
        for cl in audioset_ontology:
            # If this is the corresponding audioset class
            if cl['id'] == fsd_vocab['mids'].iloc[i]:
                # Then determine if it has any children in the audioset ontology
                if len(cl['child_ids']) == 0:
                    # If it doesn't it's a leaf
                    ranks.append('Leaf')
                # If it does then see if these children are also in the FSD50k ontology
                else:
                    child_set = set(cl['child_ids'])
                    if len(child_set.intersection(set_of_mids)) == 0:
                        # if the children aren't in FSD50k ontology then it's a leaf
                        ranks.append('Leaf')
                    else:
                        # if they are then it's an intermediate node
                        ranks.append('Intermediate')
                break

    fsd_vocab['ranks'] = ranks
    if output_file is None:
        output_file = 'vocabulary_ranked.csv'
    fsd_vocab.to_csv(output_file, header=False, index=False)


def _remove_labels(labels, to_keep):
    '''Internal utility function'''
    labels = labels.split(',')
    kept = [l for l in labels if l in to_keep]
    labels = ','.join(kept)
    return labels

def filter_labels(ground_truth, ranked_vocabulary, node_rank='Leaf',
                  output_file=None, save=False, drop_no_label=True):
    '''Filters labels based on label node rank in audioset ontology.
    
    Inputs
    ------
    ground_truth : csv file with FSD50K ground truth labels
    ranked_vocabulary : ranked FSD50K vocabulary csv file. 
    node_rank : str, if "Leaf" keep leaf labels, if "Intermediate" keep all other labels
    output_file : path to the file to where the filtered dataframe should be saved
    save : bool, set to True to save the filtered dataframe
    drop_no_label : bool, if True drop rows with no remaining labels after filtering
    
    Outputs
    -------
    ground_truth_df : pandas.Dataframe, dataframe containing the filtered labels'''
    ground_truth_df = pd.read_csv(ground_truth)
    names = ['id', 'name', 'mids', 'rank']
    ranked_vocabulary = pd.read_csv(ranked_vocabulary, header=None, names=names)
    leaves = ranked_vocabulary[ranked_vocabulary['rank'] == 'Leaf']['name'].to_list()
    intermediates = ranked_vocabulary[ranked_vocabulary['rank'] == 'Intermediate']['name'].to_list()

    if node_rank == 'Leaf':
        to_keep = leaves
    elif node_rank == 'Intermediate':
        to_keep = intermediates
    else:
        raise ValueError('node_rank arg must be either "Leaf" or "Intermediate"')

    filtered_labels = []
    for i in range(len(ground_truth_df)):
        labels = ground_truth_df['labels'].iloc[i]
        filtered_labels.append(_remove_labels(labels, to_keep=to_keep))
    ground_truth_df.drop('labels', axis=1, inplace=True)
    ground_truth_df['labels'] = filtered_labels

    if drop_no_label:
        nan_value = float('NaN')
        ground_truth_df.replace("", nan_value, inplace=True)
        ground_truth_df.dropna(subset=['labels'], inplace=True)
    
    if output_file == None:
        output_file = 'filtered_{}_{}'.format(node_rank, ground_truth.split('/')[-1])

    if save:
        ground_truth_df.to_csv(output_file, index=False)

    return ground_truth_df

def _has_children_in_list(mids, ontology):
    '''Returns list of mids who have children in the input list.'''
    output = []
    for mid in mids:
        for cl in ontology:
            if cl['id'] == mid:
                children = set(cl['child_ids'])
        num_children = len(children.intersection(set(mids)))
        if num_children > 0:
            output.append(mid)
    return output

def unsmear_labels(ground_truth, vocabulary, audioset_ontology, output_file=None, save=False):
    '''
    Unsmears labels from an FSD50K ground truth csv.
    Certain labels imply other labels (e.g. all clips labeled "Electric guitar"
    will automatically be labeled "Music". Unsmearing removes these automatically applied labels
    , only keeping the original label.)

    Inputs
    ------
    ground_truth : path to csv file with FSD50K ground truth labels
    vocabulary : path to FSD50K vocabulary csv file. 
    audioset_ontology : path to audioset ontology json file
    output_file : path to the file where the unsmeared dataframe should be saved
    save : bool, set to True to save the unsmeared dataframe

    Outputs
    -------
    ground_truth_df : FSD50K ground truth dataframe with unsmeared labels
    '''

    fsd_vocab = pd.read_csv(vocabulary, header=None,
                            names= ['id', 'name', 'mids'])

    ground_truth_df = pd.read_csv(ground_truth)

    with open(audioset_ontology, 'r') as f:
        audioset_ontology = json.load(f)

    filtered_labels = []
    for i in range(len(ground_truth_df)):
        mids = ground_truth_df['mids'].iloc[i]
        # Convert to list
        mids = mids.split(',')
        # For each mid, check if they have children already in the list.
        #  If they have at least one, remove them.
        parents = _has_children_in_list(mids, audioset_ontology)
        remainder = list(set(mids).difference(set(parents)))

        # Convert remainder back to labels
        labels = fsd_vocab[fsd_vocab['mids'].isin(remainder)]['name'].to_list()
        labels = ','.join(labels)
        filtered_labels.append(labels)

    ground_truth_df.drop('labels', axis=1, inplace=True)
    ground_truth_df['labels'] = filtered_labels

    if output_file == None:
        output_file = 'unsmeared_{}'.format(ground_truth.split('/')[-1])

    if save:
        ground_truth_df.to_csv(output_file, index=False)

    return ground_truth_df
            
def _filter_samples_by_class(df, classes_to_keep):
    '''Filter a dataframe to only keep samples which have the desired classes
       Inputs
       ------
       df : Pandas DataFrame, dataframe to perform filtering on
       classes_to_keep : list of str, list of the classes to keep after filtering
       
       Outputs
       -------
       df : pandas.Dataframe, filtered dataframe'''

    splitter = splitter = lambda s : s.split(',')
    # Have to use sets instead of doing substring match with regex because
    # if some class is a substring of another class, the latter would fail
    to_keep = df['labels'].apply(splitter).apply(set(classes_to_keep).isdisjoint)
    # Invert the boolean series
    to_keep = ~to_keep

    df = df[to_keep]

    return df


def make_model_zoo_compatible(path_to_csv,
                              classes_to_keep=None,
                              only_keep_monolabel=True, 
                              collapse_to_monolabel=False,
                              preferred_collapse_classes=None,
                              output_file=None,
                              save=False,
                              quick_hack=False):
    '''Makes the input csv compatible with the ST model zoo. Renames two columns, and has
       the option to only keep monolabel files.
       
       Inputs
       ------
       path_to_csv : PosixPath, path to the csv you want to load
       classes_to_keep : List of str, list of the classes you want to keep.
                         Set to None to keep everything.
       only_keep_monolabel : bool, if set to True we discard all samples which have multiple labels.
                             Make sure you only apply this to an unsmeared csv otherwise it will make
                             no sense
       collapse_to_monolabel : bool. If set to True, we collapse all multi_label sample to monolabel
                                     by picking a sample at random.
                                     Make sure to only apply this to an unsmeared csv
       output_file : PosixPath, path to the output file to save the resulting dataframe in
       save : bool, set to True to save the resulting dataframe.
       
       Outputs
       -------
       df : Dataframe in ESC format. '''
    
    df = pd.read_csv(path_to_csv)

    if classes_to_keep:
        df = _filter_samples_by_class(df, classes_to_keep=classes_to_keep)
    splitter = lambda s : s.split(',')

    if only_keep_monolabel:
        df = df[~df['labels'].str.contains(',')]
        
    elif collapse_to_monolabel:
        if preferred_collapse_classes is None:
            if classes_to_keep is None:
                raise ValueError("If collapse_to_monolabel is true, \
                                  at least one of classes_to_keep or preferred_collapse_classes must be specified ")
            preferred_collapse_classes = classes_to_keep
        seed = 42 # For reproducibility
        rng = np.random.default_rng(seed=seed)
        intersecter = lambda li : list(set(preferred_collapse_classes).intersection(li))
        # Frankenstein monster of a code line
        df['labels'] = df['labels'].apply(splitter).apply(intersecter).apply(rng.choice)

    # Convert labels to list if we didn't collapse to monolabel or discard multilabel
    if not only_keep_monolabel and not collapse_to_monolabel:
        df['labels'] = df['labels'].apply(splitter)
    
    # Rename columns
    mapper = {'fname':'filename', 'labels':'category'}
    df.rename(columns=mapper, inplace=True)

    # Convert dtype of filename column to str because apparently it's np.int64 by default 
    df['filename'] = df['filename'].astype('str')
    appender = lambda s : s + '.wav'
    if quick_hack:
        df['filename'] = df['filename'].apply(appender)

    # Save resulting df
    if output_file == None:
        output_file = 'model_zoo_ready_{}'.format(path_to_csv.split('/')[-1])

    if save:
        df.to_csv(output_file, index=False)

    return df


