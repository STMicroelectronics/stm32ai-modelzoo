# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../common/utils/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../common/training/'))
from plot_learning_rate_schedule import plot_learning_rate_schedule


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, default='', help='Path to folder containing the configuration file')
    parser.add_argument('--config-name', type=str, default='user_config.yaml', help='Name of the configuration file')
    parser.add_argument("--fname", type=str, default="",  help="Path to output plot file (.png or any other format supported by matplotlib savefig())")
    args = parser.parse_args()
    
    #config_file_path = os.path.join(os.pardir, args.config_file)
    config_file_path = os.path.join(args.config_path, args.config_name)
    if not os.path.isfile(config_file_path):
        raise ValueError(f"\nUnable to find the YAML configuration file\nReceived path: {args.config_name}")
    fname = args.fname if args.fname else None

    # Call plot_learning_rate_schedule common routine 
    plot_learning_rate_schedule(config_file_path = config_file_path,
                                fname = fname)


if __name__ == '__main__':
    main()
