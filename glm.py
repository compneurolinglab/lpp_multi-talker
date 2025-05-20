import os
import sys
import nibabel as nib
import numpy as np
import pandas as pd
import nilearn
from numpy import genfromtxt
from scipy.stats import zscore
from nilearn.image import resample_to_img
from nilearn.datasets import load_mni152_gm_mask
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img, cluster_level_inference

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

subjects = ['sub-01','sub-02','sub-03','sub-04','sub-05',
            'sub-06','sub-07','sub-08','sub-09','sub-10',
            'sub-11','sub-12','sub-13','sub-14','sub-15',
            'sub-16','sub-17','sub-18','sub-19','sub-20',
            'sub-21','sub-22','sub-23','sub-24','sub-25']
subj_id = int(sys.argv[1])-1
condition = sys.argv[2]
subj = subjects[subj_id]

df_run = pd.read_csv('Analysis/run_list.csv')
df_onset = pd.read_csv('Analysis/fmri_onset.csv')
affine = np.load('Analysis/affine.npy')

def get_condition_run(subj_id,condition):
 df_subj = df_run.iloc[subj_id]
 if condition == 'single':
  col1 = 'single_f'
  col2 = 'single_m'
 elif condition in ['attend','unattend']:
  col1 = 'mixed_f'
  col2 = 'mixed_m'
 for idx, col in enumerate(df_subj[3:]):
  if col == col1:
   run_idx1 = idx+1
  elif col == col2:
   run_idx2 = idx+1
 return run_idx1,run_idx2

run_idx1,run_idx2 = get_condition_run(subj_id,condition)
img1 = nib.load('Data/derivatives/fmriprep/%s/func/%s_task-multitalker_run-%d_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz' %(subj,subj,run_idx1))
img2 = nib.load('Data/derivatives/fmriprep/%s/func/%s_task-multitalker_run-%d_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz' %(subj,subj,run_idx2))
img1_data = np.nan_to_num(zscore(img1.get_fdata()[:,:,:,onset1:onset1+600],nan_policy='omit'))
img2_data = np.nan_to_num(zscore(img2.get_fdata()[:,:,:,onset2:onset2+600],nan_policy='omit'))
fmri_data = np.concatenate([img1_data,img2_data],axis=3)
fmri_img = nib.Nifti1Image(fmri_data,affine=affine)

gm_mask = load_mni152_gm_mask()
mask = resample_to_img(gm_mask,fmri_img,interpolation='nearest')

# load regressors
regs = ['f0','intensity','word']
reg1 = np.genfromtxt('Analysis/hrf_female.csv',delimiter=',')[:600,:]
reg2 = np.genfromtxt('Analysis/hrf_male.csv',delimiter=',')[:600,:]
if condition in ['single','attend']: 
 X = np.concatenate([reg1,reg2],axis=0)
else:
 X = np.concatenate([reg2,reg1],axis=0)
X = np.nan_to_num(zscore(X,nan_policy='omit'))

contrast = np.eye(X.shape[1])
design_matrix = pd.DataFrame(X)
first_level_model = FirstLevelModel(t_r=1,hrf_model='spm',mask_img=mask)
first_level_model.fit(fmri_img,design_matrices=design_matrix)
for i, reg in enumerate(regs):
	beta_map = first_level_model.compute_contrast(contrast[i],output_type='effect_size')
	nib.save(beta_map, 'Results/glm/subj%d_%s_%s_beta.nii' % ((subj_id+1),condition,regs[i]))

# 2nd-level model
session = 'attend'
group = 'word'
n_subj = 25

betas = []
for i in range(1,n_subj+1):
	beta = nib.load('Results/glm/subj%d_%s_%s_beta.nii' %(i,session,group))#(97,115,97)
	beta_data = zscore(beta.get_fdata().flatten(),nan_policy='omit')
	beta_data = np.nan_to_num(beta_data)
	beta_data = beta_data.reshape(beta.shape)
	beta = nib.Nifti1Image(beta_data,affine=beta.affine)
	betas.append(beta)

design_matrix = pd.DataFrame([1]*len(betas),columns=['intercept'])
second_level_model = SecondLevelModel(smoothing_fwhm=8,n_jobs=4)
second_level_model.fit(betas,design_matrix=design_matrix)
zmap = second_level_model.compute_contrast(second_level_contrast='intercept',output_type='z_score')
stat_map = cluster_level_inference(zmap,threshold=6,alpha=0.001)
stat_map_resampled = resample_to_img(stat_map,gray_matter_mask,interpolation='nearest')
x = stat_map_resampled.get_fdata()*gray_matter_mask.get_fdata()
x = nib.Nifti1Image(x,affine=gray_matter_mask.affine)
nib.save(x,'Results/glm/cluster_%s_%s.nii' %(session,group))
