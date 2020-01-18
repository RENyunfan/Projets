import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import time
import cv2
import copy

TILE_W = 16
TILE_H = 16
KERNEL_RADIUS = 2
KERNEL_W = 2 * KERNEL_RADIUS + 1
mod = SourceModule('''   
__global__ void erodeGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS = 3;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
    __shared__ float sPartials[KERNEL_W*KERNEL_W];    
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     for(int i=0 ;  i< KERNEL_W*KERNEL_W ; i++ )
     sPartials[i]= d_Kernel[i];//d_Kernel[gLoc1] ;

     float sum = 0; 
     float value = 0;
     int flag=1;
     for (int i = -KERNEL_RADIUS; i <= KERNEL_RADIUS; i++){
     	for (int j = -KERNEL_RADIUS; j <= KERNEL_RADIUS; j++ ){  
          if((col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1))
          {
            return;
          }
          else
          {
            if(sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)]==0 && d_Data[total + i*dataW + j]==255 )
            {
                flag=0;
                break;
            }  
            else if(sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)]==1 && d_Data[total + i*dataW + j]==0 )
            {  
                flag=0;
                break;
            }  
          }        
        }
        sum = 255;
          if(flag == 0)
          {
            sum = 0;
            flag=1;
            break;
          }
    }
       d_Result[total] = sum;
 }
''')

erodeGPU = mod.get_function("erodeGPU")


def erode_cuda(sourceImage):
    fil = np.ones((7,7))
    # binary = th2 = cv2.adaptiveThreshold(sourceImage,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,2)#cv2.threshold(sourceImage, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    ret, binary = cv2.threshold(sourceImage, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    sourceImage = np.float32(binary)

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
    erodeGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight,1 , 1), grid=(1,imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)

    destImage=np.uint8(destImage)
    return destImage




mod2 = SourceModule('''   
__global__ void expandGPU(float *d_Result,float *d_Data,float *d_Kernel ,int dataW ,int dataH )
{
    const  int   KERNEL_RADIUS = 3;  
    const  int   KERNEL_W = 2 * KERNEL_RADIUS + 1;
    __shared__ float sPartials[KERNEL_W*KERNEL_W];    
     int row = threadIdx.x + blockDim.x * blockIdx.x;
     int col = threadIdx.y + blockDim.y * blockIdx.y;
     int total = row*dataW + col;//*dataW;

     for(int i=0 ;  i< KERNEL_W*KERNEL_W ; i++ )
     sPartials[i]= d_Kernel[i];//d_Kernel[gLoc1] ;

     float sum = 0; 
     float value = 0;
     int flag=1;
     for (int i = -KERNEL_RADIUS; i <= KERNEL_RADIUS; i++){
     	for (int j = -KERNEL_RADIUS; j <= KERNEL_RADIUS; j++ ){  
          if((col+j)<0 ||(row+i) < 0 ||(row+i) > (dataH-1) ||(col+j )>(dataW-1))
          {
            continue;
          }
          else
          {
            if(sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)]==0 && d_Data[total + i*dataW + j]==0 )
            {
                flag=0;
                break;
            }  
            else if(sPartials[(i+KERNEL_RADIUS)*KERNEL_W + (j+KERNEL_RADIUS)]==1 && d_Data[total + i*dataW + j]==255 )
            {  
                flag=0;
                break;
            }  
          }        
        }
        sum = 0;
          if(flag == 0)
          {
            sum = 255;
            flag=1;
            break;
          }
    }
       d_Result[total] = sum;
 }
''')


expandGPU = mod2.get_function("expandGPU");

def dilate_cuda(sourceImage):
    fil = np.ones((7, 7))
    # binary = th2 = cv2.adaptiveThreshold(sourceImage, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3,
    #                                      2)  # cv2.threshold(sourceImage, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    ret, binary = cv2.threshold(sourceImage, 0, 255, cv2.THRESH_OTSU|cv2.THRESH_BINARY_INV)
    sourceImage = np.float32(binary)
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
    expandGPU(destImage_gpu, sourceImage_gpu, fil_gpu, DATA_W, DATA_H, block=(imageHeight, 1, 1), grid=(1, imageWidth))
    # Pull the data back from the GPU.
    cuda.memcpy_dtoh(destImage, destImage_gpu)
    destImage = np.uint8(destImage)
    return destImage