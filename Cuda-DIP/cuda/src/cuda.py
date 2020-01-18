import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import time
import cv2

import math
from matplotlib import  pyplot as plt
################## Constant #############################
# 滤波3x3
kernel_3x3 = np.ones((3, 3))
# 滤波5x5
kernel_5x5 = np.ones((5, 5))
# sobel 算子
sobel_1 = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]])
sobel_2 = np.array([[-1, -2, -1],
                    [0, 0, 0],
                    [1, 2, 1]])
# prewitt 算子
prewitt_1 = np.array([[-1, 0, 1],
                      [-1, 0, 1],
                      [-1, 0, 1]])
prewitt_2 = np.array([[-1, -1, -1],
                      [0, 0, 0],
                      [1, 1, 1]])
# Laplace 算子
laplace_8 = np.array([[1,1,1],
                      [1,-8,1],
                      [1,1,1]])
laplace_4 = np.array([[0,1,0],
                      [1,-4,1],
                      [0,1,0]])
laplace_9 = np.array([[1,1,1],
                      [1,-9,1],
                      [1,1,1]])
##################################################

def plt_show(*args):
    num = len(args)*2
    x = int(math.sqrt(num))
    if num%x:
        y=num // x +1
    else:
        y=num//x
    n = 100*x+10*y
    for i in range(0,num):
        n = n + 1

        if i<len(args):
            img = np.abs(args[i])
            # if np.mean(img) >  250:
            #     img = np.log(img)
            plt.subplot(n), plt.imshow(img,'gray'), plt.title(i+1)
            plt.axis('off')
        else:
            img = np.abs(args[i-len(args)])
            plt.subplot(n), plt.hist(img.ravel(), 256, [0, 256]), plt.title(i + 1)
            plt.axis('on')
    plt.show()


TILE_W = 16
TILE_H = 16
KERNEL_RADIUS = 1
KERNEL_W = 2 * KERNEL_RADIUS + 1
mod = SourceModule('''   
__global__ void convolutionGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS=1;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
    __shared__ float sPartials[KERNEL_W*KERNEL_W];    
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     for(int i=0 ;  i< KERNEL_W*KERNEL_W ; i++ )
     sPartials[i]= d_Kernel[i];//d_Kernel[gLoc1] ;

     float sum = 0; 
     float value = 0;
     for(int i = -KERNEL_RADIUS; i<=KERNEL_RADIUS ; i++)
     	for(int j = -KERNEL_RADIUS; j<=KERNEL_RADIUS ;j++ ){  
          if( (col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1) )
            value = 0;
          else        
             value = d_Data[total + i*dataW + j];
          sum += value * sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)];
    }
       d_Result[total] = sum;
 }
''')
convolutionGPU = mod.get_function("convolutionGPU")



def convolution_cuda(sourceImage, fil):
    sourceImage = np.float32(sourceImage)
    # Perform separable convolution on sourceImage using CUDA.
    destImage = sourceImage.copy()

    (imageHeight, imageWidth) = sourceImage.shape
    # print(imageWidth,imageHeight)
    fil = np.float32(fil)
    DATA_H = imageHeight;
    DATA_W = imageWidth
    DATA_H = np.int32(DATA_H)
    DATA_W = np.int32(DATA_W)
    # Prepare device arrays

    sourceImage_gpu = cuda.mem_alloc_like(sourceImage)
    fil_gpu = cuda.mem_alloc_like(fil)
    destImage_gpu = cuda.mem_alloc_like(sourceImage)

    cuda.memcpy_htod(sourceImage_gpu, sourceImage)
    cuda.memcpy_htod(fil_gpu, fil)
    convolutionGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)

    return destImage

def test_convolution_cuda(original,fil):
    original = np.float32(original)
    destImage = original.copy()
    destImage[:] = np.nan
    time_b = time.time()
    destImage = convolution_cuda(original, fil)
    time_e = time.time()
    # You probably wand to display the result image using the tool of your choice here.
    #print("GPU mode FPS =:",1/(time_e-time_b))
    # print(destImage)
    # plt_show(destImage)
    # print(destImage)
    return destImage

# 均值滤波
def AverageFilter(original, kernel):
    '''
    :param image: 图片矩阵
    :param kernel: 滤波窗口
    :return:均值滤波后的矩阵
    '''

    dist = convolution_cuda(original,kernel)
    dist= dist/(kernel.shape[0]**2)
    dist = np.uint8(dist)
    return dist

# 高斯滤波
def GaussianFilter(Image,sigma=1):
    '''
    :param sigma: σ标准差
    :return: 高斯滤波器的模板
    '''
    img_h = img_w = 2 * sigma + 1
    gaussian_mat = np.zeros((img_h, img_w))
    for x in range(-sigma, sigma + 1):
        for y in range(-sigma, sigma + 1):
            gaussian_mat[x + sigma][y + sigma] = np.exp(-0.5 * (x ** 2 + y ** 2) / (sigma ** 2))
    return AverageFilter(Image,gaussian_mat)

# Sobel Edge
def SobelEdgeFilter(image, sobel):
    '''
    :param image: 图片矩阵
    :param sobel: 滤波窗口
    :return:Sobel处理后的矩阵
    '''
    return convolution_cuda(image, sobel)

def PrewittEdgeFilter(image, prewitt_x, prewitt_y):
    '''
    :param image: 图片矩阵
    :param prewitt_x: 竖直方向
    :param prewitt_y:  水平方向
    :return:处理后的矩阵
    '''
    img_X = convolution_cuda(image, prewitt_x)
    img_Y = convolution_cuda(image, prewitt_y)

    img_prediction = np.zeros(img_X.shape)
    for i in range(img_prediction.shape[0]):
        for j in range(img_prediction.shape[1]):
            img_prediction[i][j] = max(img_X[i][j], img_Y[i][j])
    return img_prediction



mod2 = SourceModule('''   
__global__ void maxGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS=1;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     float max = 0; 
     float value = 0;
     for(int i = -KERNEL_RADIUS; i<=KERNEL_RADIUS ; i++){
     	for(int j = -KERNEL_RADIUS; j<=KERNEL_RADIUS ;j++ ){  
          if( (col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1) )
            value = 0;
          else  
          {      
             value = d_Data[total + i*dataW + j];
             if(max<value) max=value;
          }
        }
    }
       d_Result[total] = max;
 }
''')

maxGPU = mod2.get_function("maxGPU");

def maxFilter_cuda(sourceImage):
    sourceImage=np.float32(sourceImage)
    # Perform separable convolution on sourceImage using CUDA.
    destImage = sourceImage.copy()
    destImage = np.float32(destImage)
    fil=np.zeros((3,3))
    (imageHeight, imageWidth) = destImage.shape
    # print(imageWidth,imageHeight)
    fil = np.float32(fil)
    DATA_H = imageHeight;
    DATA_W = imageWidth
    DATA_H = np.int32(DATA_H)
    DATA_W = np.int32(DATA_W)
    # Prepare device arrays

    sourceImage_gpu = cuda.mem_alloc_like(sourceImage)
    fil_gpu = cuda.mem_alloc_like(fil)
    destImage_gpu = cuda.mem_alloc_like(sourceImage)

    cuda.memcpy_htod(sourceImage_gpu, sourceImage)
    cuda.memcpy_htod(fil_gpu, fil)
    maxGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    return destImage


mod3 = SourceModule('''   
__global__ void minGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS=1;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     float min = 255; 
     float value = 0;
     for(int i = -KERNEL_RADIUS; i<=KERNEL_RADIUS ; i++){
     	for(int j = -KERNEL_RADIUS; j<=KERNEL_RADIUS ;j++ ){  
          if( (col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1) )
            value = 0;
          else  
          {      
             value = d_Data[total + i*dataW + j];
             if(min>value) min=value;
          }
        }
    }
       d_Result[total] = min;
 }
''')

minGPU = mod3.get_function("minGPU");

def maxFilter_cuda(sourceImage):
    sourceImage=np.float32(sourceImage)
    # Perform separable convolution on sourceImage using CUDA.
    destImage = sourceImage.copy()
    destImage = np.float32(destImage)
    fil=np.zeros((3,3))
    (imageHeight, imageWidth) = destImage.shape
    # print(imageWidth,imageHeight)
    fil = np.float32(fil)
    DATA_H = imageHeight;
    DATA_W = imageWidth
    DATA_H = np.int32(DATA_H)
    DATA_W = np.int32(DATA_W)
    # Prepare device arrays

    sourceImage_gpu = cuda.mem_alloc_like(sourceImage)
    fil_gpu = cuda.mem_alloc_like(fil)
    destImage_gpu = cuda.mem_alloc_like(sourceImage)

    cuda.memcpy_htod(sourceImage_gpu, sourceImage)
    cuda.memcpy_htod(fil_gpu, fil)
    minGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    return destImage


mod4 = SourceModule('''   
__global__ void expandGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS=1;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
    __shared__ float sPartials[KERNEL_W*KERNEL_W];    
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     for(int i=0 ;  i< KERNEL_W*KERNEL_W ; i++ )
     sPartials[i]= d_Kernel[i];//d_Kernel[gLoc1] ;

     float sum = 0; 
     float value = 0;
     for(int i = -KERNEL_RADIUS; i<=KERNEL_RADIUS ; i++)
     	for(int j = -KERNEL_RADIUS; j<=KERNEL_RADIUS ;j++ ){  
          if( (col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1) )
            value = 0;
          else        
             value = d_Data[total + i*dataW + j];
          sum += value * sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)];
    }
       d_Result[total] = sum;
 }
''')


expandGPU = mod4.get_function("expandGPU");

def expand_cuda(sourceImage):
    sourceImage=np.float32(sourceImage)
    # Perform separable convolution on sourceImage using CUDA.
    destImage = sourceImage.copy()
    destImage = np.float32(destImage)
    fil=np.zeros((3,3))
    (imageHeight, imageWidth) = destImage.shape
    # print(imageWidth,imageHeight)
    fil = np.float32(fil)
    DATA_H = imageHeight;
    DATA_W = imageWidth
    DATA_H = np.int32(DATA_H)
    DATA_W = np.int32(DATA_W)
    # Prepare device arrays

    sourceImage_gpu = cuda.mem_alloc_like(sourceImage)
    fil_gpu = cuda.mem_alloc_like(fil)
    destImage_gpu = cuda.mem_alloc_like(sourceImage)

    cuda.memcpy_htod(sourceImage_gpu, sourceImage)
    cuda.memcpy_htod(fil_gpu, fil)
    minGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    return destImage
    sourceImage=np.float32(sourceImage)
    # Perform separable convolution on sourceImage using CUDA.
    destImage = sourceImage.copy()
    destImage = np.float32(destImage)
    fil=np.zeros((3,3))
    (imageHeight, imageWidth) = destImage.shape
    # print(imageWidth,imageHeight)
    fil = np.float32(fil)
    DATA_H = imageHeight;
    DATA_W = imageWidth
    DATA_H = np.int32(DATA_H)
    DATA_W = np.int32(DATA_W)
    # Prepare device arrays

    sourceImage_gpu = cuda.mem_alloc_like(sourceImage)
    fil_gpu = cuda.mem_alloc_like(fil)
    destImage_gpu = cuda.mem_alloc_like(sourceImage)

    cuda.memcpy_htod(sourceImage_gpu, sourceImage)
    cuda.memcpy_htod(fil_gpu, fil)
    minGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    return destImage