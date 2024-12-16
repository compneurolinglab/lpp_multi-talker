import sys
import os
from nipype.algorithms.confounds import TSNR

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

subjects = ['sub-01','sub-02','sub-03','sub-04','sub-05',
            'sub-06','sub-07','sub-08','sub-09','sub-10',
            'sub-11','sub-12','sub-13','sub-14','sub-15',
            'sub-16','sub-17','sub-18','sub-19','sub-20',
            'sub-21','sub-22','sub-23','sub-24','sub-25']

subj_id = int(sys.argv[1])-1
subj = subjects[subj_id]
tsnr = TSNR()

output = 'Results/tsnr/'
if not os.path.exists(output):
	os.makedirs(output)

for i in range(1,5):
	print('>>> raw %s, run%d' %(subj,i))
	f = "Data/%s/func/%s_task-multitalker_run-0%d_bold.nii.gz" %(subj,subj,i)
	tsnr.inputs.in_file = f
	tsnr.inputs.tsnr_file = os.path.join(output, '%s_run-%d_tsnr_raw.nii.gz' %(subj,i))
	tsnr.inputs.mean_file = os.path.join(output, '%s_run-%d_mean_raw.nii.gz' %(subj,i))
	tsnr.inputs.stddev_file = os.path.join(output, '%s_run-%d_stddev_raw.nii.gz' %(subj,i))
	tsnr.inputs.detrended_file = os.path.join(output, '%s_run-%d_detrended_raw.nii.gz' %(subj,i))
	tsnr.inputs.regress_poly = 4
	tsnr.run()
	
for i in range(1,5):
	print('>>> preprocessed %s, run_%d' %(subj,i))
	f = 'Data/derivatives/fmriprep/%s/func/%s_task-multitalker_run-%d_desc-preproc_bold.nii.gz' %(subj,subj,i)
	tsnr.inputs.in_file = f
	tsnr.inputs.tsnr_file = os.path.join(output, '%s_run-%d_tsnr_preproc.nii.gz' %(subj,i))
	tsnr.inputs.mean_file = os.path.join(output, '%s_run-%d_mean_preproc.nii.gz' %(subj,i))
	tsnr.inputs.stddev_file = os.path.join(output, '%s_run-%d_stddev_preproc.nii.gz' %(subj,i))
	tsnr.inputs.detrended_file = os.path.join(output, '%s_run-%d_detrended_preproc.nii.gz' %(subj,i))
	tsnr.inputs.regress_poly = 4
	tsnr.run()

