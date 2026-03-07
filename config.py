
from pathlib import Path

# BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\EEG_project\data\ds004347") 
BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\dataset\ds004347")

# Where to store our derivatives (preprocessed data, figures, etc.)
DERIV_ROOT = BIDS_ROOT / "derivatives" / "eegtigers"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# We'll start with a single subject for Milestone 3
SUBJECTS = ["001"]
# SUBJECTS = [f"{i:03d}" for i in range(1, 25)]

# ==== FILTERING / PREPROCESSING ===========================================

#Identify bad channels manually
BAD_CHANNELS_MAP = {
    "001": ["P2", "FC6", "F8", "AF7", "Fp1", "AF4"],  # may only provide first 3 if we want to stick to our change
}

# Your change vs authors: Band-pass instead of simple low-pass at 25 Hz
L_FREQ = 0.5   # high-pass
H_FREQ = 25.0  # low-pass

# Powerline noise
NOTCH_FREQS = (50.0,)  # Hz

# Resampling rate (Hz)
RESAMPLE_FREQ = 256

# ICA parameters
ICA_METHOD = "fastica" # may change this to a better one
ICA_N_COMPONENTS = 30  # can be None (all) or number < n_channels

# List of ICA components to remove (will be updated after visual inspection)
# ICA_EXCLUDE = [0,1,3]
ICA_EXCLUDE_MAP = {
    # "001": [0, 1, 3, 12, 15],  # [0, 1, 2, 3, 15] will use all this identified if removing 3 doesn't give better answer Starting empty for sub-001 should be filled after inspection
    "001": [0, 1, 2, 3, 4, 5, 8, 14, 15, 21]
}

# Time window around each stimulus (in seconds)
TMIN = -1
TMAX = 1

# Classic baseline correction window
BASELINE = (-0.2, 0.05)

EMG_ZM_CH = "EXG5"  

# Corrugator Supercilii (CS, Frowning) = EXG7 (Highest tonic activity)
EMG_CS_CH = "EXG7" 

# EMG High-pass filter frequency for isolating muscle spikes (typical > 20 Hz)
EMG_HPF = 20.0

# Event codes from sub-001_task-jacobsen_events.tsv
EVENT_ID = {
    "random": 3,
    "symmetry": 1,
}

IGNORE_EVENT_VALUES = [255]  # start/sync trigger

# Channels of interest for ERP plot (occipital / parietal)
ERP_CHANNELS = ["PO7", "PO8", "Oz", "O1", "O2", "POz"]

# General figure output folder
FIG_ROOT = DERIV_ROOT / "figures"
FIG_ROOT.mkdir(parents=True, exist_ok=True)