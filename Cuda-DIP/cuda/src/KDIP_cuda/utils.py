import math
import matplotlib.pyplot as plt
import numpy as np
import cv2
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

def putTex(str,Img,color = 1):
    if color == 0:
        cv2.putText(Img, str, (Img.shape[0] - 100, 100), cv2.FONT_HERSHEY_PLAIN, 6, (0,0,0), 3)
    else:
        cv2.putText(Img, str, (Img.shape[0] - 100, 100), cv2.FONT_HERSHEY_PLAIN, 6, (255, 255, 255), 3)