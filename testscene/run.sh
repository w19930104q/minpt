#!/bin/sh
# Reproduce the BVH A/B comparison.
# Usage: sh testscene/run.sh [g++ path]
set -e
cd "$(dirname "$0")/.."
CXX=${1:-$HOME/bin/g++}

$CXX -O2 -fopenmp -std=c++17 -o minpt_bvh minpt_bvh.cpp
python3 testscene/gen_scene.py

mkdir -p testscene/results

# mode 0 = original BVH (control), mode 1 = reordered deterministic BVH
./minpt_bvh testscene/scene.obj "" "" testscene/results/out_old.pfm  16 8 0 64 64 0 1 2.8 0 0.9 0 45 1 36 1 0 testscene/results/stats_old.txt  2>/dev/null | tail -1
./minpt_bvh testscene/scene.obj "" "" testscene/results/out_new.pfm  16 8 0 64 64 0 1 2.8 0 0.9 0 45 1 36 1 1 testscene/results/stats_new.txt  2>/dev/null | tail -1
./minpt_bvh testscene/scene.obj "" "" testscene/results/out_new2.pfm 16 8 0 64 64 0 1 2.8 0 0.9 0 45 1 36 1 1 testscene/results/stats_new2.txt 2>/dev/null | tail -1

echo "--- old vs new ---"
python3 testscene/compare.py testscene/results/stats_old.txt testscene/results/stats_new.txt
echo "--- new vs new (determinism) ---"
python3 testscene/compare.py testscene/results/stats_new.txt testscene/results/stats_new2.txt
