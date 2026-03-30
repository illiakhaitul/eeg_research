"""
=============================================================================
                                EEG Tigers
=============================================================================
Team Members & Subject Analyzed:
- Aman Kumar   : Subjects 001 - 012
- Illia Khaitul: Subjects 013 - 024
=============================================================================
"""

"""
This config.py file serves as the central hub for all parameters, settings, and utility functions 
used across our EEG data processing pipeline. By consolidating these configurations in one place, 
we ensure that our codebase remains modular, maintainable, and easily adaptable for future projects or different datasets.  
Update path specifically "BIDS_ROOT" variable to point to dataset and study-specific settings here before running.
Results can be found in the "derivatives/eegtigers" folder, organized by subject. Figures will be saved in "derivatives/eegtigers/figures".
"""

from pathlib import Path

# ==== DIRECTORIES ====
BIDS_ROOT = Path(r"E:\masters Stuttgart\Uni Work\sem 3\EEG\dataset\ds004347")
DERIV_ROOT = BIDS_ROOT / "derivatives" / "eegtigers"
DERIV_ROOT.mkdir(parents=True, exist_ok=True)

# ==== BIDS FILE METADATA ====
BIDS_TASK = "jacobsen"
BIDS_DATATYPE = "eeg"
BIDS_SUFFIX = "eeg"
BIDS_EXTENSION = ".bdf"

# General figure output folder
FIG_ROOT = DERIV_ROOT / "figures"
FIG_ROOT.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012",
            "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024"]

# ==== PREPROCESSING PARAMETERS ===========================================

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
	"013": ["POz", "Iz", "P8"],
    "014": ["AF7", "Fp1", "Fp2", "AF8", "TP8"],
    "015": ["Fp1", "AF7", "Fpz", "Fp2", "AF8"],
    "016": ["F2", "Fp1", "Fpz"],
    "017": ["POz"],
    "018": ["Fp1", "Fp2", "P9"], 
    "019": [],
    "020": ["P9", "O1", "TP7", "Fp1", "P10"],
    "021": ["PO4", "AF8", "FT7", "F4"],
    "022": ["P10"],
    "023": ["P9", "F5", "Fp1"],
    "024": ["P10", "P9", "Fp2"]
}

# This seems correct, because while originally author used 
# a simple 25 Hz low-pass filter, upgrading to a strict 0.5 - 30.0 Hz band-pass 
# removes slow-wave drifts and sweat artifacts while preserving the core frequencies 
# required to accurately measure the Sustained Posterior Negativity (SPN) effect.
L_FREQ = 0.5
H_FREQ = 30.0

# Resampling rate (Hz)
RESAMPLE_FREQ = 256

# Original sampling rate for ds004347 Experiment 1 BioSemi data
ORIG_SFREQ = 512

# ==== ICA PARAMETERS ====
"""
We chose FastICA with 30 components because it provides an 
optimal balance. It is computationally efficient while providing enough 
dimensions to cleanly separate ocular and cardiac artifacts from the 
underlying neural signal in our 64-channel array.
"""
ICA_METHOD = "fastica" 
ICA_N_COMPONENTS = 30
# This seems correct, because locking the random state ensures strict 
# reproducibility of the ICA component decomposition across different pipeline runs.
ICA_RANDOM_STATE = 97

# List of ICA components to remove (updated after visual inspection)
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
	"013": [1, 2],
    "014": [0, 1, 2],
    "015": [0, 1, 2],
    "016": [0, 1, 3, 4, 6],
    "017": [0, 4, 9, 13, 22],
    "018": [],
    "019": [0],
    "020": [3, 9],
    "021": [2, 4, 9], 
    "022": [0, 1],
    "023": [0, 1, 3],
    "024": [0, 1, 2, 3, 5]
}

# ==== EPOCHING PARAMETERS ====
# ==== Time window around each stimulus (in seconds) ====
TMIN = -1
TMAX = 1

# This seems correct, because author used a -200 to +50 ms 
# baseline. By modernizing to a strict -200 to 0 ms pre-stimulus baseline, we prevent 
# any post-stimulus visual evoked potentials (VEPs) from bleeding into and artificially 
# skewing the baseline correction phase.
BASELINE = (-0.2, 0.0)

# ==== Event codes from sub-0XX_task-jacobsen_events.tsv and sub-0XX_task-jacobsen_events.json file ====
EVENT_ID = {
    "random": 3,
    "symmetry": 1,
}

# ==== Ignore start/sync markers ====
IGNORE_EVENT_VALUES = [255] 

# ==== STATISTICAL PARAMETERS ====
# We choose 1000 permutations, because it provides a stable, 
# robust approximation of the null distribution for the spatio-temporal cluster test.
CLUSTER_ALPHA = 0.05
CLUSTER_PERMUTATIONS = 1000


# These channels align with the primary SPN regions of interest(ROI)
# (Lateral Occipital / Parietal) identified in the original paper and are commonly used in EEG research to capture visual processing effects.
ERP_CHANNELS = ["PO7", "PO8", "Oz", "O1", "O2", "POz"]

# Main ROI for final reported SPN
SPN_ROI_MAIN = ["PO7", "PO8"]


# ==== UTILITY FUNCTIONS ====
# update directory paths once defined above with variable name "BIDS_ROOT", then we use these helpers everywhere
# to keep the code modular and avoid hard-coded paths.
def get_subject_deriv_dir(subject: str) -> Path:
    out = DERIV_ROOT / f"sub-{subject}"
    out.mkdir(parents=True, exist_ok=True)
    return out

def get_subject_fig_dir(subject: str) -> Path:
    out = FIG_ROOT / f"sub-{subject}"
    out.mkdir(parents=True, exist_ok=True)
    return out
