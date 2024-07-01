#!/bin/sh
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

is_dcmipp_present() {
    DCMIPP_SENSOR="NOTFOUND"
    # on disco board ov5640 camera can be present on csi connector
    for video in $(find /sys/class/video4linux -name "video*" -type l);
    do
        if [ "$(cat $video/name)" = "dcmipp_main_capture" ]; then
            cd $video/device/
            mediadev=/dev/$(ls -d media*)
            cd -
            for sub in $(find /sys/class/video4linux -name "v4l-subdev*" -type l);
            do
                subdev_name=$(tr -d '\0' < $sub/name | awk '{print $1}')
                if [ "$subdev_name" = "ov5640" ] || [ "$subdev_name" = "imx335" ]; then
                    DCMIPP_SENSOR=$subdev_name
                    V4L_DEVICE="device=/dev/$(basename $video)"
                    sensorsubdev="$(tr -d '\0' < $sub/name)"
                    sensordev=$(media-ctl -d $mediadev -p -e "$sensorsubdev" | grep "node name" | awk -F\name '{print $2}')
                    #interface is connected to input of isp (":1 [ENABLED" with media-ctl -p)
                    interfacesubdev=$(media-ctl -d $mediadev -p -e "dcmipp_main_isp" | grep ":1 \[ENABLED" | awk -F\" '{print $2}')
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
        if [  $(cat $video/name | grep -q "dcmi";echo $?) -ne 0 ] &&  [ $(cat $video/name | grep -q "stm";echo $?) -ne 0 ]; then
            WEBCAM_found="FOUND"
            break;
        fi
    done
}

# ------------------------------
#         main
# ------------------------------

# camera detection
# detect if we have a ov5640 or imx335 plugged and associated to dcmipp
echo "check if a CSI or USB camera is connected"
is_dcmipp_present
if [ "$DCMIPP_SENSOR" != "NOTFOUND" ]; then
    echo "dcmipp found"
    exit 0
fi
get_webcam_device
if [ "$WEBCAM_found" = "FOUND" ]; then
    echo "webcam found"
    exit 0
fi
exit 1
