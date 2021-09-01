import json


label_name = {}


def get_num(section):
    if '-' in section:
        if int(section.split('-')[0]) < int(section.split('-')[1]):
            sec = [int(x) for x in range(int(section.split('-')[0]), int(section.split('-')[1])+1)]
        else:
            sec = [int(x) for x in range(int(section.split('-')[1]), int(section.split('-')[0]) + 1)][::-1]
        return sec
    else:
        sec = [int(x) for x in section.split(',') if x.isdigit()]
        return sec


def point_comparison(point, occlusion_list):
    for occlusion in occlusion_list:
        x = [occlusion[0][0], occlusion[1][0]]
        y = [occlusion[0][1], occlusion[1][1]]
        if min(x) < point[0] < max(x) and min(y) < point[1] < max(y):
            return 1
    return None


def get_newShape(shapes, sec, occlusion_list):
    new_shapes = []
    for num in range(len(sec)):
        shape = {
            "label": str(sec[num]),
            "points": [shapes[num]],
            "group_id": point_comparison(shapes[num], occlusion_list),
            "shape_type": "point",
        }
        new_shapes.append(shape)
    return new_shapes


with open('config.txt', 'r', encoding='utf-8') as f:
    for lab in f.readlines()[4:]:
        if len(lab.split('#')) > 2:
            label = lab.split('#')[0]
            num = lab.split('#')[1]
            section = lab.split('#')[2].replace('\n', '')
            label_name[label] = [num, section]


path = r'E:\数据测试\232点测试数据\2M0A7004.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
shapes = data["shapes"]

occlusion_list = []
for shape in shapes:
    if shape["shape_type"] == "rectangle":
        occlusion_list.append(shape["points"])


new_shapes = []
label_list = []
new_points = {}
for i in label_name:
    sec = get_num(label_name[i][1])
    if int(label_name[i][0]) == len(sec):
        for shape in shapes:
            if shape["label"] == i:
                points = shape["points"]
                if shape["points"][0][0] > shape["points"][-1][0]:
                    points = points[::-1]
                new = get_newShape(points, sec, occlusion_list)
                if new:
                    for k in new:
                        if k["label"] not in new_points:
                            new_points[k["label"]] = [k["points"][0], k["group_id"]]
            if shape["shape_type"] == "point" and shape["label"] not in new_points:
                new_points[shape["label"]] = [shape["points"][0], shape["group_id"]]
                            # label_list.append(k["label"])
                            # new_shapes.append(k)
# print(new_points)
# print(len(new_points))
bbb = [x for x in new_points]
print(bbb)
for i in range(232):
    if str(i) not in bbb:
        print(i)
# data["shapes"] = new_shapes
# with open(path.replace('2M0A7004.json', '222.json'), 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)
# print(new_shapes)