import os, shutil
import csv
import cv2
from lxml.etree import Element, SubElement, tostring


target = "F:/VOC2007/"
image_set = "E:/cardata/train_1w/"
label_set = "E:/cardata/train_1w.csv"
val_set = "E:/cardata/train_b/"
vlabel_set = "F:/cardata/val_txt"
size = (1069, 500)


def create_xml(filename, width, height, depth, object,
               database='cardata', annotation='new', folder='VOC2007'):
    node_root = Element('annotation')

    node_folder = SubElement(node_root, 'folder')
    node_folder.text = folder

    node_filename = SubElement(node_root, 'filename')
    node_filename.text = filename

    node_source = SubElement(node_root, 'source')
    node_database = SubElement(node_source, 'database')
    node_database.text = database
    node_annotation = SubElement(node_source, 'annotation')
    node_annotation.text = annotation

    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = width
    node_height = SubElement(node_size, 'height')
    node_height.text = height
    node_depth = SubElement(node_size, 'depth')
    node_depth.text = depth

    if object is None: return node_root

    for i, obj in enumerate(object):
        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = obj['name']

        node_pose = SubElement(node_object, 'pose')
        node_pose.text = 'Unspecified'

        node_truncated = SubElement(node_object, 'truncated')
        node_truncated.text = obj['truncated']

        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = obj['difficult']

        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = obj['xmin']
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = obj['ymin']
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = obj['xmax']
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = obj['ymax']

    return node_root

def read_data(file_path, sw, sh):
    with open(file_path) as f:
        object_list = []
        lines = f.readlines()
        num = lines[0].strip('\n')
        for i in range(int(num)):
            # from wmin, hmin, wmax, hmax
            # to wmin, hmin, wmax, hmax
            object = {}
            object['name'] = lines[1 + i * 5].strip('\n')
            if object['name'] != 'car':
                print(lines[1 + i * 5])
            object['truncated'] = '0'
            object['difficult'] = '0'
            xmin = int(float(lines[2 + i * 5]) * sw)
            ymin = int(float(lines[3 + i * 5]) * sh)
            xmax = int(float(lines[4 + i * 5]) * sw)
            ymax = int(float(lines[5 + i * 5]) * sh)
            xmin = max(xmin, 0)
            ymin = max(ymin, 0)
            xmax = min(xmax, size[0])
            ymax = min(ymax, size[1])
            object['xmin'] = str(xmin)
            object['ymin'] = str(ymin)
            object['xmax'] = str(xmax)
            object['ymax'] = str(ymax)
            object_list.append(object)
    return object_list

def process_result(results, sw, sh):
    object_list = []
    objects = result.split(';')
    for object in objects:
        data = object.split('_')
        if len(data) != 4: continue
        object = {}
        object['name'] = 'car'
        object['truncated'] = '0'
        object['difficult'] = '0'
        xmin = int(float(data[0]) * sw)
        ymin = int(float(data[1]) * sh)
        xmax = int(float(data[2]) * sw + float(data[0]) * sw)
        ymax = int(float(data[3]) * sh + float(data[1]) * sh)
        xmin = max(xmin, 0)
        ymin = max(ymin, 0)
        xmax = min(xmax, size[0])
        ymax = min(ymax, size[1])
        object['xmin'] = str(xmin)
        object['ymin'] = str(ymin)
        object['xmax'] = str(xmax)
        object['ymax'] = str(ymax)
        object_list.append(object)
    return object_list

image_target = os.path.join(target, "JPEGImages/")
label_target = os.path.join(target, "Annotations/")
train_file = os.path.join(target, "ImageSets/Main/train.txt")
test_file = os.path.join(target, "ImageSets/Main/test.txt")
count = 1

train = open(train_file, "w")
test = open(test_file, "w")

csv_file = csv.reader(open(label_set, 'r'))
for lines in csv_file:
    sw = 1
    sh = 1
    name = str(count).zfill(6)

    # Read images
    file = lines[0]
    result = lines[1]
    if file == 'name': continue
    if result == '': continue
    image = cv2.imread(os.path.join(image_set, file[:-4] + '.jpg'))
    height, width, depth = image.shape
    if height != size[1] or width != size[0]:
        image = cv2.resize(image, size)
        sw = size[0] / width
        sh = size[1] / height

    # Read label
    object_list = process_result(result, sw, sh)
    # Skip if no object
    # if len(object_list) == 0: continue

    # Process if have objects
    train.write("%s\n" % name) # write labels
    cv2.imwrite(os.path.join(image_target, name + '.jpg'), image) # copy image
    # Create labels
    node = create_xml(name + '.jpg', str(size[0]), str(size[1]), str(depth), object_list)
    xml = tostring(node, pretty_print=True)
    writer = open(label_target + '/' + name + '.xml', 'wb')
    writer.write(xml)
    writer.close()

    print(count)
    count += 1

for file in os.listdir(vlabel_set):
    sw = 1
    sh = 1
    name = str(count).zfill(6)

    # Read images
    image = cv2.imread(os.path.join(val_set, file[:-4] + '.jpg'))
    height, width, depth = image.shape
    if height != size[1] or width != size[0]:
        image = cv2.resize(image, size)
        sw = size[0] / width
        sh = size[1] / height

    # Read label
    object_list = read_data(os.path.join(vlabel_set, file), sw, sh)
    # Skip if no object
    if len(object_list) == 0: continue

    # Process if have objects
    test.write("%s\n" % name) # write labels
    cv2.imwrite(os.path.join(image_target, name + '.jpg'), image) # copy image
    # Create labels
    node = create_xml(name + '.jpg', str(size[0]), str(size[1]), str(depth), object_list)
    xml = tostring(node, pretty_print=True)
    writer = open(label_target + '/' + name + '.xml', 'wb')
    writer.write(xml)
    writer.close()

    print(count)
    count += 1

train.close()
test.close()
