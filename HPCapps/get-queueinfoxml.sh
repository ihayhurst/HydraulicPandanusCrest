#!/usr/bin/bash
export  SGE_ROOT=/mnt/svm-chem/grid/univa
/mnt/svm-chem/grid/univa/bin/lx-amd64/qstat  -f -xml -u '*'
