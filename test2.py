import json


path = r'E:\数据测试\新建文件夹 (9)\新建文件夹 (2)\2M0A7011.json'
with open(path, 'r', ) as f:
    data = json.loads(f.read())
shapes = data["shapes"]
print(shapes)
for shape in shapes:
    if 'visible' in shape:
        visible = []
    else:
        visible = None

print(visible)