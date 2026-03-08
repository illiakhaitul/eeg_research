
from pathlib import Path

# BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\EEG_project\data\ds004347") 
BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\dataset\ds004347")

# Where to store our derivatives (preprocessed data, figures, etc.)
DERIV_ROOT = BIDS_ROOT / "derivatives" / "eegtigers"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# General figure output folder
FIG_ROOT = DERIV_ROOT / "figures"
FIG_ROOT.mkdir(parents=True, exist_ok=True)

# We'll start with a single subject for Milestone 3
SUBJECTS = ["001", "002", "003", "004", "005",]
# SUBJECTS = [f"{i:03d}" for i in range(1, 25)]

# ==== FILTERING / PREPROCESSING ===========================================

#Identify bad channels manually
BAD_CHANNELS_MAP = {
    "001": ["P2", "FC6", "F8", "AF7", "Fp1", "AF4"],
    "002": ["P1"],
    "003": ["F3"],
    "004": ["Fp1", "AF7", "P9", "T8", "TP8", "P6", "PO4", "Fp2", "FT8", "AF8"],
    "005": [],
    "006": [],
    "007": [],
    "008": [],
    "009": [],
    "010": [],
    "011": [],
    "012": [],
}

# Your change vs authors: Band-pass instead of simple low-pass at 30 Hz
L_FREQ = 0.5   # high-pass
H_FREQ = 30.0  # low-pass

# Powerline noise
# NOTCH_FREQS = (50.0,)  # Hz

# Resampling rate (Hz)
RESAMPLE_FREQ = 256

# Original sampling rate for ds004347 Experiment 1 BioSemi data
ORIG_SFREQ = 512

# ICA parameters
ICA_METHOD = "fastica" # may change this to a better one
ICA_N_COMPONENTS = 30  # can be None (all) or number < n_channels
ICA_RANDOM_STATE = 97

# List of ICA components to remove (will be updated after visual inspection)
# ICA_EXCLUDE = [0,1,3]
ICA_EXCLUDE_MAP = {
    "001": [0, 3, 4, 5, 6],
    "002": [1, 5, 6, 10, 21],
    "003": [0, 1],
    "004": [0, 2],
    "005": [0, 2],
    "006": [0, 1],
    "007": [0, 2],
    "008": [],
    "009": [],
    "010": [],
    "011": [],
    "012": [],
}

# Time window around each stimulus (in seconds)
TMIN = -1
TMAX = 1

# Classic baseline correction window
BASELINE = (-0.2, 0.0)

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

# Main ROI for final reported SPN (matches paper)
SPN_ROI_MAIN = ["PO7", "PO8"]

# Broader posterior ROI for QC / supportive checks
SPN_ROI_QC = ["PO7", "PO8", "Oz", "O1", "O2", "POz"]

def get_subject_deriv_dir(subject: str) -> Path:
    out = DERIV_ROOT / f"sub-{subject}"
    out.mkdir(parents=True, exist_ok=True)
    return out

def get_subject_fig_dir(subject: str) -> Path:
    out = FIG_ROOT / f"sub-{subject}"
    out.mkdir(parents=True, exist_ok=True)
    return out