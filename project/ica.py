"""
Independent Component Analysis (ICA) module.
Handles fitting and application of ICA for artifact rejection.
"""
from pathlib import Path
import mne
import config


def get_ica_fname(subject: str) -> Path:
    # File path where ICA solution for a subject will be stored.
    out_dir = config.get_subject_deriv_dir(subject)
    return out_dir/ f"sub-{subject}_ica.fif"


def fit_ica(raw: mne.io.BaseRaw, subject: str) -> mne.preprocessing.ICA:
    """
    Fit an ICA model on the preprocessed raw data.

    We chose FastICA with 30 components because it provides an 
    optimal balance. It is computationally efficient while providing enough 
    dimensions to cleanly separate ocular and cardiac artifacts from the 
    underlying neural signal in our 64-channel array.
    """
    ica = mne.preprocessing.ICA(
        n_components=config.ICA_N_COMPONENTS,
        method=config.ICA_METHOD,
        random_state=config.ICA_RANDOM_STATE,
        max_iter="auto",
    )
    ica.fit(raw)

    ica_fname = get_ica_fname(subject)
    ica.save(ica_fname, overwrite=True)
    print(f"Saved ICA for sub-{subject} to {ica_fname}")

    return ica


def load_ica(subject: str) -> mne.preprocessing.ICA:
    # Load a previously saved ICA solution.
    ica_fname = get_ica_fname(subject)
    return mne.preprocessing.read_ica(ica_fname)

def apply_ica(raw, ica, subject):
    # Apply targeted ICA exclusion based on our configuration map.
    exclude = config.ICA_EXCLUDE_MAP.get(subject, [])
    
    if not exclude:
        print(f"\n[!] WARNING: ICA_EXCLUDE_MAP for {subject} is EMPTY.")
        print(f"Inspect images in {config.FIG_ROOT} and update config.py.")
        # We return the original raw; it's 'dirty', but the script won't crash
        return raw.copy() 

    ica.exclude = exclude
    raw_clean = raw.copy()
    ica.apply(raw_clean)
    return raw_clean