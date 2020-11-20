import numpy as np
import cv2


path1 = r'E:\a\4_mask.png'
path2 = r'E:\a\4_label.png'
path3 = r'E:\a\4.png'

img1 = cv2.imread(path1)
img2 = cv2.imread(path2)
img3 = cv2.imread(path3)

img1 = cv2.resize(img1, (500, 500))
img2 = cv2.resize(img2, (500, 500))
img3 = cv2.resize(img3, (500, 500))

hmerge = np.hstack((img3, img2, img1))
# cv2.imshow('a', img)
# cv2.waitKey(0)
cv2.imshow('a', hmerge)
cv2.waitKey(0)