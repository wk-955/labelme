import json
import cv2
import numpy as np
import os


class TO_IMG:
    def __init__(self):
        self.label_name = {}

    def get_num(self, section):
        if '-' in section:
            if int(section.split('-')[0]) < int(section.split('-')[1]):
                sec = [int(x) for x in range(int(section.split('-')[0]), int(section.split('-')[1])+1)]
            else:
                sec = [int(x) for x in range(int(section.split('-')[1]), int(section.split('-')[0]) + 1)][::-1]
            return sec
        else:
            sec = [int(x) for x in section.split(',') if x.isdigit()]
            return sec

    def point_comparison(self, point, occlusion_list):
        for occlusion in occlusion_list:
            x = [occlusion[0][0], occlusion[1][0]]
            y = [occlusion[0][1], occlusion[1][1]]
            if min(x) < point[0] < max(x) and min(y) < point[1] < max(y):
                return 1
        return None

    def get_newShape(self, shapes, sec, occlusion_list):
        new_shapes = []
        for num in range(len(sec)):
            shape = {
                "label": str(sec[num]),
                "points": [shapes[num]],
                "group_id": self.point_comparison(shapes[num], occlusion_list),
                "shape_type": "point",
            }
            new_shapes.append(shape)
        return new_shapes


    def crate_img(self, imagePath, points):
        img = cv2.imdecode(np.fromfile(imagePath, dtype=np.uint8), -1)

        for num in points:
            color = (0, 255, 0) if points[num][1] else (0, 0, 255)
            cv2.circle(img, (round(points[num][0][0]), round(points[num][0][1])), 5, (0, 0, 255), thickness=-1)
            cv2.putText(img, num, (round(points[num][0][0]), round(points[num][0][1])), cv2.FONT_HERSHEY_PLAIN,
                        3, color, thickness=4)
            # cv2.imshow("image", img)
        cv2.namedWindow(os.path.basename(imagePath), 0)
        cv2.imshow(os.path.basename(imagePath), img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def main(self, path):
        with open('config.txt', 'r', encoding='utf-8') as f:
            for lab in f.readlines()[5:]:
                if len(lab.split('#')) > 2:
                    label = lab.split('#')[0]
                    num = lab.split('#')[1]
                    section = lab.split('#')[2].replace('\n', '')
                    self.label_name[label] = [num, section]
        with open(path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        shapes = data["shapes"]
        img = data["imagePath"]
        occlusion_list = []
        for shape in shapes:
            if shape["shape_type"] == "rectangle":
                occlusion_list.append(shape["points"])

        new_points = {}
        for i in self.label_name:
            sec = self.get_num(self.label_name[i][1])
            if int(self.label_name[i][0]) == len(sec):
                for shape in shapes:
                    if shape["label"] == i:
                        points = shape["points"]
                        if shape["points"][0][0] > shape["points"][-1][0]:
                            points = points[::-1]
                        if len(points) == len(sec):
                            new = self.get_newShape(points, sec, occlusion_list)
                            for k in new:
                                if k["label"] not in new_points:
                                    new_points[k["label"]] = [k["points"][0], k["group_id"]]
                        else:
                            print('{}: {}部位不满足配置个数{}'.format(img, i, len(points)))
                    if shape["shape_type"] == "point" and shape["label"] not in new_points:
                        new_points[shape["label"]] = [shape["points"][0], self.point_comparison(shape["points"][0], occlusion_list)]

        print('{}点个数： '.format(img), len(new_points))
        self.crate_img(os.path.join(os.path.dirname(path), img), new_points)


if __name__ == '__main__':
    a = TO_IMG()
    path = r'E:\数据测试\232点线段测试\2M0A7004.json'
    a.main(path)
# data["shapes"] = new_shapes
# with open(path.replace('2M0A7004.json', '222.json'), 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)
# print(new_shapes)