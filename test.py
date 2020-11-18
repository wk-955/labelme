import json


def CalPoint(line1, line2):
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


path = r'E:\数据测试\280点'
with open(path + '\\' + '20330.json', 'r', encoding='utf-8') as f:
    content = json.loads(f.read())
shapes = content["shapes"]
new_shapes = []
for shape in shapes:
    if shape["group_id"] == "stMobile106" and shape["label"] in ['53', '54', '57', '56']:
        new_shapes.append(shape["points"][0])
print(new_shapes)
line1 = new_shapes[0] + new_shapes[2]
line2 = new_shapes[1] + new_shapes[3]
print(line1)
print(line2)
shapes[74]["points"] = [CalPoint(line1, line2)]
content["shapes"] = shapes
with open(path + '\\' + '20330.json', 'w', encoding='utf-8') as f:
    json.dump(content, f, ensure_ascii=False, indent=4)






