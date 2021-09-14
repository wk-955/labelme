import os
import json
import shutil
import os.path as osp


def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data
    except Exception as e:
        print(e)
        print('该json格式有问题，请检查: ', path)
        return None


def deal_data(path):
    dirs = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
    if dirs:
        for d in dirs:
            new_path = os.path.join(path, d)
            convert(new_path)
    else:
        convert(path)


def convert(path):
    images = [x for x in os.listdir(path) if x.endswith('.jpg')]
    images = sorted(images, key=lambda x: int(x.split('_')[-1].replace('.jpg', '')))
    section_start = []
    section_end = []
    start = ['walk_s', 'run_s', 'jump_s', 'clap_s']
    end = ['walk_e', 'run_e', 'jump_e', 'clap_e']
    for image in images:
        if image.replace('.jpg', '.json') in os.listdir(path):
            data = read_json(os.path.join(path, image.replace('.jpg', '.json')))
            shapes = data["shapes"]
            if shapes:
                for shape in shapes:
                    if shape["label"] in start:
                        section_start.append(image.split('_')[-1].replace('.jpg', ''))
                    if shape["label"] in end:
                        section_end.append(image.split('_')[-1].replace('.jpg', ''))
    if len(section_start) == len(section_end):
        need_images = []
        section = list(zip(section_start, section_end))
        for sec in section:
            for num in range(int(sec[0]), int(sec[1])+1):
                need_images.append(osp.basename(path) + '_{}.jpg'.format(str(num)))
        move_file(path, list(set(need_images)))
        new_path = osp.join(path, '已标注图片')
        if osp.exists(new_path):
            generate_data(new_path)
    else:
        print('{}区间不完整，请检查'.format(path))


def move_file(path, need_images):
    for file in os.listdir(path):
        if file.endswith('.jpg'):
            if file in need_images:
                save = os.path.join(path, '已标注图片')
                if not os.path.exists(save):
                    os.mkdir(save)
                shutil.move(osp.join(path, file),
                            osp.join(save, file))
            else:
                save = os.path.join(path, '未标注图片')
                if not os.path.exists(save):
                    os.mkdir(save)
                shutil.move(osp.join(path, file),
                            osp.join(save, file))
        elif file.endswith('.json'):
            data = read_json(os.path.join(path, file))
            if data["shapes"]:
                save = os.path.join(path, '已标注图片')
                if not os.path.exists(save):
                    os.mkdir(save)
                shutil.move(osp.join(path, file),
                            osp.join(save, file))
            else:
                os.remove(osp.join(path, file))


def generate_data(path):
    images = [x for x in os.listdir(path) if x.endswith('.jpg')]
    images = sorted(images, key=lambda x: int(x.split('_')[-1].replace('.jpg', '')))
    for image in images:
        if image.replace('.jpg', '.json') in os.listdir(path):
            data = read_json(os.path.join(path, image.replace('.jpg', '.json')))
            shapes = data["shapes"]
            for shape in shapes:
                shape["label"] = shape["label"].replace('_s', '').replace('_e', '')
            width = data["imageHeight"]
            height = data["imageHeight"]
        else:
            file = {
                "version": "4.5.6",
                "flags": {},
                "shapes": shapes,
                "imagePath": image,
                "imageData": None,
                "imageHeight": width,
                "imageWidth": height
            }
            with open(os.path.join(path, image.replace('.jpg', '.json')), 'w', encoding='utf-8') as f:
                json.dump(file, f, ensure_ascii=False, indent=4)


def remove_json(path, number):
    if '-' in number:
        num = [x for x in range(int(number.split('-')[0]), int(number.split('-')[1])+1)]
    else:
        num = [x for x in number.split(',') if x]
    if num:
        json_files = [x for x in os.listdir(path) if x.endswith('.json')]
        for j in json_files:
            if j.split('_')[-1].replace('.json', '') in num:
                os.remove(osp.join(path, j))


if __name__ == '__main__':
    while True:
        fun = input('输入功能：0、退出  1、检测及数据生成  2、批量删除数据 \n:')
        if fun == '0':
            break
        if fun == '1':
            path = input('输入标注完的数据路径： ')
            deal_data(path)
        if fun == '2':
            path = input('输入需要删除的路径： ')
            number = input('输入需要删除的帧数(区间则用-分割,非区间用英文的逗号(,)分割): ')
            remove_json(path, number)