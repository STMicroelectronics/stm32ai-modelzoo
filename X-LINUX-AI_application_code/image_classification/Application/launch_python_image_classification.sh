#!/bin/sh
weston_user=$(ps aux | grep '/usr/bin/weston '|grep -v 'grep'|awk '{print $1}')
DEPLOY_PATH=$1
MODEL_NAME=$2
LABELS=$3
COMPATIBLE=$(cat /proc/device-tree/compatible)
if [[ "$COMPATIBLE" == *"stm32mp2"* ]]; then
	cmd="python3 $DEPLOY_PATH/Application/image_classification.py -m $DEPLOY_PATH/$MODEL_NAME -l $DEPLOY_PATH/Resources/$LABELS --framerate 30 --frame_width 640 --frame_height 480"
else
	cmd="python3 $DEPLOY_PATH/Application/image_classification.py -m $DEPLOY_PATH/$MODEL_NAME -l $DEPLOY_PATH/Resources/$LABELS --framerate 15 --frame_width 320 --frame_height 240"
fi

if [ "$weston_user" != "root" ]; then
	echo "user : "$weston_user
	script -qc "su -l $weston_user -c '$cmd'"
else
	$cmd
fi
