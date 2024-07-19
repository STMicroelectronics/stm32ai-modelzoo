# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import shutil
import os
import argparse
import numpy as np

from tqdm             import tqdm
from pycocotools.coco import COCO


def yolo_box_to_txt(box,f_name):

    result = ""

    for b in box:
        result+= str(b)+' '
    result = result[:-1]
    result+='\n'

    with open(f_name, "a") as file:
        file.write(result)
        file.close()


parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, default='./',help='path to COCO dataset val or train')
parser.add_argument('--pose', type=str, default='single',help='single or multi pose')
parser.add_argument('--keypoints', type=str, default='17',help='17 or 13 keypoints')
parser.add_argument('--outputdir', type=str, default='./output',help='output directory')
params = parser.parse_args()

KPTS        = int(params.keypoints)
COCO_origin = params.path
COCO_year   = '2017'


for COCO_type in ['val','train']:

    print('[INFO] Creation of the ' + COCO_type + ' dataset')

    COCO_destination = os.path.join(params.outputdir,params.pose,params.keypoints+'kpts',COCO_type)

    empty = True
    print('[INFO] Verifying destination folder ...')
    if not os.path.exists(params.outputdir):
        os.mkdir(params.outputdir)
    if not os.path.exists(os.path.join(params.outputdir,params.pose)):
        os.mkdir(os.path.join(params.outputdir,params.pose))
    if not os.path.exists(os.path.join(params.outputdir,params.pose,params.keypoints+'kpts')):
        os.mkdir(os.path.join(params.outputdir,params.pose,params.keypoints+'kpts'))
    if not os.path.exists(COCO_destination):
        os.mkdir(COCO_destination)
    else:
        print('[INFO] -> Destination folder already exists')
        empty = False

    if empty:
        
        annFile = os.path.join(COCO_origin,'annotations','person_keypoints_{}.json'.format(COCO_type+COCO_year))

        # initialize COCO api for instance annotations
        coco = COCO(annFile)

        # get all images containing 'person'
        catIds    = coco.getCatIds(catNms=['person'])
        imgIds    = coco.getImgIds(catIds=catIds)
        imgsInfos = coco.loadImgs(imgIds)

        for i,inf in enumerate(tqdm(imgsInfos)):

            imH, imW = inf['height'], inf['width']
            annIds = coco.getAnnIds(imgIds=inf['id'], catIds=catIds, iscrowd=None)
            anns   = coco.loadAnns(annIds)

            text_files = []
            keep_image = True
            nbr_anns = len(anns)
            acc_nz = 0

            if (params.pose == 'single' and nbr_anns == 1) or (params.pose == 'multi' and nbr_anns >= 1) :
                for bb in anns:
                    # delete all annotations that are crowds
                    if bb.get("iscrowd", False):
                        continue
                    # The COCO box format is [top left x, top left y, width, height]
                    bbox = np.array(bb['bbox'],     dtype=np.float32)
                    kpts = np.array(bb['keypoints'],dtype=np.float32)

                    W,H = bbox[2],bbox[3]

                    # delete all annotations with bbox size at 0
                    if W <= 0 or H <= 0:  # if w <= 0 and h <= 0
                        continue

                    kpts[0::3] /= imW
                    kpts[1::3] /= imH

                    kpts[2::3] = (kpts[2::3]>=1)*1

                    bbox[0] += bbox[2]/2 # center the x coordinates
                    bbox[1] += bbox[3]/2 # center the y coordinates

                    bbox[0] /= imW
                    bbox[1] /= imH
                    bbox[2] /= imW
                    bbox[3] /= imH

                    if KPTS == 13:
                        head_2 = (np.sum(kpts[2::3][:5])>=1)*1.
                        head_0 = head_2*np.sum(kpts[0::3][:5] * kpts[2::3][:5]) / (np.sum(kpts[2::3][:5])+1e-30)
                        head_1 = head_2*np.sum(kpts[1::3][:5] * kpts[2::3][:5]) / (np.sum(kpts[2::3][:5])+1e-30)
                        kpts = kpts[3*5:]
                        kpts = np.concatenate([[head_0,head_1,head_2],kpts])

                    annots = np.concatenate([[0],bbox,kpts])

                    txt_file = os.path.join(COCO_destination,inf['file_name'][:-4] + '.txt')

                    acc_nz += np.count_nonzero(kpts[2::3])

                    text_files.append([annots,txt_file])

            # if all of keypoint are missing in the detection, delete the image
            if acc_nz < 1:
                keep_image = False
                
            if keep_image :

                image_src  = os.path.join(COCO_origin,COCO_type+COCO_year,inf['file_name'])
                image_dest = os.path.join(COCO_destination,inf['file_name'])

                for t in text_files:
                    yolo_box_to_txt(t[0],t[1])

                shutil.copyfile(image_src, image_dest)