from operator import itemgetter
from itertools import groupby
# import json


class Reversal:
    def __init__(self):
        self.shapes = []
        self.groupShapes = []

    def get_people(self):
        if self.shapes:
            count = 0
            for group_id, items in groupby(self.shapes, key=itemgetter("group_id")):
                self.groupShapes.append({count: list(items)})
                count += 1

    def head(self, num):
        if self.groupShapes:
            if num < len(self.groupShapes):
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'head':
                        head = shape["points"]
                        points = [head[0], head[2], head[1]]
                        self.shapes[self.shapes.index(shape)]["points"] = points

    def face(self, num):
        if self.groupShapes:
            if num < len(self.groupShapes):
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'face':
                        face = shape["points"]
                        points = [face[1], face[0], face[2], face[4], face[3]]
                        self.shapes[self.shapes.index(shape)]["points"] = points

    def hand(self, num):
        if self.groupShapes:
            if num < len(self.groupShapes):
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'leftHand':
                        left = shape["points"]
                    elif shape["label"] == 'rightHand':
                        right = shape["points"]
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'leftHand':
                        points = [left[0]] + right
                        self.shapes[self.shapes.index(shape)]["points"] = points
                    elif shape["label"] == 'rightHand':
                        points = left[1:]
                        self.shapes[self.shapes.index(shape)]["points"] = points

    def foot(self, num):
        if self.groupShapes:
            if num < len(self.groupShapes):
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'leftFoot':
                        left = shape["points"]
                    elif shape["label"] == 'rightFoot':
                        right = shape["points"]
                for shape in self.groupShapes[num][num]:
                    if shape["label"] == 'leftFoot':
                        points = [left[0]] + right
                        self.shapes[self.shapes.index(shape)]["points"] = points
                    elif shape["label"] == 'rightFoot':
                        points = left[1:]
                        self.shapes[self.shapes.index(shape)]["points"] = points


# if __name__ == '__main__':
#     path = r'E:\数据测试\22点数据\video1\000000000000.json'
#     with open(path, 'r', encoding='utf-8') as f:
#         content = json.loads(f.read())
#     shapes = content["shapes"]
#     c = Reversal()
#     c.shapes = shapes
#     c.get_people()
