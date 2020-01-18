#!/usr/bin/env python
#-*-coding=utf-8-*-
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
import rospy

from std_msgs.msg import String

import rospy
from std_msgs.msg import String
mode = "LPF"
last_mode = "All"
def callback(data):
    global mode 
    mode = data.data
    print("111",mode)
    
 
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

    rospy.init_node('CV', anonymous=True)
    rospy.Subscriber("/mode", String, callback)
 
    # spin() simply keeps python from exiting until this node is stopped
    mode = "None"
    cap = cv2.VideoCapture(1)
    while (cap.isOpened() and not rospy.is_shutdown()):
        # 计时
        time_e = time.time()
        # 读取并处理
        _,original=cap.read()
        if original.shape[1]>680:
            original = original[:,0:original.shape[1]//2]
        gray = cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)
        Hoff = HF.line_cuda(gray)
        average= ft.AverageFilter(gray)
        gaussian = ft.GaussianFilter(gray)
        fft = ft.FFT_2d(gray)
        LPF = ft.LPF_cuda(fft,100)
        erode=mo.erode_cuda(gray)
        dilate = mo.dilate_cuda(gray)
        # 打标
        util.putTex("Org", original)
        util.putTex("Gau", gaussian)
        util.putTex("Gray", gray)
        util.putTex("LPF", LPF)
        util.putTex("Erode", erode)
        util.putTex("Dilate", dilate)
        util.putTex("Average", average)
        # 输出模式选择
        if mode == "All":
            A = np.hstack((gray,gaussian,LPF))
            B = np.hstack((erode,dilate,average))
            C = np.vstack((A,B))
            D = cv2.resize(C,(1024,512))
            cv2.imshow("filter", D)
            cv2.imshow("Org", original)
        elif mode == "Gau":
            cv2.imshow("Gau", gaussian)
        elif mode == "LPF":
            cv2.imshow("LPF", LPF)
        elif mode == "Dia":
            cv2.imshow("Dilate", dilate)
        elif mode == "Gra":
            cv2.imshow("Gray", gray)
        elif mode == "Ero":
            cv2.imshow("Erode", erode)
        elif mode =="Ave":
            cv2.imshow("Average", average)
        elif mode =="None":
            continue
        # cv2.imshow("Gau", gaussian)
        # cv2.imshow("Gray", gray)
        # cv2.imshow("LPF", LPF)
        # cv2.imshow("Erode", erode)
        # cv2.imshow("Dilate", dilate)
        # cv2.imshow("Average", average)
        # util.plt_show(original,LPF)
        # plt.ion()
        time_b = time.time()
        print("GPU mode FPS:",1/(time_b-time_e))
        if(cv2.waitKey(1) == ord('q') ):
            break
        # if getKey() == ord('i'):
        if(mode != last_mode):
            last_mode = mode
            cv2.destroyAllWindows()
    rospy.spin()
    cap.release()
    cv2.destroyAllWindows()
