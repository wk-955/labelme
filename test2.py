import cv2
import numpy as np

imagePath = r'E:\数据测试\232点测试\2M0A7004.JPG'
img = cv2.imdecode(np.fromfile(imagePath, dtype=np.uint8), -1)


# print img.shape

def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        print(xy)
        cv2.circle(img, (x, y), 10, (0, 0, 255), thickness=-1)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    5, (0, 0, 255), thickness=4)
        cv2.imshow("image", img)


cv2.namedWindow("image", 0)
# cv2.setMouseCallback("image", on_EVENT_LBUTTONDOWN)
points = [[1838.0, 1866.0], [1830.0, 2000.0], [1830.0, 2132.0], [1836.0, 2266.0], [1852.0, 2398.0], [1872.0, 2530.0], [1900.0, 2662.0], [1934.0, 2796.0], [1980.0, 2922.0], [2042.0, 3040.0], [2120.0, 3150.0], [2214.0, 3246.0], [2322.0, 3328.0], [2440.0, 3402.0], [2568.0, 3460.0], [2710.0, 3496.0], [2864.0, 3504.0]]
for point in points:
    cv2.circle(img, (round(point[0]), round(point[1])), 5, (0, 0, 255), thickness=-1)
    cv2.putText(img, str(points.index(point)), (round(point[0]), round(point[1])), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 255), thickness=4)
    cv2.imshow("image", img)

cv2.imshow("image", img)


while (True):
    try:
        cv2.waitKey(100)
    except Exception:
        cv2.destroyWindow("image")
        break

cv2.waitKey(0)
cv2.destroyAllWindow()
