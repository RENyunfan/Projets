#-*-coding=utf-8=-*-
import cv2
import numpy as np

# 绘制初始的图像（即初始化一个500*500的矩阵，并画上一条线）
img = np.zeros([500, 500]).astype(np.uint8)  # 创建一个矩阵
cv2.line(img, (50, 50), (100, 100), 255)  # 画直线
cv2.imshow('', img)
# 将关键点，也就是线上的点放入key_points列表中
key_points = []
for y_cnt in range(0, 500):  # 将直线上的点取出（白点即像素值为255的点）
    for x_cnt in range(0, 500):
        if img[y_cnt][x_cnt] == 255:
            key_points.append((x_cnt, y_cnt))
# 将key_points中的点转换到霍夫空间中，间隔的θ为1度，在笛卡尔坐标系中可以描述成在-90°到90°间以点为中心每隔1°画一条直线
conver_points = []
for key_point in key_points:  # 将点转换到霍夫空间
    conver_points_tmp = []
    for theta in range(-90, 90):  # 从-90°到90°打点，间隔1°
        x, y = key_point
        rho = x * np.cos(theta / 180 * np.pi) + y * np.sin(theta / 180 * np.pi)  # 注意将角度转换成弧度
        conver_points_tmp.append((int(theta), int(rho)))
    conver_points.append(conver_points_tmp)
# 绘制换换到霍夫空间的曲线
hough_img = np.zeros([710, 180]).astype(np.uint8)  # 转换成uint8的图像，否则imshow无法显示
for conver_point in conver_points:  # 绘制霍夫空间的曲线
    for point in conver_point:
        theta, rho = point
        hough_img[rho - 350][theta - 90] = 255

cv2.imshow('hough', hough_img)
cv2.waitKey()
