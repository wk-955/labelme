import math


class CalculationBisectionPoints:
    def __init__(self):
        # 间距
        self.spacing = 0
        # 总距离的和
        self.distanceSum = 0
        # 上一段线段剩余的距离
        self.surplusDistance = 0
        # 初始点数
        self.pointArr = []
        # 存放等分点的列表
        self.spacingPoints = []
        # 存放折线中每两点间距的列表
        self.distanceArr = []

    # 总长度
    def calculateDistanceSum(self, points):
        pointDistance = 0
        for i in range(len(points)-1):
            point1 = points[i]
            point2 = points[i+1]

            small_distance = self.calculateDistance(point1, point2)
            self.distanceSum += small_distance
            self.distanceArr.append(small_distance)
            pointDistance = self.distanceSum
        return pointDistance

    # 两点间距
    def calculateDistance(self, point1, point2):
        x = pow(point1[0] - point2[0], 2)
        y = pow(point1[1] - point2[1], 2)

        result = math.sqrt(x + y)


        return result

    # 计算λ s: 折线间距 n: 剩余长度
    def calculateLambda(self, s, n):
        lam = n / (s-n)
        return lam

    # 计算x坐标
    def calculateX(self, x1, x2, lam):
        x = (x1 + lam * x2) / (1 + lam)
        return x

    # 计算y坐标
    def calculateY(self, y1, y2, lam):
        y = (y1 + lam * y2) / (1 + lam)
        return y

    def doCalculate(self, i=0):

        if i < (len(self.pointArr)-1):
            startPoint = self.pointArr[i]
            endPoint = self.pointArr[i+1]
            if self.spacing:
                # 间隔个数
                pointNum = int((self.distanceArr[i] + self.surplusDistance) / self.spacing)

                if pointNum > 0:
                    for j in range(pointNum):

                        if j == 0:
                            n = self.spacing - self.surplusDistance
                            s = self.distanceArr[i]
                        else:
                            n = (j+1) * self.spacing - self.surplusDistance
                            s = self.distanceArr[i]

                        if n != s:
                            lam = self.calculateLambda(s, n)
                            x = self.calculateX(startPoint[0], endPoint[0], lam)
                            y = self.calculateY(startPoint[1], endPoint[1], lam)

                            newPoint = (x, y)
                            self.spacingPoints.append(newPoint)
                        else:
                            self.spacingPoints.append(endPoint)

                    self.surplusDistance += (self.distanceArr[i] - pointNum*self.spacing)
                else:
                    self.surplusDistance += (self.distanceArr[i] - pointNum*self.spacing)

                self.doCalculate(i+1)