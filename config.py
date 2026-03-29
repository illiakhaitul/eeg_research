from pathlib import Path

"""
=============================================================================
                                EEG Tigers
=============================================================================
Team Members & Subject Analyzed:
- Aman Kumar   : Subjects 001 - 012
- Illia Khaitul: Subjects 013 - 024
=============================================================================
"""

# BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\EEG_project\data\ds004347") 
BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\dataset\ds004347")

# Where to store our derivatives (preprocessed data, figures, etc.)
DERIV_ROOT = BIDS_ROOT / "derivatives" / "eegtigers"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# General figure output folder
FIG_ROOT = DERIV_ROOT / "figures"
FIG_ROOT.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012",
            "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024"]
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
    "008": ["P9"],
    "009": ["FC6"],
    "010": [],
    "011": [],
    "012": [],
	"013": ["POz", "AF8", "CP4", "Iz", "Fp1"],
    "014": ["AF7", "Fp1", "Fp2", "AF8", "TP8", "Fpz", "AF3"],
    "015": ["Fp1", "AF7", "Fpz", "Fp2", "AF8"],
    "016": ["F2", "Fp1", "Fpz"],
    "017": ["Fp1", "Fp2", "Fpz", "AF7", "AF8", "AF3", "AF4", "AFz", "Iz"], # better with reject = dict(eeg=150e-6)
    "018": ["C4", "CP4", "CP2", "FCz", "Cz", "Fp1", "Fp2", "AF8"],  # better with reject = dict(eeg=150e-6)
    "019": [],
    "020": ["P9", "O1", "TP7", "Fp1", "P10"],
    "021": ["PO4", "AF8", "FT7", "Fp2", "Fp1", "AF4", "Oz", "F4"],
    "022": ["P10"],
    "023": ["P9", "F5", "Fp1"],
    "024": ["P10", "P9", "Fp2", "Fpz", "AF3"]
}

# Our change vs authors: Band-pass instead of simple low-pass at 30 Hz
L_FREQ = 0.5   # high-pass
H_FREQ = 30.0  # low-pass

# Powerline noise
# NOTCH_FREQS = (50.0,)  # Hz

# Resampling rate (Hz)
RESAMPLE_FREQ = 256

# Original sampling rate for ds004347 Experiment 1 BioSemi data
ORIG_SFREQ = 512

# ICA parameters
ICA_METHOD = "fastica" 
ICA_N_COMPONENTS = 30
ICA_RANDOM_STATE = 97

# List of ICA components to remove (will be updated after visual inspection)
ICA_EXCLUDE_MAP = {
    "001": [0, 3, 4, 5, 6],
    "002": [1, 5, 6, 10, 21],
    "003": [0, 1],
    "004": [0, 2],
    "005": [0, 2],
    "006": [0, 1],
    "007": [0, 2],
    "008": [2],
    "009": [1],
    "010": [0],
    "011": [0, 1],
    "012": [0,1],
	"013": [1,2,3],
    "014": [0, 1, 2, 4, 6],
    "015": [0,1,2],
    "016": [3, 4, 6],
    "017": [1, 4, 9, 13], # better with reject = dict(eeg=150e-6)
    "018": [],
    "019": [],
    "020": [3, 9],
    "021": [2, 4, 9, 24, 26], 
    "022": [0, 1, 2, 3, 26, 29],
    "023": [0, 1, 3, 8, 13, 26, 29],
    "024": [0, 2, 3, 5, 9, 10]
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

# ==== STATISTICAL PARAMETERS ====
CLUSTER_ALPHA = 0.05
CLUSTER_PERMUTATIONS = 1000

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