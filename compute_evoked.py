import os sys
import numpy as np
import pandas as pd

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

group = 'attend'
s1 = pd.read_csv('s1_word_info.csv')
s2 = pd.read_csv('s2_word_info.csv')
	 
if group == 'single':
 sessions = ['single_f','single_m']
elif group in ['attend','unattend']:
 sessions = ['mixed_f','mixed_m']

def get_word(subj_id,session,word):
 subj_data = np.load('Data/subj%d_%s.npy' %(subj_id,session))
 subj_word = []
 for idx,row in word.iterrows():
  offset = int(row['offset'])
  if offset+50 < subj_data.shape[1]:
   subj_word.append(subj_data[:,offset-10:offset+51])
  else:
   continue
 subj_word = np.array(subj_word)
 return subj_word

all_data = []
n_subjs = 25
for i in range(1,n_subjs+1):
 subj_word1 = get_word(i,sessions[0],s1)
 subj_word2 = get_word(i,sessions[1],s2)
 subj_word = np.concatenate([subj_word1,subj_word2],axis=0)
 mean_word = np.mean(subj_word,axis=0)
 all_data.append(mean_word)
 
all_data = np.array(all_data)
mean_data = np.mean(all_data,axis=0)
np.save('Results/evoked/evoked_all_%s.npy' %group,all_data)
np.save('Results/evoked/evoked_mean_%s.npy' %group,mean_data)

