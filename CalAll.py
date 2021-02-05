from SpacingAlgo import CalculationBisectionPoints


class CalAll:

    def __init__(self):
        self.shapes = []

    def Line(self):
        if self.shapes:
            left_line1 = []
            left_line2 = []
            right_line1 = []
            right_line2 = []
            other = []
            for shape in self.shapes:
                if shape["shape_type"] == "linestrip" and shape["label"] == "left":
                    left_line1 = shape["points"][:5]
                    left_line2 = shape["points"][4:]
                elif shape["shape_type"] == "linestrip" and shape["label"] == "right":
                    right_line1 = shape["points"][:5]
                    right_line2 = shape["points"][4:]
                elif shape["shape_type"] == "point" and shape["label"] == '0':
                    left_line1.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '4':
                    left_line1.append(shape["points"][0])
                    left_line2.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '8':
                    left_line2.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '9':
                    right_line1.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '13':
                    right_line1.append(shape["points"][0])
                    right_line2.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '17':
                    right_line2.append(shape["points"][0])
                else:
                    other.append(shape)
            if left_line1 and left_line2 and right_line1 and right_line2 :
                new_shapes = []
                left = self.LeftLine(left_line1, left_line2)
                l = {
                    "label": "left",
                    "points": left,
                    "group_id": None,
                    "shape_type": "linestrip",
                    "flags": {}
                }
                new_shapes.append(l)

                right = self.RightLine(right_line1, right_line2)
                r = {
                    "label": "right",
                    "points": right,
                    "group_id": None,
                    "shape_type": "linestrip",
                    "flags": {}
                }
                new_shapes.append(r)
                # if len(new_shapes) == 18:
                new_shapes += other
                # print(new_shapes)
                self.shapes = new_shapes
                return self.shapes

    def LLine(self):
        if self.shapes:
            left_line1 = []
            left_line2 = []
            other = []
            for shape in self.shapes:
                if shape["shape_type"] == "linestrip" and shape["label"] == "left":
                    left_line1 = shape["points"][:5]
                    left_line2 = shape["points"][4:]
                elif shape["shape_type"] == "point" and shape["label"] == '0':
                    left_line1.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '4':
                    left_line1.append(shape["points"][0])
                    left_line2.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '8':
                    left_line2.append(shape["points"][0])
                else:
                    other.append(shape)
            if left_line1 and left_line2:
                new_shapes = []
                left = self.LeftLine(left_line1, left_line2)
                l = {
                    "label": "left",
                    "points": left,
                    "group_id": None,
                    "shape_type": "linestrip",
                    "flags": {}
                }
                new_shapes.append(l)
                new_shapes += other
                self.shapes = new_shapes
                return self.shapes

    def RLine(self):
        if self.shapes:
            right_line1 = []
            right_line2 = []
            other = []
            for shape in self.shapes:
                if shape["shape_type"] == "linestrip" and shape["label"] == "right":
                    right_line1 = shape["points"][:5]
                    right_line2 = shape["points"][4:]
                elif shape["shape_type"] == "point" and shape["label"] == '9':
                    right_line1.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '13':
                    right_line1.append(shape["points"][0])
                    right_line2.append(shape["points"][0])
                elif shape["shape_type"] == "point" and shape["label"] == '17':
                    right_line2.append(shape["points"][0])
                else:
                    other.append(shape)
            if right_line1 and right_line2:
                new_shapes = []
                right = self.RightLine(right_line1, right_line2)
                r = {
                    "label": "right",
                    "points": right,
                    "group_id": None,
                    "shape_type": "linestrip",
                    "flags": {}
                }
                new_shapes.append(r)
                new_shapes += other
                self.shapes = new_shapes
                return self.shapes

    def LeftLine(self, line1, line2):
        new = [line1[0]]
        new_points = self.Cal(line1, 4)
        for i in new_points[:3]:
            new.append([i[0], i[1]])
        new.append(line1[-1])
        new_points = self.Cal(line2, 4)
        for i in new_points[:3]:
            new.append([i[0], i[1]])
        new.append(line2[-1])
        return new

    def RightLine(self, line1, line2):
        new = [line1[0]]
        new_points = self.Cal(line1, 4)
        for i in new_points[:3]:
            new.append([i[0], i[1]])
        new.append(line1[-1])
        new_points = self.Cal(line2, 4)
        for i in new_points[:3]:
            new.append([i[0], i[1]])
        new.append(line2[-1])
        return new

    def Cal(self, points, intervalNum):
        # points = [points[0]] + list(sorted(points[1:-1], key=lambda x: x[0])) + [points[-1]]

        c = CalculationBisectionPoints()
        long = c.calculateDistanceSum(points)
        c.pointArr = points
        c.spacing = long / intervalNum
        c.doCalculate()
        return c.spacingPoints

    def CalMid(self, point1, point2):
        x = (point1[0] + point2[0]) / 2
        y = (point1[1] + point2[1]) / 2
        return [x, y]

    def CalMidPoints(self, line1, line2):
        x1, y1, x2, y2 = line1[0], line1[1], line1[2], line1[3]
        x3, y3, x4, y4 = line2[0], line2[1], line2[2], line2[3]

        k1 = (y2 - y1) * 1.0 / (x2 - x1)
        b1 = y1 * 1.0 - x1 * k1 * 1.0
        if (x4 - x3) == 0:
            k2 = None
            b2 = 0
        else:
            k2 = (y4 - y3) * 1.0 / (x4 - x3)
            b2 = y3 * 1.0 - x3 * k2 * 1.0
        if k2 == None:
            x = x3
        else:
            x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0
        return [x, y]
