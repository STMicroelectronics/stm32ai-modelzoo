# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os

import numpy as np
import pandas as pd
import tensorflow as tf
from preprocessing import gravity_rotation
from scipy import stats
# library to generate filter for gravity rotation and preprocessing
from scipy.signal import butter
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
# to one hot code the labels
from tensorflow.keras.utils import to_categorical
from tqdm import tqdm


class WISDM:
    def __init__(self, cfg, reducedClasses=True):
        if not os.path.exists(cfg.dataset.training_path):
            raise ValueError(f"the path provided for the WISDM dataset does not appear to exist\
                please check the wisdm.yaml file and provide a valid path! \n path provided: {cfg.dataset.training_path}")
        self.location = cfg.dataset.training_path
        self.seq_len = cfg.pre_processing.segment_len
        self.seq_step = cfg.pre_processing.segment_step
        self.preprocessing = cfg.pre_processing.preprocessing
        self.classes = cfg.dataset.class_names
        self.batch_size = cfg.tf_train_parameters.batch_size
        self.train_test_split = 0.8
        self.train_valid_split = 0.8
        self.reducedClasses = reducedClasses
        self.to_cache = True
        self.model_type = cfg.model.model_type.name

    def split_train_test_data(self, dataset):
        # split train and test dataset with trainTestSplit proportion.
        # (trainTestSplit out of 1 stay as train)
        datasetTrain = dataset[0: int(dataset.shape[0] * self.train_test_split)]
        datasetTest = dataset[int(
            dataset.shape[0] * self.train_test_split): int(dataset.shape[0])]
        return datasetTrain, datasetTest

    def clean_csv(self):

        # read data file
        fin = open(self.location, "rt")

        # read file contents to string
        data = fin.read()

        # fix all problems by replacing ';\n' with '\n's etc
        data = data.replace(';\n', '\n').replace(
            '\n;\n', '\n').replace(';', '\n').replace(',\n', '\n')

        # close the data file
        fin.close()

        # open the data file in write mode
        fin = open(self.location, "wt")

        # overrite the data file with the correct data
        fin.write(data)

        # close the file
        fin.close()

    def read_dataset(self):
        # read all the data in csv 'WISDM_ar_v1.1_raw.txt' into a dataframe
        #  called dataset
        columns = ['User', 'Activity_Label', 'Arrival_Time',
                   'x', 'y', 'z']  # headers for the columns
        self.clean_csv()
        dataset = pd.read_csv(self.location, header=None,
                              names=columns, delimiter=',')

        # removing the ; at the end of each line and casting the last variable
        #  to datatype float from string
        dataset['z'] = [float(str(char).replace(";", "")) for char in dataset['z']]

        # remove the user column as we do not need it
        dataset = dataset.drop('User', axis=1)

        # as we are workign with numbers, let us replace all the empty columns
        # entries with NaN (not a number)
        dataset.replace(to_replace='null', value=np.NaN)

        # remove any data entry which contains NaN as a member
        dataset = dataset.dropna(axis=0, how='any')
        if self.reducedClasses:
            dataset['Activity_Label'] = ['Stationary' if activity == 'Standing' or activity == 'Sitting' else activity
                                         for activity in dataset['Activity_Label']]
            dataset['Activity_Label'] = ['Stairs' if activity == 'Upstairs' or activity == 'Downstairs' else activity
                                         for activity in dataset['Activity_Label']]

        # removing the columns for time stamp and rearranging remaining columns
        dataset = dataset[['x', 'y', 'z', 'Activity_Label']]
        # dataset = dataset[dataset.Activity_Label != 'Stairs']
        datasetTrain, datasetTest = self.split_train_test_data(dataset)
        return datasetTrain, datasetTest

    def preprocess_data(self, data):

        # choose a sample frequency
        # hardcoding to have code equivalency with C-implementation (WISDM has 20 Hz)
        fSample = 26

        if self.preprocessing:
            # create a copy of data to avoid overwriting the passed dataframe
            datacopy = data.copy()
            # create highpass filter to remove dc components
            fCut = 0.4
            filterType = 'highpass'
            fNorm = fCut / fSample
            num, den = butter(4, fNorm, btype=filterType)

            # preprocess the dataset by finding and rotating the gravity axis
            data_x = datacopy[datacopy.columns[: 3]]

            datacopy[datacopy.columns[: 3]] = gravity_rotation(
                np.array(data_x, dtype=float), A_COEFF=den, B_COEFF=num)
            return datacopy
        else:
            return data

    def get_segment_indices(self, dataColumn):

        # get segment indices to window the data into overlapping frames
        init = 0
        while init < len(dataColumn):
            yield int(init), int(init + self.seq_len)
            init = init + self.seq_step

    def get_data_segments(self, dataset):

        # segmentng the data into overlaping frames
        dataIndices = dataset.index.tolist()
        nSamples = len(dataIndices)
        segments = []
        labels = []

        # need the following variable for tqdm to show the progress bar
        numSegments = int(np.floor((nSamples - self.seq_len) / self.seq_step)) + 1

        # creating segments until the get_segment_indices keep on yielding the start and end of the segments
        for (init, end) in tqdm(self.get_segment_indices(dataIndices), unit=' segments', desc='Segments built ', total=numSegments):

            # check if the nr of remaing samples are enough to create a frame
            if (end < nSamples):
                segments.append(np.transpose([dataset['x'].values[init: end],
                                dataset['y'].values[init: end],
                                dataset['z'].values[init: end]]))

                # use the label which occured the most in the frame
                labels.append(stats.mode(dataset['Activity_Label'][init: end])[0][0])

        # converting the segments from list to numpy array
        segments = np.asarray(segments, dtype=np.float)
        labels = np.asarray(labels)
        return segments, labels

    def reshape_sequences(self, sequences, labels, split=False):
        # this function reshapes the sequences into a shape which is acceptable by tensorflow
        # i.e. channel_last
        # it also enocdes the class labels into one_hot_code
        # finally it splits the data into train and validation parts using trainValidSplit
        # proportions suplied by the user

        # reshaping the sequences to generate tensors with channel last configuration
        reshaped_sequences = sequences.reshape(
            sequences.shape[0], sequences.shape[1], sequences.shape[2], 1)

        # one hot code the labels
        labels = to_categorical([self.classes.index(label)
                                for label in labels], num_classes=len(self.classes))
        if split:
            # splitting train and validation data
            validation_x, train_x, validation_y, train_y = train_test_split(reshaped_sequences, labels,
                                                                            test_size=self.train_valid_split, shuffle=True, random_state=611)
            return train_x, train_y, validation_x, validation_y
        else:
            return reshaped_sequences, labels

    def prepare_data(self, load_from_memory=False):

        # this function prepares the dataset for training, validation and testing by generating

        # read public datasets
        datasetTrain, datasetTest = self.read_dataset()

        # preprocess train and test datasets
        datasetTrainPreprocessed = self.preprocess_data(datasetTrain)
        datasetTestPreprocessed = self.preprocess_data(datasetTest)

        # segment train and test datasets
        print('[INFO] : Segmenting Train data')
        (sequencesTrain, labelsTrain) = self.get_data_segments(datasetTrainPreprocessed)

        print('[INFO] : Segmenting Test data')
        (sequencesTest, labelsTest) = self.get_data_segments(datasetTestPreprocessed)

        print('[INFO] : Segmentation finished!')

        # reshape sequences
        train_x, train_y, validation_x, validation_y = self.reshape_sequences(
            sequencesTrain, labelsTrain, split=True)
        test_x, test_y = self.reshape_sequences(sequencesTest, labelsTest)

        # shuffle the data
        train_x, train_y = shuffle(train_x, train_y, random_state=611)
        test_x, test_y = shuffle(test_x, test_y, random_state=611)
        validation_x, validation_y = shuffle(
            validation_x, validation_y, random_state=611)

        self.train_x = train_x
        self.train_y = train_y
        self.validation_x = validation_x
        self.validation_y = validation_y
        self.test_x = test_x
        self.test_y = test_y
        ''' Check if creating a SVC or other models.
        if it is an svc change the shapes of the data ( nr_samples, step_size * nr_axis )
        if not keep the data in ( nr_samples, step_size, nr_axis, 1 )
        '''
        if self.model_type == 'svc':
            # vectroizing the inputs
            self.train_x = self.train_x.reshape((self.train_x.shape[0], -1))
            self.test_x = self.test_x.reshape((self.test_x.shape[0], -1))
            self.validation_x = self.validation_x.reshape(
                (self.validation_x.shape[0], -1))

            # decoding to the class id from one-hot code
            self.train_y = np.argmax(self.train_y, axis=1).astype(np.int16)
            self.test_y = np.argmax(self.test_y, axis=1).astype(np.int16)
            self.validation_y = np.argmax(self.validation_y, axis=1).astype(np.int16)

    def get_dataset(self):

        # Prepare the train/val/test dataset
        self.prepare_data()

        train_ds = tf.data.Dataset.from_tensor_slices((self.train_x, self.train_y))
        train_ds = train_ds.shuffle(self.train_x.shape[0], reshuffle_each_iteration=True, seed=123).batch(self.batch_size)

        valid_ds = tf.data.Dataset.from_tensor_slices(
            (self.validation_x, self.validation_y)).batch(self.batch_size)
        test_ds = tf.data.Dataset.from_tensor_slices(
            (self.test_x, self.test_y)).batch(self.batch_size)

        if self.to_cache:
            train_ds = train_ds.cache()
            valid_ds = valid_ds.cache()
            test_ds = test_ds.cache()

        train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
        valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
        test_ds = test_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

        return train_ds, valid_ds, test_ds
