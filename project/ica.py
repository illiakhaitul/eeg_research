from pathlib import Path
from typing import Iterable, Optional

import mne

import config


def get_ica_fname(subject: str) -> Path:
    """
    File path where ICA solution for a subject will be stored.
    """
    return config.DERIV_ROOT / f"sub-{subject}_ica.fif"


def fit_ica(raw: mne.io.BaseRaw, subject: str) -> mne.preprocessing.ICA:
    """
    Fit an ICA model on the preprocessed raw data.

    Parameters
    ----------
    raw : Raw
        Preprocessed raw data (preferably high-pass filtered).
    subject : str
        Subject ID (e.g. "001").

    Returns
    -------
    ica : mne.preprocessing.ICA
    """
    ica = mne.preprocessing.ICA(
        n_components=config.ICA_N_COMPONENTS,
        method=config.ICA_METHOD,
        random_state=97,
        max_iter="auto",
    )
    ica.fit(raw)

    ica_fname = get_ica_fname(subject)
    ica.save(ica_fname, overwrite=True)
    print(f"Saved ICA for sub-{subject} to {ica_fname}")

    return ica


def load_ica(subject: str) -> mne.preprocessing.ICA:
    """
    Load a previously saved ICA solution.
    """
    ica_fname = get_ica_fname(subject)
    return mne.preprocessing.read_ica(ica_fname)


def apply_ica(
    raw: mne.io.BaseRaw,
    ica: mne.preprocessing.ICA,
    exclude: Optional[Iterable[int]] = None,
) -> mne.io.BaseRaw:
    """
    Apply ICA to remove artefactual components.

    For Milestone 3 we use a manual list from config.ICA_EXCLUDE.
    Later you can replace this by automatic IC classification (ICLabel, etc.).
    """
    raw_clean = raw.copy()
    if exclude is None:
        exclude = config.ICA_EXCLUDE

    ica.exclude = list(exclude)
    print(f"Applying ICA, excluding components: {ica.exclude}")
    ica.apply(raw_clean)

    return raw_clean