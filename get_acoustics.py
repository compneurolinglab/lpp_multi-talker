import os, sys
import parselmouth
import numpy as np
from scipy.signal import spectrogram as sg 
from scipy.signal import hilbert
from scipy.io import wavfile

DIR = '/scratch/ResearchGroups/lt_jixingli/lpp_multitalker/'
os.chdir(DIR)

group = 'single_female'
snd = parselmouth.Sound('Analysis/%s.wav' %stim)

# get pitch
pitch = snd.to_pitch()
f0 = pitch.selected_array['frequency'].ravel()
f0[np.isnan(f0)] = 0

# get intensity
intensity = snd.to_intensity()
intensity_values = intensity.values.flatten()
