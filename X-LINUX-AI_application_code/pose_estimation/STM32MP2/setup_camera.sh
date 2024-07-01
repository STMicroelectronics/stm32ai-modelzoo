#!/bin/bash
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

WIDTH=$1
HEIGHT=$2
FPS=$3
RQ_NN_WIDTH=$4
RQ_NN_HEIGHT=$5
DEVICE=$6
FMTdisplay=RGB16
FMTnn=RGB
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
displaybuscode=RGB565_2X8_LE
nnbuscode=RGB888_1X24

function cmd() {
	cmd=$1
	eval $cmd > /dev/null 2>&1
}

function is_dcmipp_present() {
	DCMIPP_SENSOR="NOTFOUND"
	# on disco board ov5640 camera can be present on csi connector
	for video in $(find /sys/class/video4linux -name "video*" -type l);
	do
        if [ "$(cat $video/name)" = "dcmipp_aux_capture" ]; then
            V4L_DEVICE_PREV="$(basename $video)"
            echo "V4L_DEVICE_PREV="$V4L_DEVICE_PREV
        fi
		if [ "$(cat $video/name)" = "dcmipp_main_capture" ]; then
			cd $video/device/
			mediadev=/dev/$(ls -d media*)
			cd -
			for sub in $(find /sys/class/video4linux -name "v4l-subdev*" -type l);
			do
				subdev_name=$(tr -d '\0' < $sub/name | awk '{print $1}')
				if [ "$subdev_name" = "ov5640" ] || [ "$subdev_name" = "imx335" ]; then
					DCMIPP_SENSOR=$subdev_name
					V4L_DEVICE="$(basename $video)"
					sensorsubdev="$(tr -d '\0' < $sub/name)"
					sensordev=$(media-ctl -d $mediadev -p -e "$sensorsubdev" | grep "node name" | awk -F\name '{print $2}')
					#interface is connected to input of isp (":1 [ENABLED" with media-ctl -p)
					interfacesubdev=$(media-ctl -d $mediadev -p -e "dcmipp_input" | grep ":1 \[ENABLED" | awk -F\" '{print $2}')
				fi
			done
		fi
	done
}

function get_webcam_device() {
    found="NOTFOUND"
    for video in $(find /sys/class/video4linux -name "video*" -type l | sort);
    do
        if [ "$(cat $video/name)" = "dcmipp_main_capture" ] || [ "$(cat $video/name)" = "st,stm32mp25-vdec-dec" ] || [ "$(cat $video/name)" = "st,stm32mp25-venc-enc" ] || [ "$(cat $video/name)" = "dcmipp_dump_capture" ] || [ "$(cat $video/name)" = "dcmipp_aux_capture" ] || [ "$(cat $video/name)" = "dcmipp_main_isp_stat_capture" ] ; then
            found="FOUND"
        else
            V4L_DEVICE="$(basename $video)"
            break;
        fi
    done
}

# ------------------------------
#         main
# ------------------------------

if [ -z "$RQ_NN_WIDTH" ] || [ -z "$RQ_NN_HEIGHT" ]; then
	echo "No NN resolution specified use single DCMIPP pipeline"
	dual_pipe=0
else
	echo "NN resolution specified use dual DCMIPP pipelines"
	dual_pipe=1
fi

#if a video device is specified in the launch script use it if not search for
#dcmipp camera of a webcam
if [ "$DEVICE" != "" ]; then
	echo "A video device has been specified"
	DCMIPP_SENSOR="NOTFOUND"
	for video in $(find /sys/class/video4linux -name "video*" -type l);
	do
        if [ "$(cat $video/name)" = "dcmipp_aux_capture" ]; then
            V4L_DEVICE_PREV="$(basename $video)"
            echo "V4L_DEVICE_PREV="$V4L_DEVICE_PREV
		fi
	done
	if [ "$(cat /sys/class/video4linux/$DEVICE/name)" = "dcmipp_dump_capture" ] || [ "$(cat /sys/class/video4linux/$DEVICE/name)" = "dcmipp_main_capture" ] ; then
		cd /sys/class/video4linux/$DEVICE/device/
		mediadev=/dev/$(ls -d media*)
		cd -
		for sub in $(find /sys/class/video4linux -name "v4l-subdev*" -type l);
		do
			subdev_name=$(tr -d '\0' < $sub/name | awk '{print $1}')
			if [ "$subdev_name" = "imx335" ] || [ "$subdev_name" = "ov5640" ]; then
				DCMIPP_SENSOR=$subdev_name
				echo "DCMIPP_SENSOR="$DCMIPP_SENSOR
				V4L_DEVICE="$(basename $DEVICE)"
				sensorsubdev="$(tr -d '\0' < $sub/name)"
				sensordev=$(media-ctl -d $mediadev -p -e "$sensorsubdev" | grep "node name" | awk -F\name '{print $2}')
				#interface is connected to input of isp (":1 [ENABLED" with media-ctl -p)
				interfacesubdev=$(media-ctl -d $mediadev -p -e "dcmipp_input" | grep ":1 \[ENABLED" | awk -F\" '{print $2}')
			fi
		done
	else
		if [ "$(cat /sys/class/video4linux/$DEVICE/name)" != "dcmipp_dump_capture" ] || [ "$(cat /sys/class/video4linux/$DEVICE/name)" != "dcmipp_main_capture" ] ; then
			V4L_DEVICE="$(basename $DEVICE)"
		else
			echo "camera specified not valid ... try to find another camera"
			is_dcmipp_present
		fi
	fi
	echo "DCMIPP_SENSOR="$DCMIPP_SENSOR
else
	is_dcmipp_present
	echo "DCMIPP_SENSOR="$DCMIPP_SENSOR
fi

if [ "$DCMIPP_SENSOR" != "NOTFOUND" ]; then
	#Use sensor in raw-bayer format
	sensorbuscode=`v4l2-ctl --list-subdev-mbus-codes -d $sensordev | grep SRGGB | awk -FMEDIA_BUS_FMT_ '{print $2}'`

	if [ "$DCMIPP_SENSOR" = "ov5640" ]; then
		#OV5640 only support 720p with raw-bayer format
		CAMERA_WIDTH=1280
		CAMERA_HEIGHT=720
		#OV5640 claims to support all raw bayer combinations but always output SBGGR8_1X8...
		sensorbuscode=SBGGR8_1X8
	elif [ "$DCMIPP_SENSOR" = "imx335" ]; then
		if [ $dual_pipe -eq 1 ]; then
			aux_postproc=`media-ctl -d $mediadev -e dcmipp_aux_postproc`
			echo "aux_postproc="$aux_postproc
		else
			main_postproc=`media-ctl -d $mediadev -e dcmipp_main_postproc`
			echo "main_postproc="$main_postproc
		fi
	fi

	#Let sensor return its prefered resolution & format
    media-ctl -d $mediadev --set-v4l2 "'$sensorsubdev':0[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}@1/${FPS} field:none]" > /dev/null 2>&1
    sensorfmt=`media-ctl -d $mediadev --get-v4l2 "'$sensorsubdev':0" | awk -F"fmt:" '{print $2}' | awk -F" " '{print $1}'`
    SENSORWIDTH=`echo $sensorfmt | awk -F"/" '{print $2}' | awk -F"x" '{print $1}'`
    SENSORHEIGHT=`echo $sensorfmt | awk -F"/" '{print $2}' | awk -F"x" '{print $2}' | awk -F" " '{print $1}' | awk -F"@" '{print $1}'`

	# echo "sensorsubdev="$sensorsubdev
	# echo "interfacesubdev="$interfacesubdev
	# echo "sensorbuscode="$sensorbuscode

	if [ $dual_pipe -eq 1 ]; then
		#Use main pipe for debayering, scaling and color conversion
		echo "Mediacontroller graph:"

		# Configure the sensor resolution to max resolution (2592x1940)
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'$sensorsubdev':0[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""

		# Configure the Pipe2 to get its input from Pipe1 ISP output
		cmd "  media-ctl -d $mediadev -l '\"dcmipp_main_isp\":1->\"dcmipp_aux_postproc\":0[1]' -v"

		# Same resolution/format (2592x1940) out of the CSI and enter into the DCMIPP
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'$interfacesubdev':1[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""

		# The Main Pipe ISP automatically inherit from the previous setting done on the CSI (since they share a link)
		# However, we first need to perform a first level of decimation to achieve required outputs
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_input':2[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_isp':1[fmt:RGB888_1X24/${SENSORWIDTH}x${SENSORHEIGHT} field:none]\""

		# Configure the Pipe1 postprocessing downscale to NN input resolution
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_postproc':0[compose:(0,0)/${RQ_NN_WIDTH}x${RQ_NN_HEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_postproc':1[fmt:$nnbuscode/${RQ_NN_WIDTH}x${RQ_NN_HEIGHT}]\""

		# Configure Pipe2 PostProcessing to the display resolution
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_aux_postproc':0[compose:(0,0)/${WIDTH}x${HEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_aux_postproc':1[fmt:$displaybuscode/${WIDTH}x${HEIGHT}]\" -v"
		echo ""

		#v4l2-ctl -d /dev/v4l-subdev6 --set-ctrl=horizontal_flip=1
		V4L2_CAPS_PREV="video/x-raw, format=$FMTdisplay, width=$WIDTH, height=$HEIGHT, framerate=$FPS/1"
		V4L2_CAPS_NN="video/x-raw, format=$FMTnn, width=$RQ_NN_WIDTH, height=$RQ_NN_HEIGHT, framerate=$FPS/1"
		V4L_OPT=""
		echo "V4L_DEVICE_PREV="$V4L_DEVICE_PREV
		echo "V4L_DEVICE_NN="$V4L_DEVICE
		echo "V4L2_CAPS_PREV="$V4L2_CAPS_PREV
		echo "V4L2_CAPS_NN="$V4L2_CAPS_NN
		echo "DCMIPP_SENSOR="$DCMIPP_SENSOR
		echo "AUX_POSTPROC="$aux_postproc
	else
		#Use main pipe for debayering, scaling and color conversion
		echo "Mediacontroller graph:"
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'$sensorsubdev':0[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'$interfacesubdev':1[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_input':2[fmt:$sensorbuscode/${SENSORWIDTH}x${SENSORHEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_isp':1[fmt:RGB888_1X24/${SENSORWIDTH}x${SENSORHEIGHT} field:none]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_postproc':0[compose:(0,0)/${WIDTH}x${HEIGHT}]\""
		cmd "  media-ctl -d $mediadev --set-v4l2 \"'dcmipp_main_postproc':1[fmt:$displaybuscode/${WIDTH}x${HEIGHT}]\""
		echo ""

		#v4l2-ctl -d /dev/v4l-subdev6 --set-ctrl=horizontal_flip=1
		V4L2_CAPS="video/x-raw, format=$FMTdisplay, width=$WIDTH, height=$HEIGHT"
		V4L_OPT=""
		echo "V4L_DEVICE_PREV="$V4L_DEVICE
		echo "V4L2_CAPS_PREV="$V4L2_CAPS
		echo "DCMIPP_SENSOR="$DCMIPP_SENSOR
		echo "MAIN_POSTPROC="$main_postproc
	fi

else
	if [ "$DEVICE" = "" ];then
		get_webcam_device
	fi
	# suppose we have a webcam
	V4L2_CAPS="video/x-raw, width=$WIDTH, height=$HEIGHT"
	V4L_OPT="io-mode=4"
	v4l2-ctl --set-parm=20
	echo "V4L_DEVICE_PREV="$V4L_DEVICE
	echo "V4L2_CAPS_PREV="$V4L2_CAPS
fi
