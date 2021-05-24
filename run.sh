#!/bin/sh

source /Users/tylergreen/opt/anaconda3/etc/profile.d/conda.sh
conda deactivate 
conda activate base

cd /Users/tylergreen/PGALiveLeaderboard

python main.py
