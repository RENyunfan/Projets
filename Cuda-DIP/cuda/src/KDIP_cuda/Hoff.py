import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import time
import cv2
import math
from matplotlib import  pyplot as plt


# mod = SourceModule('''
# __global__ void HoffGPU(float *d_Result,float *d_IMG,int theta,int dataW ,int dataH )
# {
#     int row = threadIdx.x + blockDim.x * blockIdx.x;
#     int col = threadIdx.y + blockDim.y * blockIdx.y;
#     int total = row*dataW + col;//*dataW;
#     float rho = 0;
#     if(d_IMG[total]>0)
#      {
#         rho = row * cos(float(theta)) + col *sin(float(theta));
#         d_Result[total] = rho;
#      }
#      else d_Result[total] = 0;
#
#
#
#  }
# ''')
mod = SourceModule('''   
__global__ void HoffGPU(float *d_Result,float *d_IMG,int dataW ,int dataH )
{   
    int thetas = blockIdx.x;
    int row = threadIdx.x ;//+ blockDim.x * blockIdx.x;
    int col = threadIdx.y ;//+ blockDim.y * blockIdx.y;
    int total = thetas*dataH*dataW+row*dataW + col;//*dataW;
    float rho = 0;
    if(d_IMG[total]>0)
     {
        ///rho = row * cos(float(theta)) + col *sin(float(theta));
        d_Result[total] = rho;
     }
     else d_Result[total] = 0;



 }
''')
HoffGPU = mod.get_function("HoffGPU");
def line_cuda(sourceImage):
    time_e = time.time()
    gray = cv2.cvtColor(sourceImage, cv2.COLOR_BGR2GRAY)
    # binary = th2 = cv2.adaptiveThreshold(sourceImage,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,2)#cv2.threshold(sourceImage, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    # gray = sourceImage
    binary=np.float32(gray)

    destImage = np.float32(gray*5)
    (imageHeight, imageWidth) = gray.shape
    DATA_H = np.int32(imageHeight)
    DATA_W = np.int32(imageWidth)

    # for i in range( -90,90):
    #     sourceImage_gpu = cuda.mem_alloc_like(binary)
    #     destImage_gpu = cuda.mem_alloc_like(binary)
    #     cuda.memcpy_htod(sourceImage_gpu, binary)
    #     theta = np.int32(i)
    #     HoffGPU(destImage_gpu, sourceImage_gpu, theta, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    #     cuda.memcpy_dtoh(destImage, destImage_gpu)
    #     ans = np.sort(destImage)

    sourceImage_gpu = cuda.mem_alloc_like(binary)
    destImage_gpu = cuda.mem_alloc_like(destImage)
    cuda.memcpy_htod(sourceImage_gpu, binary)
    HoffGPU(destImage_gpu, sourceImage_gpu, DATA_W, DATA_H, block=(1,1,1), grid=(imageWidth, imageHeight))
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    ans = np.sort(destImage)

    time_b = time.time()
    print("GPU mode time:",  (time_b - time_e))
    return binary
