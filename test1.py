import os
import sys
import cv2
import numpy as np
import matplotlib

imagePath = r"E:\数据测试\232点测试数据\2M0A7004.JPG"

image = cv2.imdecode(np.fromfile(imagePath, dtype=np.uint8), -1)

point_size = 5
point_color = (0, 0, 255)  # BGR
thickness = 4  # 0 、4、8

# 此处省略得到坐标的过程，coordinates存放坐标
# 格式为：coordinates=[[x1,y1],[x2,y2],[x3,y3],...,[xn,yn]]

coordinates = [[1838.0, 1866.0], [1830.0, 2000.0], [1830.0, 2132.0], [1836.0, 2266.0], [1852.0, 2398.0], [1872.0, 2530.0], [1900.0, 2662.0], [1934.0, 2796.0], [1980.0, 2922.0], [2042.0, 3040.0], [2120.0, 3150.0], [2214.0, 3246.0], [2322.0, 3328.0], [2440.0, 3402.0], [2568.0, 3460.0], [2710.0, 3496.0], [2864.0, 3504.0]]
for coor in coordinates:
    print(coor)

    cv2.circle(image, (int(coor[0]), int(coor[1])), point_size, point_color, thickness)
cv2.namedWindow("a", 0)
cv2.imshow('a', image)
cv2.waitKey(0)

# cv2.imwrite('1.png', image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])