
from pathlib import Path

BIDS_ROOT = Path(r"D:\VUZ\uni\code_rest\EEG_Lecture\ds004347") 

# Where to store our derivatives (preprocessed data, figures, etc.)
DERIV_ROOT = BIDS_ROOT / "derivatives" / "eegtigers"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# We'll start with a single subject for Milestone 3
SUBJECTS = ["001"]
""" SUBJECTS = [f"{i:03d}" for i in range(1, 25)] """

# ==== FILTERING / PREPROCESSING ===========================================

# Your change vs authors: Band-pass instead of simple low-pass at 25 Hz
L_FREQ = 0.1   # high-pass
H_FREQ = 40.0  # low-pass

# Powerline noise
NOTCH_FREQS = (50.0,)  # Hz

# ICA parameters
ICA_METHOD = "fastica"
ICA_N_COMPONENTS = 30  # can be None (all) or number < n_channels

# List of ICA components to remove (will be updated after visual inspection)
ICA_EXCLUDE = []  # e.g. [0, 1, 5]

# Time window around each stimulus (in seconds)
TMIN = -0.2
TMAX = 0.8

# Classic baseline correction window
BASELINE = (-0.2, 0.0)

# Event codes from sub-001_task-jacobsen_events.tsv
EVENT_ID = {
    "random": 1,
    "symmetry": 3,
}

IGNORE_EVENT_VALUES = [255]  # start/sync trigger

# Channels of interest for ERP plot (occipital / parietal)
ERP_CHANNELS = ["Oz", "O1", "O2", "POz"]

# General figure output folder
FIG_ROOT = DERIV_ROOT / "figures"
FIG_ROOT.mkdir(parents=True, exist_ok=True)