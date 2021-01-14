from SpacingAlgo import CalculationBisectionPoints
import math


class CalAuto:

    def __init__(self):
        self.shapes = []
        self.newShapes = []

    def deal(self):
        self.autoFace()
        self.autoEyebrow()
        self.autoEye()
        self.autoMouse()
        self.autoNose()
        self.autoEyepupli()
        # return self.newShapes

    # 脸颊
    def autoFace(self):
        try:
            face = []
            for shape in self.shapes[26:29]:
                face.append(shape["points"][0])
            intervalNum = 17
            points = self.Cal(face, intervalNum)
            points += [face[2]]
            if points:
                count = 0
                for i in range(0, 17):
                    shape = {
                        "label": "{}".format(i),
                        "points": [list(points[count])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                    count += 1

            face = []
            for shape in self.shapes[28:31]:
                face.append(shape["points"][0])
            intervalNum = 16
            points = self.Cal(face, intervalNum)
            if points:
                count = 0
                for i in range(0, 16):
                    shape = {
                        "label": "{}".format(i+17),
                        "points": [list(points[count])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                    count += 1
        except Exception as e:
            print(e)

    # 眉毛
    def autoEyebrow(self):
        try:
            left_eye = []
            for shape in self.shapes[:3]:
                left_eye.append(shape["points"][0])
            # 106点的
            intervalNum = 4
            points = self.Cal(left_eye, intervalNum)
            points = self.shapes[0]["points"] + points + self.shapes[2]["points"]
            for i in range(33, 38):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i-33])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            left_eye[1] = self.shapes[3]["points"][0]
            left_eye[2] = self.shapes[4]["points"][0]
            points = self.Cal(left_eye, intervalNum)
            points = points + self.shapes[4]["points"]
            for i in range(64, 68):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 64])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            # 134点的
            left_eye = []
            for shape in self.shapes[:3]:
                left_eye.append(shape["points"][0])
            # 106点的
            intervalNum = 6
            points = self.Cal(left_eye, intervalNum)
            points = self.shapes[0]["points"] + points + self.shapes[2]["points"]
            for i in range(44, 51):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 44])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            left_eye[1] = self.shapes[3]["points"][0]
            left_eye[2] = self.shapes[4]["points"][0]
            points = self.Cal(left_eye, intervalNum)
            points = points + self.shapes[4]["points"]
            for i in range(51, 57):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 51])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            right_eye = []
            for shape in self.shapes[5:8]:
                right_eye.append(shape["points"][0])
            intervalNum = 4
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[5]["points"] + points + self.shapes[7]["points"]
            for i in range(38, 43):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i-38])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            right_eye[0] = self.shapes[8]["points"][0]
            right_eye[1] = self.shapes[9]["points"][0]
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[8]["points"] + points
            for i in range(68, 72):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 68])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            # 134点的
            right_eye = []
            for shape in self.shapes[5:8]:
                right_eye.append(shape["points"][0])
            intervalNum = 6
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[5]["points"] + points + self.shapes[8]["points"]

            count = 0
            for i in range(63, 56, -1):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[count])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                count += 1
                self.newShapes.append(shape)

            right_eye[0] = self.shapes[8]["points"][0]
            right_eye[1] = self.shapes[9]["points"][0]
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[8]["points"] + points
            count = 0
            for i in range(69, 63, -1):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[count])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                count += 1
                self.newShapes.append(shape)
        except Exception as e:
            print(e)

    # 眼睛
    def autoEye(self):
        try:
            left_eye = []
            for shape in self.shapes[10:13]:
                left_eye.append(shape["points"][0])
            # 106点的
            intervalNum = 4
            points = self.Cal(left_eye, intervalNum)
            points = self.shapes[10]["points"] + points + self.shapes[12]["points"]
            for i in range(52, 57):
                if i<54:
                    shape = {
                        "label": "{}".format(i),
                        "points": [list(points[i - 52])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                elif i==54:
                    shape = {
                        "label": "{}".format(72),
                        "points": [list(points[i - 52])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                else:
                    shape = {
                        "label": "{}".format(i-1),
                        "points": [list(points[i - 52])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)

            intervalNum = 11
            points = self.Cal(left_eye, intervalNum)
            points = self.shapes[10]["points"] + points
            for i in range(11, 22):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 11])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            left_eye[1] = self.shapes[13]["points"][0]
            intervalNum = 4
            points = self.Cal(left_eye, intervalNum)
            for i in range(0, 3):
                if i < 1:
                    shape = {
                        "label": "{}".format(57),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                elif i == 1:
                    shape = {
                        "label": "{}".format(73),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                else:
                    shape = {
                        "label": "{}".format(56),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)

            intervalNum = 11
            points = self.Cal(left_eye, intervalNum)
            points = points + self.shapes[12]["points"]
            for i in range(0, 11):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            right_eye = []
            for shape in self.shapes[14:17]:
                right_eye.append(shape["points"][0])
            # 106点的
            intervalNum = 4
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[14]["points"] + points + self.shapes[16]["points"]
            for i in range(58, 63):
                if i < 60:
                    shape = {
                        "label": "{}".format(i),
                        "points": [list(points[i - 58])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                elif i == 60:
                    shape = {
                        "label": "{}".format(75),
                        "points": [list(points[i - 58])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                else:
                    shape = {
                        "label": "{}".format(i - 1),
                        "points": [list(points[i - 58])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)

            intervalNum = 11
            points = self.Cal(right_eye, intervalNum)
            points += [right_eye[2]]
            count = 43
            for i in range(11):
                shape = {
                    "label": "{}".format(count),
                    "points": [list(points[i])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                count -= 1
                self.newShapes.append(shape)

            right_eye[1] = self.shapes[17]["points"][0]
            intervalNum = 4
            points = self.Cal(right_eye, intervalNum)
            for i in range(0, 3):
                if i < 1:
                    shape = {
                        "label": "{}".format(63),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                elif i == 1:
                    shape = {
                        "label": "{}".format(76),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                else:
                    shape = {
                        "label": "{}".format(62),
                        "points": [list(points[i])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)

            intervalNum = 11
            points = self.Cal(right_eye, intervalNum)
            points = self.shapes[14]["points"] + points + self.shapes[16]["points"]
            count = 32
            for i in range(0, 11):
                shape = {
                    "label": "{}".format(count),
                    "points": [list(points[i])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                count -= 1
                self.newShapes.append(shape)
        except Exception as e:
            print(e)

    # 嘴巴
    # def autoMouse(self):
    #     try:
    #         mouse = []
    #         for shape in self.shapes:
    #             if shape["group_id"] == 'mouse':
    #                 mouse.append(shape["points"][0])
    #         upper = mouse[:3]
    #         # 106点的
    #         intervalNum = 6
    #         points = self.Cal(upper, intervalNum)
    #         points = [upper[0]] + points + [upper[2]]
    #         for i in range(84, 91):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 84])],
    #                 "group_id": "stMobile106",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #
    #         intervalNum = 16
    #         points = self.Cal(upper, intervalNum)
    #         points = [upper[0]] + points + [upper[2]]
    #         for i in range(70, 87):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 70])],
    #                 "group_id": "extraFacePoints",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #
    #         intervalNum = 6
    #         upper[1] = mouse[3]
    #         points = self.Cal(upper, intervalNum)
    #         points = points
    #         for i in range(96, 101):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 96])],
    #                 "group_id": "stMobile106",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #
    #         intervalNum = 18
    #         points = self.Cal(upper, intervalNum)
    #         for i in range(87, 104):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 87])],
    #                 "group_id": "extraFacePoints",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #
    #         # 下唇
    #         lower = [mouse[0]] + [mouse[4]] + [mouse[2]]
    #         # 106点的
    #         intervalNum = 4
    #         points = self.Cal(lower, intervalNum)
    #         count = 103
    #         for i in range(3):
    #             shape = {
    #                 "label": "{}".format(count),
    #                 "points": [list(points[i])],
    #                 "group_id": "stMobile106",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             count -= 1
    #             self.newShapes.append(shape)
    #
    #         intervalNum = 16
    #         points = self.Cal(lower, intervalNum)
    #         for i in range(104, 119):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 104])],
    #                 "group_id": "extraFacePoints",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #
    #         lower[1] = mouse[5]
    #         intervalNum = 6
    #         points = self.Cal(lower, intervalNum)
    #         count = 95
    #         for i in range(5):
    #             shape = {
    #                 "label": "{}".format(count),
    #                 "points": [list(points[i])],
    #                 "group_id": "stMobile106",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             count -= 1
    #             self.newShapes.append(shape)
    #
    #         intervalNum = 16
    #         points = self.Cal(lower, intervalNum)
    #         for i in range(119, 134):
    #             shape = {
    #                 "label": "{}".format(i),
    #                 "points": [list(points[i - 119])],
    #                 "group_id": "extraFacePoints",
    #                 "shape_type": "point",
    #                 "flags": {}
    #             }
    #             self.newShapes.append(shape)
    #     except Exception as e:
    #         print(e)
    # 嘴唇
    def autoMouse(self):
        try:
            mouse = []
            for shape in self.shapes:
                if shape["group_id"] == 'mouse':
                    mouse.append(shape["points"][0])
            upper = mouse[:2]
            # 106点的
            intervalNum = 3
            points = self.Cal(upper, intervalNum)
            points = [upper[0]] + points + [upper[1]]
            for i in range(84, 88):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 84])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            intervalNum = 8
            points = self.Cal(upper, intervalNum)
            points = [upper[0]] + points + [upper[1]]
            for i in range(70, 79):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 70])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            upper = mouse[1:3]
            intervalNum = 3
            points = self.Cal(upper, intervalNum)
            points += [upper[1]]
            for i in range(88, 91):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 88])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            intervalNum = 8
            points = self.Cal(upper, intervalNum)
            points = points + [upper[1]]
            for i in range(79, 87):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 79])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            upper = [mouse[0]] + [mouse[3]]
            intervalNum = 3
            points = self.Cal(upper, intervalNum)
            points = points + [upper[1]]
            for i in range(96, 99):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 96])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            intervalNum = 9
            points = self.Cal(upper, intervalNum)
            points += [upper[1]]
            for i in range(87, 96):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 87])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            upper = [mouse[3]] + [mouse[2]]
            intervalNum = 3
            points = self.Cal(upper, intervalNum)
            points = points
            for i in range(99, 101):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 99])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            intervalNum = 9
            points = self.Cal(upper, intervalNum)
            for i in range(96, 104):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 96])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            # 下唇
            lower = [mouse[0]] + [mouse[4]]
            # 106点的
            intervalNum = 2
            points = self.Cal(lower, intervalNum)
            points += [lower[1]]
            count = 103
            for i in range(2):
                shape = {
                    "label": "{}".format(count),
                    "points": [list(points[i])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                count -= 1
                self.newShapes.append(shape)

            lower = [mouse[4]] + [mouse[2]]
            intervalNum = 2
            points = self.Cal(lower, intervalNum)
            shape = {
                "label": "{}".format(101),
                "points": [list(points[0])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            lower = [mouse[0]] + [mouse[5]]
            intervalNum = 3
            points = self.Cal(lower, intervalNum)
            points += [lower[1]]
            count = 95
            for i in range(3):
                shape = {
                    "label": "{}".format(count),
                    "points": [list(points[i])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                count -= 1
                self.newShapes.append(shape)

            lower = [mouse[5]] + [mouse[2]]
            intervalNum = 3
            points = self.Cal(lower, intervalNum)
            count = 92
            for i in range(2):
                shape = {
                    "label": "{}".format(count),
                    "points": [list(points[i])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                count -= 1
                self.newShapes.append(shape)

            lower = [mouse[0]] + [mouse[4]]
            intervalNum = 8
            points = self.Cal(lower, intervalNum)
            for i in range(104, 112):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 104])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            lower = [mouse[4]] + [mouse[2]]
            intervalNum = 8
            points = self.Cal(lower, intervalNum)
            for i in range(112, 119):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 112])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            lower = [mouse[0]] + [mouse[5]]
            intervalNum = 8
            points = self.Cal(lower, intervalNum)
            points += [lower[1]]
            for i in range(119, 127):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 119])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            lower = [mouse[5]] + [mouse[2]]
            intervalNum = 8
            points = self.Cal(lower, intervalNum)
            for i in range(127, 134):
                shape = {
                    "label": "{}".format(i),
                    "points": [list(points[i - 127])],
                    "group_id": "extraFacePoints",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

        except Exception as e:
            print(e)

    # 鼻子
    def autoNose(self):
        try:
            nose = []
            for shape in self.shapes:
                if shape["group_id"] == 'nose':
                    nose.append(shape["points"][0])
                elif shape["group_id"] == 'left_eye' and shape["label"] == "12":
                    eye1 = shape["points"][0]
                elif shape["group_id"] == 'right_eye' and shape["label"] == "15":
                    eye2 = shape["points"][0]
            intervalNum = 4
            points = self.Cal(nose, intervalNum)
            points = [nose[0]] + points + [nose[1]]
            for i in range(43, 48):
                if i == 47:
                    shape = {
                        "label": "{}".format(49),
                        "points": [list(points[i - 43])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)
                else:
                    shape = {
                        "label": "{}".format(i),
                        "points": [list(points[i - 43])],
                        "group_id": "stMobile106",
                        "shape_type": "point",
                        "flags": {}
                    }
                    self.newShapes.append(shape)

            shape = {
                "label": "{}".format(78),
                "points": [self.CalMid(eye1, nose[0])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)
            shape = {
                "label": "{}".format(79),
                "points": [self.CalMid(eye2, nose[0])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            shape = {
                "label": "{}".format(80),
                "points": [self.CalMid(self.CalMid(eye1, nose[0]), [eye1[0], nose[1][1]])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            shape = {
                "label": "{}".format(81),
                "points": [self.CalMid(self.CalMid(eye2, nose[0]), [eye2[0], nose[1][1]])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            shape = {
                "label": "{}".format(82),
                "points": [[eye1[0], nose[1][1]]],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            shape = {
                "label": "{}".format(83),
                "points": [[eye2[0], nose[1][1]]],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            intervalNum = 3
            n1 = [[eye1[0], nose[1][1]], nose[1]]
            points = self.Cal(n1, intervalNum)
            for num in range(47, 49):
                shape = {
                    "label": "{}".format(num),
                    "points": [list(points[num - 47])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)

            n2 = [[eye2[0], nose[1][1]], nose[1]]
            points = self.Cal(n2, intervalNum)
            for num in range(50, 52):
                shape = {
                    "label": "{}".format(num),
                    "points": [list(points[num - 50])],
                    "group_id": "stMobile106",
                    "shape_type": "point",
                    "flags": {}
                }
                self.newShapes.append(shape)
        except Exception as e:
            print(e)

    # 眼瞳
    def autoEyepupli(self):
        try:
            left_eye = []
            for shape in self.shapes:
                if shape["label"] in ['11', '13']:
                    left_eye.append(shape["points"][0])
            shape = {
                "label": "{}".format(74),
                "points": [self.CalMid(left_eye[0], left_eye[1])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)
            shape = {
                "label": "{}".format(104),
                "points": [self.CalMid(left_eye[0], left_eye[1])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)
            shape = {
                "label": "{}".format(0),
                "points": [self.CalMid(left_eye[0], left_eye[1])],
                "group_id": "eyeballCenter",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            right_eye = []
            for shape in self.shapes:
                if shape["label"] in ['16', '18']:
                    right_eye.append(shape["points"][0])
            shape = {
                "label": "{}".format(77),
                "points": [self.CalMid(right_eye[0], right_eye[1])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)
            shape = {
                "label": "{}".format(105),
                "points": [self.CalMid(right_eye[0], right_eye[1])],
                "group_id": "stMobile106",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)
            shape = {
                "label": "{}".format(1),
                "points": [self.CalMid(right_eye[0], right_eye[1])],
                "group_id": "eyeballCenter",
                "shape_type": "point",
                "flags": {}
            }
            self.newShapes.append(shape)

            left_eye[0] = self.CalMid(left_eye[0], left_eye[1])
            self.CalLPupil(left_eye[0], left_eye[1])

            right_eye[0] = self.CalMid(right_eye[0], right_eye[1])
            self.CalRPupol(right_eye[0], right_eye[1])
        except Exception as e:
            print(e)

    def CalLPupil(self, circle_center, circle_peripheral):
        r = round(math.hypot(circle_center[0] - circle_peripheral[0], circle_center[1] - circle_peripheral[1]))
        radians = (math.pi / 180) * round(360 / 19)
        new_points = []
        for i in range(19):
            if i < 5:
                x = circle_center[0] + r * math.sin(radians * i)
                y = circle_center[1] + r * math.cos(radians * i)
                shape = {
                    "label": "{}".format(4 - i),
                    "points": [[x, y]],
                    "group_id": "eyeballContour",
                    "shape_type": "point",
                    "flags": {}
                }
                new_points.append(shape)
            else:
                x = circle_center[0] + r * math.sin(radians * i)
                y = circle_center[1] + r * math.cos(radians * i)
                shape = {
                    "label": "{}".format(23 - i),
                    "points": [[x, y]],
                    "group_id": "eyeballContour",
                    "shape_type": "point",
                    "flags": {}
                }
                new_points.append(shape)
        self.newShapes = self.newShapes + new_points

    def CalRPupol(self, circle_center, circle_peripheral):
        r = round(math.hypot(circle_center[0] - circle_peripheral[0], circle_center[1] - circle_peripheral[1]))
        radians = (math.pi / 180) * round(360 / 19)
        new_points = []
        for i in range(19):
            if i < 15:
                x = circle_center[0] + r * math.sin(radians * i)
                y = circle_center[1] + r * math.cos(radians * i)
                shape = {
                    "label": "{}".format(i + 23),
                    "points": [[x, y]],
                    "group_id": "eyeballContour",
                    "shape_type": "point",
                    "flags": {}
                }
                new_points.append(shape)
            else:
                x = circle_center[0] + r * math.sin(radians * i)
                y = circle_center[1] + r * math.cos(radians * i)
                shape = {
                    "label": "{}".format(i + 4),
                    "points": [[x, y]],
                    "group_id": "eyeballContour",
                    "shape_type": "point",
                    "flags": {}
                }
                new_points.append(shape)
        self.newShapes = self.newShapes + new_points

    def Cal(self, points, intervalNum):
        points = [points[0]] + list(sorted(points[1:-1], key=lambda x: x[0])) + [points[-1]]

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


if __name__ == '__main__':
    import json
    path = r'E:\数据测试\280手动打点\新建文件夹\66561.json'
    with open(path, 'r', encoding='utf-8') as f:
        content = json.loads(f.read())
    shapes = content["shapes"]

    c = CalAuto()
    c.shapes = shapes
    newShapes = c.deal()
    content["shapes"] = newShapes
    with open(path.replace('.json', '_1.json'), 'w', encoding='utf-8') as f1:
        json.dump(content, f1, ensure_ascii=False, indent=4)