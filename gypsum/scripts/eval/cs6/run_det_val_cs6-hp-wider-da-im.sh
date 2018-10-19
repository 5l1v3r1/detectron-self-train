#!/usr/bin/env bash


## --- CS6 + WIDER Joint training [distill branch] ---
##  domain-adaptation expts 
DET_NAME=frcnn-R-50-C4-1x
TRAIN_IMDB=CS6-train-HP+WIDER-da-im_10k
CFG_PATH=configs/cs6/e2e_faster_rcnn_R-50-C4_1x_domain_im.yaml
WT_PATH=Outputs/e2e_faster_rcnn_R-50-C4_1x_domain_im/Oct06-23-57-55_node119_step/ckpt/model_step9999.pth


CONF_THRESH=0.1
OUT_DIR="Outputs/evaluations/"${DET_NAME}"/cs6/train-"${TRAIN_IMDB}"_val-easy_conf-"${CONF_THRESH}



###     Run detector on all videos listed in "val easy" split of CS6
for VIDEO in `cat data/CS6/list_video_val_easy.txt`
do
    echo $VIDEO

    sbatch gypsum/scripts/eval/cs6/run_detector_full_video_titanx.sbatch \
        ${VIDEO} \
        ${CFG_PATH} \
        ${WT_PATH} \
        ${OUT_DIR} \
        ${CONF_THRESH}

    # sbatch gypsum/scripts/eval/cs6/run_det_video.sbatch \
    #     $VIDEO \
    #     ${DET_NAME} \
    #     ${OUT_DIR} \
    #     ${CONF_THRESH}

done
