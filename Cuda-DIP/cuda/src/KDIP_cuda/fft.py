# -*- coding: utf-8 -*-
"""
@author: Kevin
"""

import numpy


def FFT_v1(Img, Wr):
    if Img.shape[0] == 2:
        pic = numpy.zeros([2], dtype=complex)
        pic = pic * (1 + 0j)
        pic[0] = Img[0] + Img[1] * Wr[0]
        pic[1] = Img[0] - Img[1] * Wr[0]
        return pic
    else:
        pic = numpy.empty([Img.shape[0]], dtype=complex)
        pic[0:Img.shape[0] // 2] = FFT_v1(Img[::2], Wr[::2]) + Wr * FFT_v1(Img[1::2], Wr[::2])
        pic[Img.shape[0] // 2:Img.shape[0]] = FFT_v1(Img[::2], Wr[::2]) - Wr * FFT_v1(Img[1::2], Wr[::2])
        return pic;


def FFT_1d(Img):
    Wr = numpy.ones([Img.shape[0] // 2]) * [
        numpy.cos(2 * numpy.pi * i / Img.shape[0]) - 1j * numpy.sin(2 * numpy.pi * i / Img.shape[0]) for i in
        numpy.arange(Img.shape[0] / 2)]
    return FFT_v1(Img, Wr)


def FFT_2dd(Img):
    pic = numpy.zeros([Img.shape[0], Img.shape[1]], dtype=complex)
    for i in numpy.arange(Img.shape[0]):
        pic[:, i] = FFT_1d(Img[:, i])
    for i in numpy.arange(Img.shape[1]):
        pic[i, :] = FFT_1d(pic[i, :])

    return pic




import time


# if __name__ == "__main__":
#     array = numpy.zeros([512], dtype=complex)
#     array[0], array[1], array[2], array[3], array[4], array[5], array[6], array[7], array[8] = 1, 5, 3, 2, 5, 6, 1, 6, 3
#
#     img = data.camera()
#
#     print("numpy.fft.fft2()函数计算结果：")
#     t_s1 = time.time()
#     print(numpy.fft.fft2(img[:16, 0:16]))
#     t_e1 = time.time()
#     print("计算时间：" + str(t_e1 - t_s1))
#
#     print("FFT_2d()函数的计算结果：")
#     t_s2 = time.time()
#     print(FFT_2d(img[:16, 0:16]))
#     t_e2 = time.time()
#     print("计算时间：" + str(t_e2 - t_s2))
# io.imshow(numpy.log(numpy.real(numpy.fft.fft2(img))))
# io.imshow(numpy.real(FFT_2d(img[0:256,0:256])))
# img = data.camera()
# print(numpy.fft.fft2(img))
# io.imshow(FFT_2d(img))

