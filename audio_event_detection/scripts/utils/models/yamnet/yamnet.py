# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from pathlib import Path
from ..model_utils import add_head
from keras import layers
from keras import regularizers

def get_pretrained_model(cfg):
    # Load model
    yamnet_backbone = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
                         'yamnet_{}_f32.h5'.format(str(cfg.model.model_type.embedding_size))))
    print("Backbone layers")
    print(yamnet_backbone.layers)
    # Add permutation layer
    inp = layers.Input(shape=(64, 96, 1))
    x = layers.Permute((2, 1, 3))(inp)
    out = yamnet_backbone(x)
    permuted_backbone = tf.keras.models.Model(inputs=inp, outputs=out)

    # Add head
    n_classes = len(cfg.dataset.class_names)
    if cfg.dataset.use_other_class:
        n_classes += 1
        
    if cfg.model.multi_label:
        activation = 'sigmoïd'
    else:
        activation ='softmax'

    yamnet = add_head(backbone=permuted_backbone,
                         n_classes=n_classes,
                         trainable_backbone=cfg.model.fine_tune,
                         add_flatten=False,
                         functional=True,
                         activation=activation,
                         kernel_regularizer=regularizers.L2(0),
                         activity_regularizer=regularizers.L1(0),
                         dropout=cfg.model.dropout)
                         
    return yamnet