import os
import os.path as osp
import json


def rename(path):
    images = [x for x in os.listdir(path) if osp.splitext(x)[1].lower() in ['.jpg', '.png', '.jpeg']]
    count = 0
    for image in images:
        os.rename(osp.join(path, image),
                  osp.join(path, 'video-%s.jpg' % str(count)))
        os.rename(osp.join(path, osp.splitext(image)[0] + '.json'),
                  osp.join(path, 'video-%s.json' % str(count)))
        count += 1


def read_data(path):
    images = [x for x in os.listdir(path) if osp.splitext(x)[1].lower() in ['.jpg', '.png', '.jpeg']]
    for image in images[:1]:
        with open(osp.join(path, osp.splitext(image)[0] + '.json'), 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        head = {
            "label": "head",
            "points": [shapes[1]["points"][0], shapes[2]["points"][0], shapes[3]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }
        face = {
            "label": "face",
            "points": [shapes[4]["points"][0], shapes[5]["points"][0], shapes[6]["points"][0], shapes[7]["points"][0],
                      shapes[8]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }
        left_hand = {
            "label": "left_hand",
            "points": [shapes[9]["points"][0], shapes[10]["points"][0], shapes[12]["points"][0], shapes[14]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }
        right_hand = {
            "label": "right_hand",
            "points": [shapes[11]["points"][0], shapes[13]["points"][0], shapes[15]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }
        left_foot = {
            "label": "left_foot",
            "points": [shapes[22]["points"][0], shapes[16]["points"][0], shapes[18]["points"][0], shapes[20]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }
        right_foot = {
            "label": "right_foot",
            "points": [shapes[17]["points"][0], shapes[19]["points"][0], shapes[21]["points"][0]],
            "group_id": 0,
            "shape_type": "linestrip",
            "flags": {}
        }

        new_shapes = [
            head,
            face,
            left_hand,
            right_hand,
            left_foot,
            right_foot,
            shapes[0]
        ]

        content["shapes"] = new_shapes
        with open(osp.join(path, osp.splitext(image)[0] + '.json'), 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

        # for shape in shapes:
        #     print(shape)
        # for shape in shapes:
        #     if shape["label"] in ['0', '1', '2']:
        #         head.append(shape["points"][0])
        #     elif shape["label"] in ['3', '4', '5', '6', '7']:
        #         face.append(shape["points"][0])
        #     elif shape["label"] in ['8', '9', '11', '13']:
        #         left_hand.append(shape["points"][0])
        #     elif shape["label"] in ['10', '12', '14']:
        #         right_hand.append(shape["points"][0])
        #     elif shape["label"] in ['15', '17', '19']:
        #         left_foot.append(shape["points"][0])
        #     elif shape["label"] in ['16', '18', '20']:
        #         right_foot.append(shape["points"][0])


if __name__ == '__main__':
    path = r'E:\数据测试\22点数据'
    # rename(path)
    read_data(path)