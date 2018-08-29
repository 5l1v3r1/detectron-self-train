from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import h5py
import json
import os
import scipy.misc
import sys
import re
import fnmatch
import datetime
from PIL import Image
import numpy as np


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)

this_dir = os.path.dirname(__file__)
add_path(this_dir)
# print(this_dir)
add_path(os.path.join(this_dir, '..', '..'))

import utils
import utils.boxes as bboxs_util
import utils.face_utils as face_util


# INFO = {
#     "description": "WIDER Face Dataset",
#     "url": "http://mmlab.ie.cuhk.edu.hk/projects/WIDERFace/",
#     "version": "0.1.0",
#     "year": 2018,
#     "contributor": "umass vision",
#     "date_created": datetime.datetime.utcnow().isoformat(' ')
# }

# LICENSES = [
#     {
#         "id": 1,
#         "name": "placeholder",
#         "url": "placeholder"
#     }
# ]

# CATEGORIES = [
#     {
#         'id': 1,
#         'name': 'face',
#         'supercategory': 'face',
#     },
# ]



def parse_args():
    parser = argparse.ArgumentParser(description='Convert dataset')
    parser.add_argument(
        '--dataset', help="wider", default='wider', type=str)
    parser.add_argument(
        '--outdir', help="output dir for json files", 
        default='', type=str)
    parser.add_argument(
        '--datadir', help="data dir for annotations to be converted",
        default='', type=str)
    parser.add_argument(
        '--imdir', help="root directory for loading dataset images",
        default='', type=str)
    parser.add_argument(
        '--annotfile', help="directly specify the annotations file",
        default='', type=str)
    # if len(sys.argv) == 1:
    #     parser.print_help()
    #     sys.exit(1)
    return parser.parse_args()



def convert_wider_annots(data_dir, out_dir, data_set='WIDER'):
    """Convert from WIDER FDDB-style format to COCO bounding box"""

    # http://cocodataset.org/#format-data: [x,w,width,height]
    json_name = 'wider_face_train_annot_coco_style.json'
    img_id = 0
    ann_id = 0
    cat_id = 1

    print('Starting %s' % data_set)
    ann_dict = {}
    categories = [{"id": 1, "name": 'face'}]
    images = []
    annotations = []
    ann_file = os.path.join(data_dir, 'wider_face_train_annot.txt')
    wider_annot_dict = face_util.parse_wider_gt(ann_file) # [im-file] = [[x,y,w,h], ...]

    for filename in wider_annot_dict.keys():
        if len(images) % 50 == 0:
            print("Processed %s images, %s annotations" % (
                len(images), len(annotations)))

        image = {}
        image['id'] = img_id
        img_id += 1
        im = Image.open(os.path.join(data_dir, filename))
        image['width'] = im.height
        image['height'] = im.width
        image['file_name'] = filename
        images.append(image)

        for gt_bbox in wider_annot_dict[filename]:
            ann = {}
            ann['id'] = ann_id
            ann_id += 1
            ann['image_id'] = image['id']
            ann['segmentation'] = []
            ann['category_id'] = cat_id # 1:"face" for WIDER
            ann['iscrowd'] = 0
            ann['area'] = gt_bbox[2] * gt_bbox[3]
            ann['bbox'] = gt_bbox 
            annotations.append(ann)

    ann_dict['images'] = images
    ann_dict['categories'] = categories
    ann_dict['annotations'] = annotations
    print("Num categories: %s" % len(categories))
    print("Num images: %s" % len(images))
    print("Num annotations: %s" % len(annotations))
    with open(os.path.join(out_dir, json_name), 'w', encoding='utf8') as outfile:
        outfile.write(json.dumps(ann_dict))



def convert_cs6_annots(ann_file, im_dir, out_dir, data_set='CS6-subset'):
    """Convert from FDDB-style detections format to COCO annotations"""

    if data_set=='CS6-subset':
        json_name = 'cs6-subset_face_train_annot_coco_style.json'
    elif data_set=='CS6-subset-score':
        # include "scores" as soft-labels
        json_name = 'cs6-subset_face_train_score-annot_coco_style.json'
    elif data_set=='CS6-subset-gt':
        json_name = 'cs6-subset-gt_face_train_annot_coco_style.json'
    elif data_set=='CS6-train-gt':
        json_name = 'cs6-train-gt_face_train_annot_coco_style.json'
    else:
        raise NotImplementedError


    img_id = 0
    ann_id = 0
    cat_id = 1

    print('Starting %s' % data_set)
    ann_dict = {}
    categories = [{"id": 1, "name": 'face'}]
    images = []
    annotations = []
    
    wider_annot_dict = face_util.parse_wider_gt(ann_file) # [im-file] = [[x,y,w,h], ...]    

    for filename in wider_annot_dict.keys():
        if len(images) % 50 == 0:
            print("Processed %s images, %s annotations" % (
                len(images), len(annotations)))

        image = {}
        image['id'] = img_id
        img_id += 1
        im = Image.open(os.path.join(im_dir, filename))
        image['width'] = im.height
        image['height'] = im.width
        image['file_name'] = filename
        images.append(image)

        for gt_bbox in wider_annot_dict[filename]:
            ann = {}
            ann['id'] = ann_id
            ann_id += 1
            ann['image_id'] = image['id']
            ann['segmentation'] = []
            ann['category_id'] = cat_id # 1:"face" for WIDER
            ann['iscrowd'] = 0
            ann['area'] = gt_bbox[2] * gt_bbox[3]
            ann['bbox'] = gt_bbox[:4]
            if 'score' in data_set:
                ann['score'] = gt_bbox[4] # for soft-label distillation
            annotations.append(ann)

    ann_dict['images'] = images
    ann_dict['categories'] = categories
    ann_dict['annotations'] = annotations
    print("Num categories: %s" % len(categories))
    print("Num images: %s" % len(images))
    print("Num annotations: %s" % len(annotations))
    with open(os.path.join(out_dir, json_name), 'w', encoding='utf8') as outfile:
        outfile.write(json.dumps(ann_dict))



if __name__ == '__main__':
    args = parse_args()
    
    if args.dataset == "wider":
        convert_wider_annots(args.datadir, args.outdir)
    elif args.dataset == "cs6-subset":
        convert_cs6_annots(args.annotfile, args.imdir, 
                           args.outdir, data_set='CS6-subset')
    elif args.dataset == "cs6-subset-score":
        convert_cs6_annots(args.annotfile, args.imdir, 
                           args.outdir, data_set='CS6-subset-score')
    elif args.dataset == "cs6-subset-gt":
        convert_cs6_annots(args.annotfile, args.imdir, 
                           args.outdir, data_set='CS6-subset-gt')
    elif args.dataset == "cs6-train-gt":
        # set defaults if inputs args are empty
        if not args.annotfile:
            args.annotfile = 'data/CS6_annot/annot-format-GT/cs6_gt_annot_train.txt'
        if not args.imdir:
            args.imdir = 'data/CS6_annot'
        if not args.outdir:
            args.outdir = 'data/CS6_annot'
        convert_cs6_annots(args.annotfile, args.imdir, 
                           args.outdir, data_set='CS6-train-gt')
    else:
        print("Dataset not supported: %s" % args.dataset)
