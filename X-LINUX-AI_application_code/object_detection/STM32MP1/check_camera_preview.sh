#!/bin/sh
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

is_dcmipp_present() {
    DCMIPP_PRESENT="NOTFOUND"
    # on disco board gc2145 or ov5640 camera can be present on csi connector
    for video in $(find /sys/class/video4linux -name "video*" -type l);
    do
        if [ "$(cat $video/name)" = "dcmipp_dump_capture" ]; then
            for sub in $(find /sys/class/video4linux -name "v4l-subdev*" -type l);
            do
                subdev_name=$(tr -d '\0' < $sub/name | awk '{print $1}')
                if [ "$subdev_name" = "gc2145" ] || [ "$subdev_name" = "ov5640" ]; then
                    DCMIPP_PRESENT="FOUND"
                    return
                fi
            done
        fi
    done
}

get_webcam_device() {
    WEBCAM_found="NOTFOUND"
    for video in $(find /sys/class/video4linux -name "video*" -type l | sort);
    do
        if [ ! "$(cat $video/name)" = "dcmipp_dump_capture" ]; then
            WEBCAM_found="FOUND"
            break;
        fi
    done
}

# ------------------------------
#         main
# ------------------------------

# camera detection
# detect if we have a gc2145 or ov5640 plugged and associated to dcmipp
is_dcmipp_present
if [ "$DCMIPP_PRESENT" = "FOUND" ]; then
    exit 0
fi
get_webcam_device
if [ "$WEBCAM_found" = "FOUND" ]; then
    exit 0
fi
exit 1
