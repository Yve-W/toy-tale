import cv2
import numpy as np

#The picture should be in the current directory

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
img=cv2.imread("img.jpg",1)
cv2.setWindowProperty('image',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()