import sys
import os
import numpy as np
import nibabel as nib
import pandas as pd
import mne, eelbrain
from scipy.stats import zscore, pearsonr
from mne.stats import spatio_temporal_cluster_1samp_test
import matplotlib.pyplot as plt

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

group = 'single'
raw = mne.io.read_raw_brainvision('Analysis/sample/sub-01_task-multitalker_eeg.vhdr',preload=True)
info = raw.info
montage = mne.channels.read_custom_montage('Analysis/CACS-64.bvef')
info.set_montage(montage)
adjacency, ch_names = mne.channels.find_ch_adjacency(info,'eeg')  

data = np.load('Data/eeg/%s_all.npy' %group)
median_data = np.load('Data/eeg/%s_median.npy' %group)

# inter-subject correlation
n_channels = 64
corr = np.zeros((n_channels,n_subj))
for c in range(n_channels):
 for i in range(n_subj):
  subj_channel = data[i,c,:]
  corr[c,i],_ = pearsonr(median_channel[c],subj_channel) 
corr = np.nan_to_num(zscore(corr,axis=0,nan_policy='omit'))

# spatiotemporal clustering
cor_exp = np.expand_dims(corr.T,axis=1)
t_val, clusters, p_val, H0 = spatio_temporal_cluster_1samp_test(
																													cor_exp, n_permutations=10000, 
																													adjacency=adjacency, tail=1)
