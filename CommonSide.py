import os
import json

from labelme import utils
import PIL
import imgviz

import os.path as osp
from PIL import Image
import cv2
import numpy as np


class GetCommonSide:

    def __init__(self):
        self.face = self.hair = self.left_ear = self.right_ear = self.neck = []

    def comparisonPoints(self, point, points_list):
        for p in points_list:
            if point != p:
                if p[0]-5 < point[0] < p[0]+5:
                    if p[1]-5 < point[1] < p[1]+5:
                        return p
        return None

    def readFile(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.loads(f.read())

        shapes = content["shapes"]
        for shape in shapes:
            if shape["label"] == '1':
                self.face = shape["points"]
            if shape["label"] == '10':
                self.hair = shape["points"]
            if shape["label"] == '11':
                self.left_ear = shape["points"]
            if shape["label"] == '12':
                self.right_ear = shape["points"]
            if shape["label"] == '15':
                self.neck = shape["points"]

        if self.face:
            if self.hair:
                hair1 = self.comparisonPoints(self.hair[0], self.face)
                hair2 = self.comparisonPoints(self.hair[1], self.face)
                if hair1 and hair2:
                    self.hair[:2] = list(reversed(self.face[self.face.index(hair2):self.face.index(hair1)]))

            if self.left_ear:
                ear1 = self.comparisonPoints(self.left_ear[0], self.face)
                ear2 = self.comparisonPoints(self.left_ear[-1], self.face)
                if ear1 and ear2:
                    self.left_ear[0] = ear1
                    self.left_ear[-1] = ear2
                    self.left_ear = self.left_ear+list(reversed(self.face[self.face.index(ear1):self.face.index(ear2)]))

            if self.right_ear:
                ear1 = self.comparisonPoints(self.right_ear[0], self.face)
                ear2 = self.comparisonPoints(self.right_ear[-1], self.face)
                if ear1 and ear2:
                    self.right_ear[0] = ear1
                    self.right_ear[-1] = ear2
                    self.right_ear = self.right_ear+self.face[self.face.index(ear2)+1:self.face.index(ear1)]

            if self.neck:
                neck1 = self.comparisonPoints(self.neck[0], self.face)
                neck2 = self.comparisonPoints(self.neck[-1], self.face)
                if neck1 and neck2:
                    self.neck[0] = neck1
                    self.neck[-1] = neck2
                    self.neck = self.neck + list(reversed(self.face[0:self.face.index(neck2)])) + \
                                list(reversed(self.face[self.face.index(neck1):]))

        for shape in shapes:
            if shape["label"] == '1':
                shape["points"] = self.face
            if shape["label"] == '10':
                shape["points"] = self.hair
            if shape["label"] == '11':
                shape["points"] = self.left_ear
            if shape["label"] == '12':
                shape["points"] = self.right_ear
            if shape["label"] == '15':
                shape["points"] = self.neck

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

        self.generateMask(json_file)

    def generateMask(self, json_file):
        try:
            data = json.load(open(json_file))
            img = utils.img_b64_to_arr(data['imageData'])

            lbl, lbl_names = utils.labelme_shapes_to_label(img.shape, data['shapes'])
            # 加区域显示
            captions = ['%d: %s' % (l, name) for l, name in enumerate(lbl_names)]
            lbl_viz = imgviz.label2rgb(
                label=lbl, img=imgviz.asgray(img),
                # label_names=captions,
                # loc='rb'
            )
            save_file_name = osp.splitext(osp.basename(json_file))[0]
            out_dir = osp.join(osp.dirname(json_file), 'mask')
            out_dir1 = osp.join(out_dir, save_file_name)
            if not osp.exists(out_dir1):
                os.makedirs(out_dir1)

            image1 = out_dir1 + '\\' + save_file_name + '.png'
            image2 = osp.join(out_dir1 + '\\' + save_file_name + '_mask.png')
            image3 = out_dir1 + '\\' + save_file_name + '_label.png'

            PIL.Image.fromarray(img).save(image1)
            utils.lblsave(image2, lbl)
            PIL.Image.fromarray(lbl_viz).save(image3)

            self.comparePictures(image1, image2, image3)

        except Exception as e:
            print(e)

    def comparePictures(self, image1, image2, image3):
        img1 = cv2.imread(image1)
        img2 = cv2.imread(image2)
        img3 = cv2.imread(image3)

        img1 = cv2.resize(img1, (500, 500))
        img2 = cv2.resize(img2, (500, 500))
        img3 = cv2.resize(img3, (500, 500))

        hmerge = np.hstack((img3, img2, img1))
        cv2.imshow('compare', hmerge)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# if __name__ == '__main__':
#     gc = GetCommonSide()
#     # path = r'E:\数据测试\语义分割\4.json'
#     path = r'E:\数据测试\语义分割'
#     for file in [x for x in os.listdir(path) if x.endswith('.json')]:
#         path1 = os.path.join(path, file)
#         gc.readFile(path1)





