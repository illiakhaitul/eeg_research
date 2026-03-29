"""
Epoching module.
Handles BIDS event extraction, alignment, and MNE Epoch creation.
"""

from typing import Tuple
import numpy as np
import pandas as pd
import mne

import config
from .io import get_events_tsv_path


def load_events(subject: str) -> np.ndarray:
    """
    Read events from the BIDS events.tsv file and convert to MNE events array.

    We use the 'sample' column as event sample index and 'value' as event code.
    Rows with values in config.IGNORE_EVENT_VALUES are dropped.
    """
    events_path = get_events_tsv_path(subject)
    df = pd.read_csv(events_path, sep="\t")

    # Drop ignored event codes
    if "value" not in df.columns:
        raise ValueError(f"'value' column not found in {events_path}")
    df = df[~df["value"].isin(config.IGNORE_EVENT_VALUES)]

    samples = df["sample"].astype(int).to_numpy()
    event_codes = df["value"].astype(int).to_numpy()

    events = np.column_stack([samples, np.zeros_like(samples), event_codes])
    return events


def make_epochs(
    raw: mne.io.BaseRaw,
    subject: str,
) -> mne.Epochs:
    """
    Create MNE Epochs for one subject.
    """
    events = load_events(subject)
    
    sfreq_orig = config.ORIG_SFREQ
    sfreq_new = raw.info["sfreq"]

    events[:,0] = np.round(events[:,0] / sfreq_orig * sfreq_new).astype(int)

    # Sanity check: at least some events
    if len(events) == 0:
        raise RuntimeError(f"No events found for subject {subject}.")
    
    reject = dict(eeg=100e-6)

    epochs = mne.Epochs(
        raw,
        events=events,
        event_id=config.EVENT_ID,
        tmin=config.TMIN,
        tmax=config.TMAX,
        baseline=config.BASELINE,
        preload=True,
        reject=reject,
    )

    # Save epochs to derivatives
    out_dir = config.get_subject_deriv_dir(subject)
    epo_fname = out_dir/ f"sub-{subject}_epo.fif"
    epochs.save(epo_fname, overwrite=True)
    print(f"Saved epochs for sub-{subject} to {epo_fname}")

    return epochs