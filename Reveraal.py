class Reversal:
    def __init__(self):
        self.shapes = []

    def head(self):
        if self.shapes:
            for shape in self.shapes:
                if shape["label"] == 'head':
                    head = shape["points"]
                    points = [head[0], head[2], head[1]]
                    shape["points"] = points

    def face(self):
        if self.shapes:
            for shape in self.shapes:
                if shape["label"] == 'face':
                    face = shape["points"]
                    points = [face[1], face[0], face[2], face[4], face[3]]
                    shape["points"] = points

    def hand(self):
        if self.shapes:
            for shape in self.shapes:
                if shape["label"] == 'left_hand':
                    left = shape["points"]
                elif shape["label"] == 'right_hand':
                    right = shape["points"]
            for shape in self.shapes:
                if shape["label"] == 'left_hand':
                    points = [left[0]] + right
                    shape["points"] = points
                elif shape["label"] == 'right_hand':
                    points = left[1:]
                    shape["points"] = points

    def foot(self):
        if self.shapes:
            for shape in self.shapes:
                if shape["label"] == 'left_foot':
                    left = shape["points"]
                elif shape["label"] == 'right_foot':
                    right = shape["points"]
            for shape in self.shapes:
                if shape["label"] == 'left_foot':
                    points = [left[0]] + right
                    shape["points"] = points
                elif shape["label"] == 'right_foot':
                    points = left[1:]
                    shape["points"] = points
