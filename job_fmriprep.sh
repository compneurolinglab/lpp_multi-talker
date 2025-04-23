#!/bin/bash
#SBATCH --job-name=preproc
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --output=preproc.txt
#SBATCH --error=preproc_err.txt
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=200G

module load singularity/3.5.3
singularity build fmriprep.simg docker://poldracklab/fmriprep:latest

bids_root_dir = /scratch/ResearchGroups/lt_jixingli/lpp_multitalker/
subj = 01
nthreads = 12
mem = 150
container = singularity
mem=`echo "${mem//[!0-9]/}"`
mem_mb=`echo $(((mem*1000)-5000))`

export TEMPLATEFLOW_HOME = /home/zhengwuma2/.cache/templateflow
export FS_LICENSE = /scratch/zhengwuma2/utlis/license.txt
echo ">>> Begin Preprocessing..."
unset PYTHONPATH; singularity run -B /home/zhengwuma2/.cache/templateflow:/opt/templateflow fmriprep.simg \
		$bids_root_dir $bids_root_dir/derivatives \
		participant \
		--participant-label $subj \
		--skip-bids-validation \
		--md-only-boilerplate \
		--fs-license-file $FS_LICENSE \
		--fs-no-reconall \
		--output-spaces MNI152NLin2009cAsym:res-2 \
		--nthreads $nthreads \
		--stop-on-first-crash \
		--mem_mb $mem_mb \
		-w fmriprep_work
echo "End ..."