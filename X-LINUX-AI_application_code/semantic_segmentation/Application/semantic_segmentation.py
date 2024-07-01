#!/usr/bin/python3
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf
from gi.repository import Gst

import sys
import numpy as np
import argparse
import signal
import os
import random
import json
import subprocess
import re
import time
import os.path
import math
from os import path
import cv2
from PIL import Image
import PIL
from deeplab_v3_pp import NeuralNetwork
from timeit import default_timer as timer

np.set_printoptions(threshold=np.inf)
#init gstreamer
Gst.init(None)
Gst.init_check(None)
#init gtk
Gtk.init(None)
Gtk.init_check(None)

#path definition
RESOURCES_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) + "/../Resources/"

class GstWidget(Gtk.Box):
    """
    Class that handles Gstreamer pipeline using gtkwaylandsink and appsink
    """
    def __init__(self, app, nn):
         super().__init__()
         # connect the gtkwidget with the realize callback
         self.connect('realize', self._on_realize)
         self.instant_fps = 0
         self.app = app
         self.nn = nn
         self.cpt_frame = 0
         self.isp_first_config = True

    def _on_realize(self, widget):
        if(args.dual_camera_pipeline):
            self.camera_pipeline_preview_creation()
            self.nn_pipeline_creation()
            self.pipeline_preview.set_state(Gst.State.PLAYING)
            self.pipeline_nn.set_state(Gst.State.PLAYING)
        else :
            self.camera_pipeline_creation()

    def camera_pipeline_creation(self):
        """
        Creation of the gstreamer pipeline when gstwidget is created dedicated to handle
        camera stream and NN inference (mode single pipeline)
        """
        # gstreamer pipeline creation
        self.pipeline_preview = Gst.Pipeline()

        # creation of the source v4l2src
        self.v4lsrc1 = Gst.ElementFactory.make("v4l2src", "source")
        video_device = "/dev/" + str(self.app.video_device_prev)
        self.v4lsrc1.set_property("device", video_device)

        #creation of the v4l2src caps
        caps = str(self.app.camera_caps_prev) + ", framerate=" + str(args.framerate)+ "/1"
        print("Camera pipeline configuration : ",caps)
        camera1caps = Gst.Caps.from_string(caps)
        self.camerafilter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        self.camerafilter1.set_property("caps", camera1caps)

        # creation of the videoconvert elements
        self.videoformatconverter1 = Gst.ElementFactory.make("videoconvert", "video_convert1")
        self.videoformatconverter2 = Gst.ElementFactory.make("videoconvert", "video_convert2")

        self.tee = Gst.ElementFactory.make("tee", "tee")

        # creation and configuration of the queue elements
        self.queue1 = Gst.ElementFactory.make("queue", "queue-1")
        self.queue2 = Gst.ElementFactory.make("queue", "queue-2")
        self.queue1.set_property("max-size-buffers", 1)
        self.queue1.set_property("leaky", 2)
        self.queue2.set_property("max-size-buffers", 1)
        self.queue2.set_property("leaky", 2)

        # creation and configuration of the appsink element
        self.appsink = Gst.ElementFactory.make("appsink", "appsink")
        nn_caps = "video/x-raw, format = RGB, width=" + str(self.app.nn_input_width) + ",height=" + str(self.app.nn_input_height)
        nncaps = Gst.Caps.from_string(nn_caps)
        self.appsink.set_property("caps", nncaps)
        self.appsink.set_property("emit-signals", True)
        self.appsink.set_property("sync", False)
        self.appsink.set_property("max-buffers", 1)
        self.appsink.set_property("drop", True)
        self.appsink.connect("new-sample", self.new_sample)

        # creation of the gtkwaylandsink element to handle the gestreamer video stream
        self.gtkwaylandsink = Gst.ElementFactory.make("gtkwaylandsink")
        self.pack_start(self.gtkwaylandsink.props.widget, True, True, 0)
        self.gtkwaylandsink.props.widget.show()

        # creation and configuration of the fpsdisplaysink element to measure display fps
        self.fps_disp_sink = Gst.ElementFactory.make("fpsdisplaysink", "fpsmeasure1")
        self.fps_disp_sink.set_property("signal-fps-measurements", True)
        self.fps_disp_sink.set_property("fps-update-interval", 2000)
        self.fps_disp_sink.set_property("text-overlay", False)
        self.fps_disp_sink.set_property("video-sink", self.gtkwaylandsink)
        self.fps_disp_sink.connect("fps-measurements",self.get_fps_display)

        # creation of the video rate and video scale elements
        self.video_rate = Gst.ElementFactory.make("videorate", "video-rate")
        self.video_scale = Gst.ElementFactory.make("videoscale", "video-scale")

        # Add all elements to the pipeline
        self.pipeline_preview.add(self.v4lsrc1)
        self.pipeline_preview.add(self.camerafilter1)
        self.pipeline_preview.add(self.videoformatconverter1)
        self.pipeline_preview.add(self.videoformatconverter2)
        self.pipeline_preview.add(self.tee)
        self.pipeline_preview.add(self.queue1)
        self.pipeline_preview.add(self.queue2)
        self.pipeline_preview.add(self.appsink)
        self.pipeline_preview.add(self.fps_disp_sink)
        self.pipeline_preview.add(self.video_rate)
        self.pipeline_preview.add(self.video_scale)

        # linking elements together
        #                              -> queue 1 -> videoconvert -> fpsdisplaysink
        # v4l2src -> video rate -> tee
        #                              -> queue 2 -> videoconvert -> video scale -> appsink
        self.v4lsrc1.link(self.video_rate)
        self.video_rate.link(self.camerafilter1)
        self.camerafilter1.link(self.tee)
        self.queue1.link(self.videoformatconverter1)
        self.videoformatconverter1.link(self.fps_disp_sink)
        self.queue2.link(self.videoformatconverter2)
        self.videoformatconverter2.link(self.video_scale)
        self.video_scale.link(self.appsink)
        self.tee.link(self.queue1)
        self.tee.link(self.queue2)

        # set pipeline playing mode
        self.pipeline_preview.set_state(Gst.State.PLAYING)
        # getting pipeline bus
        self.bus_preview = self.pipeline_preview.get_bus()
        self.bus_preview.add_signal_watch()
        self.bus_preview.connect('message::error', self.msg_error_cb)
        self.bus_preview.connect('message::eos', self.msg_eos_cb)
        self.bus_preview.connect('message::info', self.msg_info_cb)
        self.bus_preview.connect('message::application', self.msg_application_cb)
        self.bus_preview.connect('message::state-changed', self.msg_state_changed_cb)
        return True

    def camera_pipeline_preview_creation(self):
        """
        Creation of the gstreamer pipeline when gstwidget is created dedicated to camera stream
        (in dual camera pipeline mode)
        """
        # gstreamer pipeline creation
        self.pipeline_preview = Gst.Pipeline()

        # creation of the source v4l2src for preview
        self.v4lsrc_preview = Gst.ElementFactory.make("v4l2src", "source_prev")
        video_device_preview = "/dev/" + str(self.app.video_device_prev)
        self.v4lsrc_preview.set_property("device", video_device_preview)
        print("device used for preview : ",video_device_preview)

        #creation of the v4l2src caps for preview
        caps_prev = str(self.app.camera_caps_prev)
        print("Camera pipeline preview configuration : ",caps_prev)
        camera1caps_prev = Gst.Caps.from_string(caps_prev)
        self.camerafilter_prev = Gst.ElementFactory.make("capsfilter", "filter_preview")
        self.camerafilter_prev.set_property("caps", camera1caps_prev)

        # creation and configuration of the queue elements
        self.queue_prev = Gst.ElementFactory.make("queue", "queue-prev")
        self.queue_prev.set_property("max-size-buffers", 1)
        self.queue_prev.set_property("leaky", 2)

        # creation of the gtkwaylandsink element to handle the gstreamer video stream
        properties_names=["drm-device"]
        properties_values=[" "]
        self.gtkwaylandsink = Gst.ElementFactory.make_with_properties("gtkwaylandsink",properties_names,properties_values)
        self.pack_start(self.gtkwaylandsink.props.widget, True, True, 0)
        self.gtkwaylandsink.props.widget.show()

        # creation and configuration of the fpsdisplaysink element to measure display fps
        self.fps_disp_sink = Gst.ElementFactory.make("fpsdisplaysink", "fpsmeasure1")
        self.fps_disp_sink.set_property("signal-fps-measurements", True)
        self.fps_disp_sink.set_property("fps-update-interval", 2000)
        self.fps_disp_sink.set_property("text-overlay", False)
        self.fps_disp_sink.set_property("video-sink", self.gtkwaylandsink)
        self.fps_disp_sink.connect("fps-measurements",self.get_fps_display)

        # Add all elements to the pipeline
        self.pipeline_preview.add(self.v4lsrc_preview)
        self.pipeline_preview.add(self.camerafilter_prev)
        self.pipeline_preview.add(self.queue_prev)
        self.pipeline_preview.add(self.fps_disp_sink)

        # linking elements together
        self.v4lsrc_preview.link(self.camerafilter_prev)
        self.camerafilter_prev.link(self.queue_prev)
        self.queue_prev.link(self.fps_disp_sink)

        # self.setup_nn_pipeline()
        # set pipeline playing mode
        # self.pipeline_preview.set_state(Gst.State.PLAYING)
        # set pipeline playing mode
        # self.pipeline_nn.set_state(Gst.State.PLAYING)
        self.bus_preview = self.pipeline_preview.get_bus()
        self.bus_preview.add_signal_watch()
        self.bus_preview.connect('message::error', self.msg_error_cb)
        self.bus_preview.connect('message::eos', self.msg_eos_cb)
        self.bus_preview.connect('message::info', self.msg_info_cb)
        self.bus_preview.connect('message::state-changed', self.msg_state_changed_cb)
        return True

    def nn_pipeline_creation(self):
        """
        Creation of the gstreamer pipeline when gstwidget is created dedicated to NN model inference
        (in dual camera pipeline mode)
        """
        self.pipeline_nn = Gst.Pipeline()

        # creation of the source v4l2src for nn
        self.v4lsrc_nn = Gst.ElementFactory.make("v4l2src", "source_nn")
        video_device_nn = "/dev/" + str(self.app.video_device_nn)
        self.v4lsrc_nn.set_property("device", video_device_nn)
        print("device used as input of the NN : ",video_device_nn)

        caps_nn_rq = str(self.app.camera_caps_nn)
        print("Camera pipeline nn requested configuration : ",caps_nn_rq)
        camera1caps_nn_rq = Gst.Caps.from_string(caps_nn_rq)
        self.camerafilter_nn_rq = Gst.ElementFactory.make("capsfilter", "filter_nn_requested")
        self.camerafilter_nn_rq.set_property("caps", camera1caps_nn_rq)

        # creation and configuration of the queue elements
        self.queue_nn = Gst.ElementFactory.make("queue", "queue-nn")
        self.queue_nn.set_property("max-size-buffers", 1)
        self.queue_nn.set_property("leaky", 2)

        # creation and configuration of the appsink element
        self.appsink = Gst.ElementFactory.make("appsink", "appsink")
        self.appsink.set_property("caps", camera1caps_nn_rq)
        self.appsink.set_property("emit-signals", True)
        self.appsink.set_property("sync", False)
        self.appsink.set_property("max-buffers", 1)
        self.appsink.set_property("drop", True)
        self.appsink.connect("new-sample", self.new_sample)

        # Add all elements to the pipeline
        self.pipeline_nn.add(self.v4lsrc_nn)
        self.pipeline_nn.add(self.camerafilter_nn_rq)
        self.pipeline_nn.add(self.queue_nn)
        self.pipeline_nn.add(self.appsink)

        # linking elements together
        self.v4lsrc_nn.link(self.camerafilter_nn_rq)
        self.camerafilter_nn_rq.link(self.queue_nn)
        self.queue_nn.link(self.appsink)

        # getting pipeline bus
        self.bus_nn = self.pipeline_nn.get_bus()
        self.bus_nn.add_signal_watch()
        self.bus_nn.connect('message::error', self.msg_error_cb)
        self.bus_nn.connect('message::eos', self.msg_eos_cb)
        self.bus_nn.connect('message::info', self.msg_info_cb)
        self.bus_nn.connect('message::application', self.msg_application_cb)
        self.bus_nn.connect('message::state-changed', self.msg_state_changed_cb)
        return True

    def msg_eos_cb(self, bus, message):
        """
        Catch gstreamer end of stream signal
        """
        print('eos message -> {}'.format(message))

    def msg_info_cb(self, bus, message):
        """
        Catch gstreamer info signal
        """
        print('info message -> {}'.format(message))

    def msg_error_cb(self, bus, message):
        """
        Catch gstreamer error signal
        """
        print('error message -> {}'.format(message.parse_error()))

    def msg_state_changed_cb(self, bus, message):
        """
        Catch gstreamer state changed signal
        """
        oldstate,newstate,pending = message.parse_state_changed()
        if (oldstate == Gst.State.NULL) and (newstate == Gst.State.READY):
            Gst.debug_bin_to_dot_file(self.pipeline_preview, Gst.DebugGraphDetails.ALL,"pipeline_py_NULL_READY")

    def msg_application_cb(self, bus, message):
        """
        Catch gstreamer application signal
        """
        if message.get_structure().get_name() == 'inference-done':
            self.app.draw_inference = True
            self.app.update_ui()

    def update_isp_config(self):
        """
        Update internal ISP configuration to make the most of the camera sensor
        """
        isp_file =  "/usr/local/demo/bin/dcmipp-isp-ctrl"
        if(args.dual_camera_pipeline):
            isp_config_gamma_0 = "v4l2-ctl -d " + self.app.aux_postproc + " -c gamma_correction=0"
            isp_config_gamma_1 = "v4l2-ctl -d " + self.app.aux_postproc + " -c gamma_correction=1"
        else :
            isp_config_gamma_0 = "v4l2-ctl -d " + self.app.main_postproc + " -c gamma_correction=0"
            isp_config_gamma_1 = "v4l2-ctl -d " + self.app.main_postproc + " -c gamma_correction=1"

        isp_config_whiteb = isp_file +  " -i0 "
        isp_config_autoexposure = isp_file + " -g > /dev/null"

        if os.path.exists(isp_file) and self.app.dcmipp_sensor=="imx335" and self.isp_first_config :
            subprocess.run(isp_config_gamma_0,shell=True)
            subprocess.run(isp_config_gamma_1,shell=True)
            subprocess.run(isp_config_whiteb,shell=True)
            subprocess.run(isp_config_autoexposure,shell=True)
            self.isp_first_config = False

        if self.cpt_frame == 0 and os.path.exists(isp_file) and self.app.dcmipp_sensor=="imx335" :
            subprocess.run(isp_config_whiteb,shell=True)
            subprocess.run(isp_config_autoexposure,shell=True)

        return True

    def gst_to_opencv(self,sample):
        """
        conversion of the gstreamer frame buffer into numpy array
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        if(args.debug):
            buf_size = buf.get_size()
            buff = buf.extract_dup(0, buf.get_size())
            f=open("/home/weston/NN_sample_dump.raw", "wb")
            f.write(buff)
            f.close()
        number_of_column = caps.get_structure(0).get_value('width')
        number_of_lines = caps.get_structure(0).get_value('height')
        channels = 3
        strides = (772,3,1)
        arr = np.ndarray(
            (number_of_lines,
             number_of_column,
             channels),
            strides=strides,
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8)
        return arr

    def new_sample(self,*data):
        """
        recover video frame from appsink
        and run inference
        """
        sample = self.appsink.emit("pull-sample")
        arr = self.gst_to_opencv(sample)
        if(args.debug):
            cv2.imwrite("/home/weston/NN_cv_sample_dump.png",arr)
        self.last_picture = arr.copy()
        self.cpt_frame += 1
        if self.cpt_frame == 60:
            self.cpt_frame = 0
            self.update_isp_config()
        return Gst.FlowReturn.OK

    def get_fps_display(self,fpsdisplaysink,fps,droprate,avgfps):
        """
        measure and recover display fps
        """
        self.instant_fps = fps
        return self.instant_fps

class MainWindow(Gtk.Window):
    """
    This class handles all the functions necessary
    to display video stream in GTK GUI or still
    pictures using OpenCVS
    """

    def __init__(self,args,app):
        """
        Setup instances of class and shared variables
        usefull for the application
        """
        Gtk.Window.__init__(self)
        self.app = app
        self.main_ui_creation(args)

    def set_ui_param(self):
        """
        Setup all the UI parameter depending
        on the screen size
        """
        if self.app.window_height > self.app.window_width :
            window_constraint = self.app.window_width
        else :
            window_constraint = self.app.window_height

        self.ui_cairo_font_size = 23
        self.ui_cairo_font_size_label = 37
        self.ui_icon_exit_size = '50'
        self.ui_icon_st_size = '160'
        self.ui_icon_label_size = '64'
        if window_constraint <= 272:
               # Display 480x272
               self.ui_cairo_font_size = 11
               self.ui_cairo_font_size_label = 18
               self.ui_icon_exit_size = '25'
               self.ui_icon_st_size = '52'
               self.ui_icon_label_size = '32'
        elif window_constraint <= 480:
               #Display 800x480
               self.ui_cairo_font_size = 16
               self.ui_cairo_font_size_label = 29
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '80'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 600:
               #Display 1024x600
               self.ui_cairo_font_size = 16
               self.ui_cairo_font_size_label = 32
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '120'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 720:
               #Display 1280x720
               self.ui_cairo_font_size = 23
               self.ui_cairo_font_size_label = 38
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '160'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 1080:
               #Display 1920x1080
               self.ui_cairo_font_size = 33
               self.ui_cairo_font_size_label = 48
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '160'
               self.ui_icon_label_size = '64'

    def main_ui_creation(self,args):
        """
        Setup the Gtk UI of the main window
        """
        # remove the title bar
        self.set_decorated(False)

        self.first_drawing_call = True
        GdkDisplay = Gdk.Display.get_default()
        monitor = Gdk.Display.get_monitor(GdkDisplay, 0)
        workarea = Gdk.Monitor.get_workarea(monitor)

        GdkScreen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        css_path = RESOURCES_DIRECTORY + "Default.css"
        self.set_name("main_window")
        provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(GdkScreen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.maximize()
        self.screen_width = workarea.width
        self.screen_height = workarea.height

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', Gtk.main_quit)
        self.set_ui_param()
        # setup info_box containing inference results
        # camera preview mode
        self.info_box = Gtk.VBox()
        self.info_box.set_name("gui_main_stbox")
        self.st_icon_path = RESOURCES_DIRECTORY + 'SEMSEG_st_icon_' + self.ui_icon_st_size + 'px' + '.png'
        self.st_icon = Gtk.Image.new_from_file(self.st_icon_path)
        self.st_icon_event = Gtk.EventBox()
        self.st_icon_event.add(self.st_icon)
        self.info_box.pack_start(self.st_icon_event,False,False,2)
        self.inf_time = Gtk.Label()
        self.inf_time.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.inf_time, False, False,10)
        info_sstr = "    disp.fps :      " + "\n" + "  inf.fps :     " + "\n" + "  inf.time :    " + "\n"
        self.inf_time.set_markup("<span font=\'%d\' color='#FFFFFFFF'><b>%s\n</b></span>" % (self.ui_cairo_font_size,info_sstr))
        self.labels_to_display = Gtk.Label()
        self.labels_to_display.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.labels_to_display,False,False,2)
        self.rules = Gtk.Label()
        self.rules.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.rules,False,False,10)
        rules_sstr = " Click on " + "\n" + " camera preview " + "\n" + " to run " + "\n" + " segmentation " + "\n"
        self.rules.set_markup("<span font=\'%d\' color='#000000'><b>%s\n</b></span>" % (self.ui_cairo_font_size,rules_sstr))
        self.label_icon_path = RESOURCES_DIRECTORY + 'label_icon_' + self.ui_icon_label_size + 'x' + self.ui_icon_label_size + '.png'
        self.label_icon = Gtk.Image.new_from_file(self.label_icon_path)
        self.label_icon_event = Gtk.EventBox()
        self.label_icon_event.add(self.label_icon)
        self.info_box.pack_start(self.label_icon_event,False,False,10)

        # setup video box containing gst stream in camera previex mode
        # and a openCV picture in still picture mode
        # An overlay is used to keep a gtk drawing area on top of the video stream
        self.video_box = Gtk.HBox()
        self.video_box.set_name("gui_main_video")

        # camera preview => gst stream
        self.video_widget = self.app.gst_widget
        self.video_widget.set_app_paintable(True)
        self.video_box.pack_start(self.video_widget, True, True, 0)

        # # setup the exit box which contains the exit button
        self.exit_box = Gtk.VBox()
        self.exit_box.set_name("gui_main_exit")
        self.exit_icon_path = RESOURCES_DIRECTORY + 'exit_' + self.ui_icon_exit_size + 'x' + self.ui_icon_exit_size + '.png'
        self.exit_icon = Gtk.Image.new_from_file(self.exit_icon_path)
        self.exit_icon_event = Gtk.EventBox()
        self.exit_icon_event.add(self.exit_icon)
        self.exit_box.pack_start(self.exit_icon_event,False,False,2)

        # setup main box which group the three previous boxes
        self.main_box =  Gtk.HBox()
        self.exit_box.set_name("gui_main")
        self.main_box.pack_start(self.info_box,False,False,0)
        self.main_box.pack_start(self.video_box,True,True,0)
        self.main_box.pack_start(self.exit_box,False,False,0)
        self.add(self.main_box)
        return True

class OverlayWindow(Gtk.Window):
    """
    This class handles all the functions necessary
    to display overlayed information on top of the
    video stream and in side information boxes of
    the GUI
    """
    def __init__(self,args,app):
        """
        Setup instances of class and shared variables
        usefull for the application
        """
        Gtk.Window.__init__(self)
        self.app = app
        self.overlay_ui_creation(args)
        self.previous_touch_event = 0
        self.display_help = False

    def exit_icon_cb(self,eventbox, event):
        """
        Exit callback to close application
        """
        self.destroy()
        Gtk.main_quit()

    def label_icon_event_cb(self,eventbox, event):
        """
        Exit callback to close application
        """
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if (self.display_help):
                self.display_help = False
                self.app.update_ui()
            else :
                self.display_help = True
                self.app.update_ui()


    def touch_event_cb(self, widget, event):
        """
        Touch event callback to stop camera stream and run inference on last camera frame
        """
        if event.touch.type == Gdk.EventType.TOUCH_BEGIN:
            state = self.app.gst_widget.pipeline_preview.get_state(Gst.CLOCK_TIME_NONE)
            if (state.state == Gst.State.PLAYING):
                self.app.gst_widget.pipeline_preview.set_state(Gst.State.PAUSED)
                self.app.draw_inference=True
                if (self.app.gst_widget.last_picture is not None):
                    start_time = timer()
                    self.app.nn.launch_inference(self.app.gst_widget.last_picture)
                    stop_time = timer()
                    self.app.nn_inference_time = stop_time - start_time
                    self.app.nn_inference_fps = (1000/(self.app.nn_inference_time*1000))
                    self.app.unique_label, self.app.nn_seg_map = self.app.nn.get_results()
                self.app.update_ui()
            elif (state.state == Gst.State.PAUSED):
                self.app.gst_widget.pipeline_preview.set_state(Gst.State.PLAYING)
                self.app.draw_inference = False
                self.app.update_ui()

    def set_ui_param(self):
        """
        Setup all the UI parameter depending
        on the screen size
        """
        if self.app.window_height > self.app.window_width :
            window_constraint = self.app.window_width
        else :
            window_constraint = self.app.window_height

        self.ui_cairo_font_size = 23
        self.ui_cairo_font_size_label = 37
        self.ui_icon_exit_size = '50'
        self.ui_icon_st_size = '160'
        self.ui_icon_label_size = '64'
        if window_constraint <= 272:
               # Display 480x272
               self.ui_cairo_font_size = 11
               self.ui_cairo_font_size_label = 18
               self.ui_icon_exit_size = '25'
               self.ui_icon_st_size = '52'
               self.ui_icon_label_size = '32'
        elif window_constraint <= 480:
               #Display 800x480
               self.ui_cairo_font_size = 16
               self.ui_cairo_font_size_label = 29
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '80'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 600:
               #Display 1024x600
               self.ui_cairo_font_size = 19
               self.ui_cairo_font_size_label = 32
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '120'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 720:
               #Display 1280x720
               self.ui_cairo_font_size = 23
               self.ui_cairo_font_size_label = 38
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '160'
               self.ui_icon_label_size = '64'
        elif window_constraint <= 1080:
               #Display 1920x1080
               self.ui_cairo_font_size = 33
               self.ui_cairo_font_size_label = 48
               self.ui_icon_exit_size = '50'
               self.ui_icon_st_size = '160'
               self.ui_icon_label_size = '64'

    def overlay_ui_creation(self,args):
        """
        Setup the Gtk UI of the overlay window
        """
        # remove the title bar
        self.set_decorated(False)

        self.first_drawing_call = True
        GdkDisplay = Gdk.Display.get_default()
        monitor = Gdk.Display.get_monitor(GdkDisplay, 0)
        workarea = Gdk.Monitor.get_workarea(monitor)

        GdkScreen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        css_path = RESOURCES_DIRECTORY + "Default.css"
        self.set_name("overlay_window")
        provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(GdkScreen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.maximize()
        self.screen_width = workarea.width
        self.screen_height = workarea.height

        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', Gtk.main_quit)
        self.set_ui_param()

        # setup info_box containing inference results
        # camera preview mode
        self.info_box = Gtk.VBox()
        self.info_box.set_name("gui_overlay_stbox")
        self.st_icon_path = RESOURCES_DIRECTORY + 'SEMSEG_st_icon_' + self.ui_icon_st_size + 'px' + '.png'
        self.st_icon = Gtk.Image.new_from_file(self.st_icon_path)
        self.st_icon_event = Gtk.EventBox()
        self.st_icon_event.add(self.st_icon)
        self.info_box.pack_start(self.st_icon_event,False,False,2)
        self.inf_time = Gtk.Label()
        self.inf_time.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.inf_time,False,False,10)
        info_sstr = "    disp.fps :      " + "\n" + "  inf.fps :     " + "\n" + "  inf.time :    " + "\n"
        self.inf_time.set_markup("<span font=\'%d\' color='#FFFFFFFF'><b>%s\n</b></span>" % (self.ui_cairo_font_size,info_sstr))
        self.labels_to_display = Gtk.Label()
        self.labels_to_display.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.labels_to_display,False,False,2)
        self.rules = Gtk.Label()
        self.rules.set_justify(Gtk.Justification.CENTER)
        self.info_box.pack_start(self.rules,False,False,10)
        rules_sstr = " Click on " + "\n" + " camera preview " + "\n" + " to run " + "\n" + " segmentation " + "\n"
        self.rules.set_markup("<span font=\'%d\' color='#E6007E'><b>%s\n</b></span>" % (self.ui_cairo_font_size,rules_sstr))
        self.label_icon_path = RESOURCES_DIRECTORY + 'label_icon_' + self.ui_icon_label_size + 'x' + self.ui_icon_label_size + '.png'
        self.label_icon = Gtk.Image.new_from_file(self.label_icon_path)
        self.label_icon_event = Gtk.EventBox()
        self.label_icon_event.add(self.label_icon)
        self.label_icon_event.connect("button_press_event",self.label_icon_event_cb)
        self.info_box.pack_start(self.label_icon_event,False,False,10)

        # setup video box containing a transparent drawing area
        # to draw over the video stream
        self.video_box = Gtk.HBox()
        self.video_box.set_name("gui_overlay_video")
        self.video_box.set_app_paintable(True)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.drawing)
        self.drawing_area.connect("touch-event", self.touch_event_cb)
        self.drawing_area.add_events(Gdk.EventMask.TOUCH_MASK)
        self.drawing_area.set_name("overlay_draw")
        self.drawing_area.set_app_paintable(True)
        self.video_box.pack_start(self.drawing_area, True, True, 0)

        # # setup the exit box which contains the exit button
        self.exit_box = Gtk.VBox()
        self.exit_box.set_name("gui_overlay_exit")
        self.exit_icon_path = RESOURCES_DIRECTORY + 'exit_' + self.ui_icon_exit_size + 'x' + self.ui_icon_exit_size+ '.png'
        self.exit_icon = Gtk.Image.new_from_file(self.exit_icon_path)
        self.exit_icon_event = Gtk.EventBox()
        self.exit_icon_event.add(self.exit_icon)
        self.exit_icon_event.connect("button_press_event",self.exit_icon_cb)
        self.exit_box.pack_start(self.exit_icon_event,False,False,2)

        # setup main box which group the three previous boxes
        self.main_box =  Gtk.HBox()
        self.exit_box.set_name("gui_overlay")
        self.main_box.pack_start(self.info_box,False,False,0)
        self.main_box.pack_start(self.video_box,True,True,0)
        self.main_box.pack_start(self.exit_box,False,False,0)
        self.add(self.main_box)
        return True

    def drawing(self, widget, cr):
        """
        Drawing callback used to draw with cairo on
        the drawing area
        """
        if self.first_drawing_call :
            self.first_drawing_call = False
            self.drawing_width = widget.get_allocated_width()
            self.drawing_height = widget.get_allocated_height()
            cr.set_font_size(self.ui_cairo_font_size)
            self.draw = True
            return False

        if (self.app.draw_inference):
            self.display_help = False
            #recover the widget size depending of the information to display
            self.drawing_width = widget.get_allocated_width()
            self.drawing_height = widget.get_allocated_height()

            #adapt the drawing overlay depending on the camera stream displayed
            preview_ratio = float(args.frame_width)/float(args.frame_height)
            preview_height = self.drawing_height
            preview_width =  preview_ratio * preview_height
            if preview_width >= self.drawing_width:
                offset = 0
                preview_width = self.drawing_width
                preview_height = preview_width / preview_ratio
                vertical_offset = (self.drawing_height - preview_height)/2
            else :
                offset = (self.drawing_width - preview_width)/2
                vertical_offset = 0

            #load the segmentation bitmap as a picture
            img = Image.fromarray(self.app.nn_seg_map,'RGBA')
            img.save("/home/weston/bitmap_before_resize.png","PNG")
            size = (int(preview_width),int(preview_height))
            img = img.resize(size)
            img_alpha = img.copy()
            img_alpha.save("/home/weston/bitmap.png","PNG")

            #load the bitmap to display it as overlay
            pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/weston/bitmap.png')
            img = Gdk.cairo_set_source_pixbuf(cr, pixbuf.copy(),int(offset), int(vertical_offset))
            cr.paint()
        else:
            if (self.display_help):
                cr.rectangle(0, 0, self.drawing_width, self.drawing_height)
                cr.set_source_rgba(3,35,75,0.25)
                cr.fill()
                #determine labels to display
                labels = self.app.nn.get_labels()
                label_map = np.arange(len(labels)).reshape(len(labels), 1)
                color_map = self.app.nn.colors_map[label_map]
                offset_x = self.drawing_width/6
                offset_y = self.drawing_height/8
                #display labels
                for i in range(len(labels)):
                    if (i < 10):
                        label = labels[i]
                        text = str(label)
                        cr.set_font_size(self.ui_cairo_font_size*1.5)
                        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
                        cr.move_to(offset_x,offset_y+((self.ui_cairo_font_size*1.5)*i))
                        cr.text_path(text)
                        cr.set_source_rgba(color_map[i][0][0]/255, color_map[i][0][1]/255, color_map[i][0][2]/255,1)
                        cr.fill_preserve()
                        cr.set_source_rgb(1, 1, 1)
                        cr.set_line_width(0.1)
                        cr.stroke()
                    else :
                        label = labels[i]
                        text = str(label)
                        cr.set_font_size(self.ui_cairo_font_size*1.5)
                        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(text)
                        cr.move_to(3*offset_x,offset_y+((self.ui_cairo_font_size*1.5)*(i-10)))
                        cr.text_path(text)
                        cr.set_source_rgba(color_map[i][0][0]/255, color_map[i][0][1]/255, color_map[i][0][2]/255,1)
                        cr.fill_preserve()
                        cr.set_source_rgb(1, 1, 1)
                        cr.set_line_width(0.1)
                        cr.stroke()
            else :
                self.app.main_window.label_icon.show()
                self.label_icon.show()
                self.app.main_window.inf_time.hide()
                self.inf_time.hide()
                self.app.main_window.rules.show()
                self.rules.show()
                self.labels_to_display.hide()
        return True

class Application:
    """
    Class that handles the whole application
    """
    def __init__(self, args):
        #init variables uses :
        self.exit_app = False
        self.first_call = True
        self.loading_nn = True
        self.draw_inference = False
        self.window_width = 0
        self.window_height = 0
        self.get_display_resolution()

        #instantiate the Neural Network class
        self.nn = NeuralNetwork(args.model_file, args.label_file, float(args.input_mean), float(args.input_std))
        self.shape = self.nn.get_img_size()
        self.nn_input_width = self.shape[1]
        self.nn_input_height = self.shape[0]
        self.nn_input_channel = self.shape[2]
        self.nn_inference_time = 0.0
        self.nn_inference_fps = 0.0
        self.unique_label = []
        self.nn_seg_map = np.zeros((self.nn_input_width,self.nn_input_height,3))

        #Test if a camera is connected
        check_camera_cmd = RESOURCES_DIRECTORY + "check_camera_preview.sh"
        check_camera = subprocess.run(check_camera_cmd)
        if check_camera.returncode==1:
            print("no camera connected")
            exit(1)
        if(args.dual_camera_pipeline):
            self.video_device_prev,self.camera_caps_prev,self.video_device_nn,self.camera_caps_nn,self.dcmipp_sensor, self.aux_postproc = self.setup_camera()
        else:
            self.video_device_prev,self.camera_caps_prev,self.dcmipp_sensor, self.main_postproc = self.setup_camera()

        # initialize the list of the file to be processed (used with the
        # --image parameter)
        self.files = []

        #instantiate the Gstreamer pipeline
        self.gst_widget = GstWidget(self,self.nn)
        #instantiate the main window
        self.main_window = MainWindow(args,self)
        #instantiate the overlay window
        self.overlay_window = OverlayWindow(args,self)
        self.main()

    def get_display_resolution(self):
        """
        Used to ask the system for the display resolution
        """
        cmd = "modetest -M stm -c > /tmp/display_resolution.txt"
        subprocess.run(cmd,shell=True)
        display_info_pattern = "#0"
        display_information = ""
        display_resolution = ""
        display_width = ""
        display_height = ""

        f = open("/tmp/display_resolution.txt", "r")
        for line in f :
            if display_info_pattern in line:
                display_information = line
        display_information_splited = display_information.split()
        for i in display_information_splited :
            if "x" in i :
                display_resolution = i
        display_resolution = display_resolution.replace('x',' ')
        display_resolution = display_resolution.split()
        display_width = display_resolution[0]
        display_height = display_resolution[1]

        print("display resolution is : ",display_width, " x ", display_height)
        self.window_width = int(display_width)
        self.window_height = int(display_height)
        return 0

    def setup_camera(self):
        """
        Used to configure the camera based on resolution passed as application arguments
        """
        width = str(args.frame_width)
        height = str(args.frame_height)
        framerate = str(args.framerate)
        device = str(args.video_device)
        nn_input_width = str(self.nn_input_width)
        nn_input_height = str(self.nn_input_height)
        if (args.dual_camera_pipeline):
            config_camera = RESOURCES_DIRECTORY + "setup_camera.sh " + width + " " + height + " " + framerate + " " + nn_input_width + " " + nn_input_height + " " + device
        else:
            config_camera = RESOURCES_DIRECTORY + "setup_camera.sh " + width + " " + height + " " + framerate + " " + device
        x = subprocess.check_output(config_camera,shell=True)
        x = x.decode("utf-8")
        print(x)
        x = x.split("\n")
        for i in x :
            if "V4L_DEVICE_PREV" in i:
                video_device_prev = i.lstrip('V4L_DEVICE_PREV=')
            if "V4L2_CAPS_PREV" in i:
                camera_caps_prev = i.lstrip('V4L2_CAPS_PREV=')
            if "V4L_DEVICE_NN" in i:
                video_device_nn = i.lstrip('V4L_DEVICE_NN=')
            if "V4L2_CAPS_NN" in i:
                camera_caps_nn = i.lstrip('V4L2_CAPS_NN=')
            if "DCMIPP_SENSOR" in i:
                dcmipp_sensor = i.lstrip('DCMIPP_SENSOR=')
            if "MAIN_POSTPROC" in i:
                main_postproc = i.lstrip('MAIN_POSTPROC=')
            if "AUX_POSTPROC" in i:
                aux_postproc = i.lstrip('AUX_POSTPROC=')
        if (args.dual_camera_pipeline):
            return video_device_prev, camera_caps_prev,video_device_nn,camera_caps_nn, dcmipp_sensor, aux_postproc
        else:
            return video_device_prev, camera_caps_prev, dcmipp_sensor, main_postproc

    # Updating the labels and the inference infos displayed on the GUI interface - camera input
    def update_label_preview(self):
        """
        Updating the labels and the inference infos displayed on the GUI interface - camera input
        """
        inference_time = self.nn_inference_time * 1000
        inference_fps = self.nn_inference_fps
        display_fps = self.gst_widget.instant_fps

        str_inference_time = str("{0:0.1f}".format(inference_time)) + " ms"
        str_display_fps = str("{0:.1f}".format(display_fps)) + " fps"
        str_inference_fps = str("{0:.1f}".format(inference_fps)) + " fps"

        #determine labels to display
        labels = self.nn.get_labels()
        label_map = np.arange(len(labels)).reshape(len(labels), 1)
        color_map = self.nn.colors_map[label_map]
        label_sstr = ""
        if (self.draw_inference):
            #display labels
            for i in range(len(self.unique_label)):
                if (i != 0):
                    label = labels[self.unique_label[i]]
                    text = str(label)
                    R = hex(color_map[self.unique_label[i]][0][0])
                    G = hex(color_map[self.unique_label[i]][0][1])
                    B = hex(color_map[self.unique_label[i]][0][2])
                    R = R.removeprefix('0x')
                    G = G.removeprefix('0x')
                    B = B.removeprefix('0x')
                    R = R.upper()
                    G = G.upper()
                    B = B.upper()
                    if (len(R)==1):
                        R = "0" + R
                    if (len(G)==1):
                        G = "0" + G
                    if (len(B)==1):
                        B = "0" + B
                    label_sstr += "<span font=\'" + str(self.overlay_window.ui_cairo_font_size) + "\' color='#" + str(R) + str(G) + str(B) + "'><b>" +  text + "\n</b></span>"
            label_sstr = "<span font=\'" + str(self.overlay_window.ui_cairo_font_size) + "\' color='#FFFFFF'><b>Labels : \n</b></span>" + label_sstr
            info_sstr = "  inf.fps :     " + "\n" + str_inference_fps + "\n" + "      inf.time :        " + "\n"  + str_inference_time + "\n"
            self.overlay_window.inf_time.set_markup("<span font=\'%d\' color='#FFFFFF'><b>%s\n</b></span>" % (self.overlay_window.ui_cairo_font_size,info_sstr))
            self.overlay_window.labels_to_display.set_markup(label_sstr)
            self.overlay_window.rules.hide()
            self.main_window.label_icon.hide()
            self.overlay_window.label_icon.hide()
            self.main_window.inf_time.show()
            self.overlay_window.inf_time.show()
            self.overlay_window.labels_to_display.show()

    def update_ui(self):
        """
        refresh overlay UI
        """
        self.update_label_preview()
        self.main_window.queue_draw()
        self.overlay_window.queue_draw()


    def main(self):
        """
        main function
        """
        self.main_window.connect("delete-event", Gtk.main_quit)
        self.main_window.show_all()
        self.overlay_window.connect("delete-event", Gtk.main_quit)
        self.overlay_window.show_all()
        return True

if __name__ == '__main__':
    # add signal to catch CRTL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    #Tensorflow Lite NN intitalisation
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video_device", default="", help="video device ex: video0")
    parser.add_argument("--frame_width", default=640, help="width of the camera frame (default is 640)")
    parser.add_argument("--frame_height", default=480, help="height of the camera frame (default is 480)")
    parser.add_argument("--framerate", default=15, help="framerate of the camera (default is 15fps)")
    parser.add_argument("-m", "--model_file", default="", help=".tflite/nbg/onnx model to be executed")
    parser.add_argument("-l", "--label_file", default="", help="name of file containing labels")
    parser.add_argument("--input_mean", default=127.5, help="input mean")
    parser.add_argument("--input_std", default=127.5, help="input standard deviation")
    parser.add_argument("--dual_camera_pipeline", default=False, action='store_true', help=argparse.SUPPRESS)
    parser.add_argument("--debug", default=False, action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        application = Application(args)

    except Exception as exc:
        print("Main Exception: ", exc )

    Gtk.main()
    #remove bitmap.png file before closing app
    file = 'bitmap.png'
    location = "/home/weston"
    path = os.path.join(location,file)
    os.remove(path)
    print("gtk main finished")
    print("application exited properly")
    os._exit(0)
