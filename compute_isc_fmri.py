import sys
import os
import nibabel as nib
import numpy as np
from scipy.stats import pearsonr

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

def name2run(other,run_name):
 other_id = int(other.replace('sub-',''))
 df_other = df.iloc[other_id-1]
 for idx, col in enumerate(df_other[3:]):
  if col == run_name:
   return idx+1
 return None

subjects = ['sub-01','sub-02','sub-03','sub-04','sub-05',
            'sub-06','sub-07','sub-08','sub-09','sub-10',
            'sub-11','sub-12','sub-13','sub-14','sub-15',
            'sub-16','sub-17','sub-18','sub-19','sub-20',
            'sub-21','sub-22','sub-23','sub-24','sub-25']

df = pd.read_csv('Analysis/run_list.csv')
subj_id = int(sys.argv[1])-1
subj = subjects[subj_id]
subjects.remove(subj)

correlations = []
for i in range(1,5):
 run_name = df.iloc[subj_id]['run%d' %i]
 subj_img = nib.load('Data/derivatives/fmriprep/%s/func/%s_task-multitalker_run-%d_desc-preproc_bold.nii.gz' %(subj,subj,i)).get_fdata()
 scan_num = subj_data.shape[3]
 subj_data = subj_data.reshape(-1,scan_num)
 
 group_mean = np.zeros_like(subj_data)
 for iother, other in enumerate(subjects):
  run_id = name2run(other,run_name)
  other_id = int(other.replace('sub-',''))
  other_img = nib.load('Data/derivatives/%s/func/%s_task-multitalker_run-%d_desc-preproc_bold.nii.gz' %(other,other,run_id)).get_fdata()
  other_data = other_data.reshape(-1,scan_num)
  group_mean = (group_mean * iother + other_data)/(iother+1)

 corr = np.zeros(subj_data.shape[0])
 for j in range(subj_data.shape[0]):
  if subj_data[j,:].any() > 0 and group_mean[j,:].any() > 0:
   corr[j] = pearsonr(subj_data[j,:],group_mean[j,:])[0]
 correlations.append(corr)

correlations = np.array(correlations)
correlations_mean = np.mean(correlations,axis=0)

np.save('Results/isc/subj%d_isc.npy' %(subj_id+1), correlations)
np.save('Results/isc/subj%d_isc_mean.npy' %(subj_id+1), correlations_mean)