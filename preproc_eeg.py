import os
import numpy as np
import os.path as op
import mne
from autoreject import Ransac
from scipy.stats import zscore
import pandas as pd  
from pathlib import Path
import matplotlib.pyplot as plt
import scipy.io as sio
from pyprep.prep_pipeline import PrepPipeline
import subprocess
import sys

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)
i = int(sys.argv[1])-1


bad_types = ['bad_by_nan', 'bad_by_flat', 'bad_by_deviation', 'bad_by_hf_noise', 
             'bad_by_correlation', 'bad_by_SNR', 'bad_by_dropout', 'bad_by_ransac']
sub_cha = []
folder_path = f'sorted/sub-{i:02d}/'
vhdr_file = folder_path + f'sub-{i:02d}_task-multitalker_eeg.vhdr'
print(i)
try:
    raw = mne.io.read_raw_brainvision(vhdr_file, misc='auto')   
    raw.load_data()
    montage = mne.channels.read_custom_montage('CACS-64.bvef')
    raw.set_montage(montage, verbose=True)
    sample_rate = raw.info["sfreq"]
    raw_copy = raw.copy()
    
    prep_params = {
        "ref_chs": "eeg",
        "reref_chs": "eeg",
        "line_freqs": np.arange(50, sample_rate / 2, 50),
    }
    
    prep = PrepPipeline(raw_copy, prep_params, montage)
    prep.fit()
    
    for b in bad_types:
        cha = prep.noisy_channels_original[b]
        sub_cha.append([i, b, cha])
except Exception:
    print(f"Subject {i}: Too many bad channels to perform robust referencing. Skipping this subject.")
    continue
sub_cha_df = pd.DataFrame(sub_cha, columns=['subject', 'bad_type', 'channels'])
sub_cha_df.to_csv('bad_channels.csv' , index=False)




#ica
try: 
    folder_path = f'sorted/sub-{i:02d}/'
    vhdr_file = folder_path + f'sub-{i:02d}_task-multitalker_eeg.vhdr'
    raw = mne.io.read_raw_brainvision(vhdr_file, misc='auto')   
    raw.load_data()
    montage = mne.channels.read_custom_montage('CACS-64.bvef')
    raw.set_montage(montage, verbose=True)
    sample_rate = raw.info["sfreq"]
    bad_channels = pd.read_csv('bad_channel.csv')
    bad_chan = bad_channels.query(f'subject == {i}').query("bad_type == 'bad_by_correlation'")['channels']
    bad_chan = [chan.strip().strip("'") for chan in bad_chan.iloc[0].split(',')]  

    if not (len(bad_chan) == 1 and pd.isna(bad_chan[0])):  # Skip if bad_chan is [nan]
        bad_chan = [chan for chan in bad_chan if isinstance(chan, str) and chan]  
        raw.info['bads'] = bad_chan
        raw.interpolate_bads(reset_bads=True)

    # filtering
    raw.filter(0.1, 39, fir_design='firwin', picks=['eeg']) 

    # ICA
    ica = mne.preprocessing.ICA(n_components=20, random_state=97, method='fastica')
    ica.fit(raw)  
    save_dir = f'preprocessed/sub-{i:02d}'

    fig = ica.plot_components()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    fig.savefig(os.path.join(save_dir, f'sub-{i:02d}_ica.png'))  # Save each figure with a unique filename
    plt.close(fig) 

    with mne.viz.use_browser_backend('matplotlib'):  
        fig = ica.plot_sources(raw, show_scrollbars=False, show=False) 
        fig.savefig(os.path.join(save_dir, f'sub-{i:02d}_time.png')) 

except Exception:
    print(f"Subject {i}: something wrong with it")
    continue
