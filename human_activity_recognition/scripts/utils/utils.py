# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import json
import os
import random

import load_models
# from math import gamma
import mlflow
import numpy as np
import optuna
import sklearn
import tensorflow as tf
from common_benchmark import Cloud_benchmark, Cloud_analyze, benchmark_model, stm32ai_benchmark
from benchmark import evaluate_TFlite_quantized_model
from callbacks import get_callbacks
from datasets import WISDM
from google.protobuf.json_format import MessageToJson
from header_file_generator import gen_h_user_file
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import OmegaConf
from quantization import TFLite_PTQ_quantizer
from skl2onnx import to_onnx
from sklearn.decomposition import TruncatedSVD as TSVD
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from tensorflow import keras
from common_visualize import vis_training_curves
from visualize import (plot_confusion_matrix, training_confusion_matrix)


# Set seeds
def setup_seed(seed=611):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)  # tf cpu fix seed


def svm_model_conversion_to_onnx(clf, train_x, onx_out_file, onx_json_file):

    onx = to_onnx(clf, train_x[:1].astype(np.float32), options={'zipmap': False})
    with open(onx_out_file, "wb") as f:
        f.write(onx.SerializeToString())
    s = MessageToJson(onx)
    onx_json = json.loads(s)
    json.dumps(onx_json)
    with open(onx_json_file, 'w') as outfile:
        json.dump(onx_json, outfile, indent=4, ensure_ascii=False)


def get_config(cfg):

    config_dict = OmegaConf.to_container(cfg)
    configs = DefaultMunch.fromDict(config_dict)
    return configs


def mlflow_ini(cfg):
    print('[INFO] : Configuring ML-Flow')
    mlflow.set_tracking_uri(cfg.mlflow.uri)
    mlflow.set_experiment(cfg.general.project_name)
    mlflow.set_tag("mlflow.runName", HydraConfig.get().runtime.output_dir.split(os.sep)[-1])
    mlflow.tensorflow.autolog(log_models=False)


def get_optimizer(cfg):

    if cfg.tf_train_parameters.optimizer.lower() == "sgd":
        optimizer = keras.optimizers.SGD(learning_rate=cfg.train_parameters.initial_learning)
    elif cfg.tf_train_parameters.optimizer.lower() == "rmsprop":
        optimizer = keras.optimizers.RMSprop(learning_rate=cfg.tf_train_parameters.initial_learning)
    elif cfg.tf_train_parameters.optimizer.lower() == "adam":
        optimizer = keras.optimizers.Adam(learning_rate=cfg.tf_train_parameters.initial_learning)
    else:
        optimizer = keras.optimizers.Adam(learning_rate=cfg.tf_train_parameters.initial_learning)
    return optimizer


def get_loss(cfg):
    num_classes = len(cfg.dataset.class_names)
    if num_classes > 2:
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    return loss


def svm_optimization(train_x, train_y, dim_red=True, n_components=20, svc_C=[100, 1000], svc_Gamma=[0.001, 0.005], opt_data_keep=0.05):
    train_inds = random.choices(
        np.arange(0, len(train_y)), k=int(len(train_y) * opt_data_keep))
    train_data, train_labels = train_x[train_inds], train_y[train_inds]

    def svm_objective(trial):
        svc_c = trial.suggest_int(
            name='svc_c', low=svc_C[0], high=svc_C[1], step=100)
        svc_gamma = trial.suggest_float(
            name='svc_gamma', low=svc_Gamma[0], high=svc_Gamma[1], step=0.0005)

        if dim_red:
            dim_reduction = TSVD(n_components=n_components, random_state=611)
            classifier_obj = Pipeline([
                            ('dim_reduction', dim_reduction),
                            ('svc', SVC(C=svc_c, gamma=svc_gamma, probability=True))
                        ])
        else:
            classifier_obj = SVC(C=svc_c, gamma=svc_gamma, probability=True)

        score = sklearn.model_selection.cross_val_score(
            classifier_obj, train_data, train_labels, n_jobs=-1, cv=5)
        accuracy = round(score.mean(), 3)
        return accuracy

    study = optuna.create_study(direction='maximize')
    study.optimize(svm_objective, n_trials=50)
    classifier_obj = Pipeline([
            ('dim_reduction', TSVD(n_components=n_components, random_state=611)),
            ('svc', SVC(C=study.best_trial.params['svc_c'], gamma=study.best_trial.params['svc_gamma'], probability=True))
        ])
    classifier_obj.fit(train_data, train_labels)
    return classifier_obj, study.best_trial


def train_svc(cfg):
    if not cfg.dataset.name == 'wisdm':
        print('[ERROR] : DATASET not Supproted!')
        print('[ERROR] : Only widsm dataset is supported now, link to download : ')
        print('[Error] : link to download:')
        print('[ERROR] : https://www.cis.fordham.edu/wisdm/includes/datasets/latest/WISDM_ar_latest.tar.gz')
        return

    # create the data handler project
    data_handler = WISDM(cfg)
    data_handler.prepare_data()
    train_x = data_handler.train_x
    train_y = data_handler.train_y
    test_x = data_handler.test_x
    test_y = data_handler.test_y

    print('[INFO] : Training SVC ...')
    clf = SVC(probability=True)
    clf.fit(train_x, train_y)
    train_pred = clf.predict(train_x)
    test_pred = clf.predict(test_x)

    # default SVC
    print('[INFO] : Evaluating default SVC trained with all trainig samples ...')
    print(f'[INFO] : accuracy at training data set : {round( accuracy_score( train_pred, train_y ) * 100, 2 )}')
    print(f'[INFO] : accuracy at testing data set : {round( accuracy_score( test_pred , test_y ) * 100, 2 )}')
    if not os.path.isdir(os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir)):
        os.mkdir(os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir))
    cm = sklearn.metrics.confusion_matrix(test_y, np.argmax(clf.predict_proba(test_x), axis=1))
    plot_confusion_matrix(cm=cm, class_names=cfg.dataset.class_names,
                          model_name='def_svc_confusion_matrix', test_accuracy=round(accuracy_score(test_pred, test_y) * 100, 2))
    mlflow.log_metric("acc_def", round(accuracy_score(test_pred, test_y) * 100, 2))
    print('[INFO] : Saving the fitted model ...')
    save_model_dir = os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir)
    svm_model_conversion_to_onnx(clf, train_x, os.path.join(
        save_model_dir, 'def_svc.onnx'), os.path.join(save_model_dir, 'def_svc.json'))
    print('[INFO] : benchmarking the fitted model ...')
    stm32ai_benchmark(cfg, os.path.join(save_model_dir,'def_svc.onnx'), False)

    # Optimizing the hyper-parameters
    print('[INFO] : Optimizing the SVC with a subsample of the train data ...')
    mlflow.log_param('opt_data_rat', cfg.svc_train_parameters.opt_data_keep)
    classifier_obj, best_trial = svm_optimization(train_x, train_y, dim_red=True, n_components=20, svc_C=[
                                                  100, 1000], svc_Gamma=[0.001, 0.005], opt_data_keep=cfg.svc_train_parameters.opt_data_keep)
    train_pred = classifier_obj.predict(train_x)
    test_pred = classifier_obj.predict(test_x)
    print('[INFO] : Evaluating optimized SVC trained with subset of training samples ...')
    print(f'[INFO] : accuracy at training data set : {round( accuracy_score( train_pred, train_y ) * 100, 2 )}')
    print(f'[INFO] : accuracy at testing data set: {round( accuracy_score( test_pred , test_y ) * 100, 2 )}')
    cm = sklearn.metrics.confusion_matrix(test_y, np.argmax(classifier_obj.predict_proba(test_x), axis=1))
    plot_confusion_matrix(cm=cm, class_names=cfg.dataset.class_names,
                          model_name='opt_svc_confusion_matrix', test_accuracy=round(accuracy_score(test_pred, test_y) * 100, 2))
    mlflow.log_metric("acc_opt", round(accuracy_score(test_pred, test_y) * 100, 2))
    print('[INFO] : Saving the optimized model ...')
    svm_model_conversion_to_onnx(classifier_obj, train_x, os.path.join(save_model_dir, 'opt_svc.onnx'), os.path.join(save_model_dir, 'opt_svc.json'))
    print('[INFO] : benchmarking the fitted model ...')
    # benchmark_svc_model(cfg, 'opt_svc.onnx')
    stm32ai_benchmark(cfg, os.path.join(save_model_dir, 'opt_svc.onnx'), False)

    # Generate Config.h for C embedded application
    gen_h_user_file(cfg)

    # record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()


def train(cfg):

    if not cfg.dataset.name == 'wisdm':
        print('[ERROR] : DATASET not Supproted!')
        print('[ERROR] : Only widsm dataset is supported now, link to download : ')
        print('[ERROR] : link to download:')
        print('[ERROR] : https://www.cis.fordham.edu/wisdm/includes/datasets/latest/WISDM_ar_latest.tar.gz')
        return

    # get ANN (IGN or GMP) model
    model = load_models.get_model(cfg)
    model.summary()

    # get datasets
    data_handler = WISDM(cfg)
    train_ds, valid_ds, test_ds = data_handler.get_dataset()

    # get loss
    loss = get_loss(cfg)

    # get optimizer
    optimizer = get_optimizer(cfg)

    # get callbacks
    callbacks = get_callbacks(cfg)

    # compile the model
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    # estimate the model footprints
    print("[INFO] : Estimating the model footprints...")
    if cfg.quantization.quantize:
        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, model, train_ds=None, fake=True)
            model_path = os.path.join(HydraConfig.get().runtime.output_dir, f"{cfg.quantization.export_dir}", "quantized_model.tflite")
        else:
            raise TypeError("Quantizer and quantization type not supported yet!")
    else:
        model_path = os.path.join(HydraConfig.get().runtime.output_dir, f"{cfg.general.saved_models_dir}", "best_model.h5")
        model.save(model_path)

    # Evaluate model footprints with STM32Cube.AI
    if cfg.stm32ai.footprints_on_target:
        print("[INFO] : Establishing connection with STM32Cube.AI Developer Cloud to launch the model benchmark on STM32 target...")
        try:
            output_analyze = Cloud_analyze(cfg, model_path)
            if output_analyze == 0:
                raise Exception("Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
        except Exception as e:
            output_analyze = 0
            print("[FAIL] : ", e)
            print("[INFO] : Offline benchmark launched...")
            benchmark_model(cfg, model_path)

    else:
        benchmark_model(cfg, model_path)

    # train the model
    print("[INFO] : Starting training...")
    history = model.fit(train_ds, validation_data=valid_ds,
                        callbacks=callbacks, epochs=cfg.tf_train_parameters.training_epochs)
    # visualize training curves
    vis_training_curves(history, cfg)

    # evaluate the float model on test set
    best_model = tf.keras.models.load_model(os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir, "best_model.h5"))

    # generate the confusion matrix for the float model
    training_confusion_matrix(test_ds, best_model, cfg.dataset.class_names)

    # quantize the model with training data
    if cfg.quantization.quantize:
        print("[INFO] : Quantizing the model ... This might take few minutes ...")

        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, best_model, train_ds, fake=False)
            quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir, f"{cfg.quantization.export_dir}", "quantized_model.tflite")
            
            if cfg.stm32ai.footprints_on_target:
                try:
                    if output_analyze != 0:
                        output_benchmark = Cloud_benchmark(cfg, quantized_model_path, output_analyze)
                        if output_benchmark == 0:
                            raise Exception("Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                    else:
                        raise Exception("Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                except Exception as e:
                    print("[FAIL] :", e)
                    print("[INFO] : Offline benchmark launched...")
                    benchmark_model(cfg, quantized_model_path)
            else:
                benchmark_model(cfg, quantized_model_path)

            # evaluate the quantized model
            if cfg.quantization.evaluate:
                q_acc = evaluate_TFlite_quantized_model(quantized_model_path, test_ds, cfg)
                mlflow.log_metric("int_test_acc", q_acc)

        else:
            raise TypeError("Quantizer and quantization type not supported yet!")

        # Generate Config.h for C embedded application
        gen_h_user_file(cfg)

    # record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()
