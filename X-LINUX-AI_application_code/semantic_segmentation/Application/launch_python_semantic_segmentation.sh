#!/bin/sh
weston_user=$(ps aux | grep '/usr/bin/weston '|grep -v 'grep'|awk '{print $1}')
DEPLOY_PATH=$1
MODEL_NAME=$2
LABELS=$3
COMPATIBLE=$(cat /proc/device-tree/compatible)

cmd="python3 $DEPLOY_PATH/Application/semantic_segmentation.py -m $DEPLOY_PATH/$MODEL_NAME -l $DEPLOY_PATH/Resources/$LABELS --framerate 30 --frame_width 640 --frame_height 480"

if [ "$weston_user" != "root" ]; then
	echo "user : "$weston_user
	script -qc "su -l $weston_user -c '$cmd'"
else
	$cmd
fi
