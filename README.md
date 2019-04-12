
# PyTorch-Detectron for domain adaptation by self-training on hard examples

![intro](demo/intro_self-sup.png)


This codebase replicates results for pedestrian detection with domain shifts on the BDD100k dataset, following the CVPR 2019 paper [Automatic adaptation of object detectors to new domains using self-training](http://vis-www.cs.umass.edu/unsupVideo/docs/self-train_cvpr2019.pdf). We provide trained models, train and eval scripts as well as splits of the dataset for download. More details are available on the **[project page](http://vis-www.cs.umass.edu/unsupVideo/)**. 

This repository is heavily based off [A Pytorch Implementation of Detectron](https://github.com/roytseng-tw/Detectron.pytorch). We modify it for experiments on domain adaptation of face and pedestrian detectors. 

If you find this codebase useful, please consider citing:

```
@inproceedings{roychowdhury2019selftrain,
    Author = {Aruni RoyChowdhury and Prithvijit Chakrabarty  and Ashish Singh and SouYoung Jin and Huaizu Jiang and Liangliang Cao and Erik Learned-Miller},
    Title = {Automatic adaptation of object detectors to new domains using self-training},
    Booktitle = {IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
    Year = {2019}
}

```


## Getting Started
Clone the repo:

```
git clone https://github.com/AruniRC/Detectron-pytorch-video.git
```

### Requirements

Tested under python3.

- python packages
  - pytorch>=0.3.1
  - torchvision>=0.2.0
  - cython
  - matplotlib
  - numpy
  - scipy
  - opencv
  - pyyaml
  - packaging
  - [pycocotools](https://github.com/cocodataset/cocoapi)  — for COCO dataset, also available from pip.
  - tensorboardX  — for logging the losses in Tensorboard
- An NVIDAI GPU and CUDA 8.0 or higher. Some operations only have gpu implementation.
- **NOTICE**: different versions of Pytorch package have different memory usages.


## Installation
This walkthrough describes setting up this Detectron repo. The detailed instructions are in [INSTALL.md](INSTALL.md).



## Dataset
Create a data folder under the repo,

```
cd {repo_root}
mkdir data
```

### BDD-100k
Our pedestrian detection task uses both labeled and unlabeled data from the **Berkeley Deep Drive** [BDD-100k dataset](https://bdd-data.berkeley.edu/). Please register and download the dataset from their website. We use a symlink from our project root, `data/bdd100k` to link to the location of the downloaded dataset. The folder structure should be like this:

```
data/bdd100k/
    images/
        test/
        train/
        val/
    labels/
        train/
        val/
```

BDD-100k takes about 6.5 GB disk space. The 100k unlabeled videos take 234 GB space, but you do not need to download them, since we have already done the hard example mining on these and the extracted frames (+ pseudo-labels) are available for download.


### BDD Hard Examples
Mining the **hard positives** ("HPs") involve detecting pedestrians and tracklet formation on 100K videos. This was done on the UMass GPU Cluster and took about a week. We do not include this pipeline here (**yet**) -- the mined video frames and annotations are available for download as a gzipped tarball from [here](http://maxwell.cs.umass.edu/self-train/dataset/bdd_HP18k.tar.gz). **NOTE:** this is a large download (**23 GB**). *The data retains the permissions and licensing associated with the BDD-100K dataset (we make the video frames available here for ease of research).*

Now we create a symlink to the untarred BDD HPs from the project data folder, which should have the following structure: `data/bdd_peds_HP18k/*.jpg`. The image naming convention is `<video-name>_<frame-number>.jpg`.


### Annotation JSONs

All the annotations are assumed to be downloaded inside a folder `data/bdd_jsons` relative to the project root: `data/bdd_jsons/*.json`. We use symlinks here as well, in case the JSONs are kept in some other location.


| Data Split  | JSON |  Dataset name |  Image Dir. |
| ------------- | ------------- | ------------- | ------------- |
| BDD-Source-Train | [bdd_peds_train.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_peds_train.json) | bdd_peds_train | data/bdd100k  |
| BDD-Source-Val | [bdd_peds_val.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_peds_val.json) | bdd_peds_val | data/bdd100k  |
| BDD-Target-Train | [bdd_peds_not_clear_any_daytime_train.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_peds_not_clear_any_daytime_train.json) | bdd_peds_not_clear_any_daytime_train | data/bdd100k  |
| BDD-Target-Val | [bdd_peds_not_clear_any_daytime_val.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_peds_not_clear_any_daytime_val.json) | bdd_peds_not_clear_any_daytime_val | data/bdd100k  |
| BDD-dets | [bdd_dets18k.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_dets18k.json) | DETS18k | data/bdd_peds_HP18k  |
| BDD-HP | [bdd_HP18k.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_HP18k.json) | HP18k | data/bdd_peds_HP18k  |
| BDD-score-remap | [bdd_HP18k_remap_hist.json](http://maxwell.cs.umass.edu/self-train/dataset/bdd_jsons/bdd_HP18k_remap_hist.json) | HP18k_remap_hist | data/bdd_peds_HP18k  |



## Models

Use the environment variable `CUDA_VISIBLE_DEVICES` to control which GPUs to use. All the training scripts are run with 4 GPUs. The trained model checkpoints can be downloaded from the links under the column **Model weights**. The eval scripts need to be modified to point to where the corresponding model checkpoints have been downloaded locally. The performance numbers shown are from *single* models (the same models available for download), while the tables in the paper show results averaged across 5 rounds of train/test.

| Method  | Model weights |  Config YAML |  Train script |  Eval script | AP, AR |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Baseline | [bdd_baseline](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_baseline/bdd_peds.pth)  | [cfg](configs/baselines/bdd100k.yaml)  |  [train](gypsum/scripts/train/bdd_scripts/bdd_baseline.sh)  |  [eval](gypsum/scripts/eval/bdd_scripts/baseline_source.sh)  |  15.21, 33.09  |
| Dets | [bdd_dets](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_dets/bdd_dets_model_step29999.pth)  | [cfg](configs/baselines/bdd_peds_dets_bs64_4gpu.yaml)  |  [train](gypsum/scripts/train/bdd_scripts/bdd_source_and_dets18k.sh)  |  [eval](gypsum/scripts/eval/bdd_scripts/bdd_dets_source.sh)  |  27.55, 56.90  |
| HP | [bdd_hp](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_HP/bdd_HP_model_step29999.pth)  | [cfg](configs/baselines/bdd_peds_dets_bs64_4gpu.yaml)  |  [train](gypsum/scripts/train/bdd_scripts/bdd_source_and_HP18k.sh)  |  [eval](gypsum/scripts/eval/bdd_scripts/bdd_hp_source.sh)  |  28.34, 58.04  |
| HP-constrained | [bdd_hp-cons](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_HP-cons/bdd_HP-cons_model_step29999.pth)  | [cfg](configs/baselines/bdd_distill100_track100.yaml)  |  [train](gypsum/scripts/train/bdd_scripts/bdd_source_and_HP18k_distill100_track100.sh)  |  [eval](gypsum/scripts/eval/bdd_scripts/bdd_hp_cons_source.sh)  |  **29.57**, **56.48**  |
| HP-score-remap | [bdd_score-remap](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_HP-score-remap/bdd_HP-score-remap_model_step29999.pth)  | [cfg](configs/baselines/bdd_distill100_track100.yaml)  |  [train](gypsum/scripts/train/bdd_scripts/bdd_source_and_HP18k_remap_hist.sh)  |  [eval](gypsum/scripts/eval/bdd_scripts/bdd_score_remap_source.sh)  |  28.11, 56.80  |
| DA-im | [bdd_da-im](http://maxwell.cs.umass.edu/self-train/models/bdd_ped_models/bdd_DA-im/bdd_DA-im_model_step29999.pth)  | [cfg](configs/baselines/bdd_domain_im.yaml)  |  [train](configs/baselines/bdd_domain_im.yaml)  |  [eval](gypsum/scripts/eval/bdd_scripts/bdd_domain_im_source.sh)  |  25.71, 56.29  |





## Inference demo

**TODO**

### Visualize pre-trained Detectron model on images

This can run a pretrained Detectron model trained on MS-COCO categories, downloaded from the official Detectron Model Zoo, on the sample images. Note the `load_detectron` option to the `infer_simple.py` script, because we are using a Detectron model, not a checkpoint.

```
python tools/infer_simple.py --dataset coco --cfg cfgs/baselines/e2e_mask_rcnn_R-50-C4.yml --load_detectron {path/to/your/checkpoint} --image_dir {dir/of/input/images}  --output_dir {dir/to/save/visualizations}
```
`--output_dir` defaults to `infer_outputs`.



## Training demo

**TODO**


