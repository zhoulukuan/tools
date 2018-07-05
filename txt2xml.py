from lxml.etree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os, shutil
import cv2
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

def read_data(file_path):
    with open(file_path) as f:
        object_list = []
        lines = f.readlines()
        num = lines[0].strip('\n')
        for i in range(int(num)):
            # from wmin, hmin, wmax, hmax
            # to wmin, hmin, wmax, hmax
            object = {}
            object['name'] = lines[1 + i * 5].strip('\n')
            object['truncated'] = '0'
            object['difficult'] = '0'
            object['xmin'] = lines[2 + i * 5].strip('\n')
            object['ymin'] = lines[3 + i * 5].strip('\n')
            object['xmax'] = lines[4 + i * 5].strip('\n')
            object['ymax'] = lines[5 + i * 5].strip('\n')
            object_list.append(object)
    return object_list

data_path = '/home/lukuanzhou/Dataset/cardata/train_1w'
txt_path = '/home/lukuanzhou/Dataset/cardata/label_txt'
voc_path = '/home/lukuanzhou/Dataset/cardata/label_voc'

for file in os.listdir(data_path):
    if file[-4:] == '.txt':
        object_list = read_data(os.path.join(data_path, file))
        image = cv2.imread(os.path.join(data_path, file[:-4]+'.jpg'))
        height, width, depth = image.shape
        node = create_xml(file, str(width), str(height), str(depth), object_list)
        xml = tostring(node, pretty_print=True)

        writer = open(voc_path + '/' + file[:-4] + '.xml', 'wb')
        writer.write(xml)
        writer.close()

        # Move related files
        # shutil.move(
        #     os.path.join(data_path, file),
        #     os.path.join(txt_path, file)
        # )

