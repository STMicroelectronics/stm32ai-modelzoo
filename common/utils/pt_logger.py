# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import logging.config

KB_IN_MB_COUNT = 1024
LOGGING_NAME = 'stm32ai'
NUM_THREADS = min(8, max(1, os.cpu_count() - 1))
TQDM_BAR_FORMAT = '{l_bar}{bar:10}{r_bar}'


def set_logging(name=LOGGING_NAME, verbose=True):
    # sets up logging for the given name
    rank = int(os.getenv('RANK', "-1"))  # rank in world for Multi-GPU trainings
    level = logging.INFO if verbose and rank in {-1, 0} else logging.ERROR
    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {name: {'format': '%(message)s'}},
            'handlers': {
                name: {
                    'class': 'logging.StreamHandler',
                    'formatter': name,
                    'level': level,
                }
            },
            'loggers': {
                name: {
                    'level': level,
                    'handlers': [name],
                    'propagate': False,
                }
            },
        }
    )

set_logging(LOGGING_NAME)  # run before defining LOGGER
LOGGER = logging.getLogger(LOGGING_NAME)  # define globally