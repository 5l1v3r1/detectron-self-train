#!/usr/bin/env bash
#SBATCH --job-name=cs6-easy-det
#SBATCH -o gypsum/logs/%j_train_cs6-easy-det.txt 
#SBATCH -e gypsum/errs/%j_train_cs6-easy-det.txt
#SBATCH -p 1080ti-long
#SBATCH --gres=gpu:8
#SBATCH --mem=200000
##SBATCH --cpus-per-task=4
##SBATCH --mem-per-cpu=4096



# starts from WIDER pre-trained model
# trial run: just using CS6 data (imdb merging not done)


python tools/train_net_step.py \
    --dataset cs6-train-easy-det \
    --cfg configs/cs6/e2e_faster_rcnn_R-50-C4_1x_8gpu_50k.yaml  \
    --load_ckpt Outputs/e2e_faster_rcnn_R-50-C4_1x/Jul30-15-51-27_node097_step/ckpt/model_step79999.pth \
    --use_tfboard

