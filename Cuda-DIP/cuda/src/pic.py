#!/usr/bin/env python
# -*-coding=utf-8-*-
from __future__ import print_function
import KDIP_cuda.cuda_filter as ft
import KDIP_cuda.mono        as mo
import KDIP_cuda.fft        as myfft
import KDIP_cuda.utils        as util
import KDIP_cuda.Hoff        as HF
import matplotlib.pyplot as plt
import cv2
import time
import numpy as np
# import rospy
#
# from std_msgs.msg import String
#
# import rospy
# from std_msgs.msg import String

mode = "LPF"
last_mode = "All"


def callback(data):
    global mode
    mode = data.data
    print("111", mode)


if __name__ == '__main__':
    # original = cv2.imread("./Img/e.jpg", cv2.IMREAD_GRAYSCALE)
    # # original = cv2.resize(original,(128,64))
    # # cv2.imshow("1",original)
    # after = GaussianFilter(original)
    # # cv2.imshow("1",after)
    # # print(after)
    # plt_show(original,after)
    # cv2.waitKey(100000)
    #####################################
    image = np.zeros((100, 100))  # 背景图
    idx = np.arange(25, 75)  # 25-74序列
    image[idx[::-1], idx] = 255  # 线条\
    image[idx, idx] = 255  # 线条/
    # original = image
    # rospy.init_node('CV', anonymous=True)
    # rospy.Subscriber("/mode", String, callback)

    original = cv2.imread("./Img/llin.jpg")
    hoff = HF.line_cuda(original)
    util.plt_show(original,hoff)

