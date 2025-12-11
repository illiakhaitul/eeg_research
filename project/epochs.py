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

    # Drop ignored event codes (e.g. 255 = sync trigger)
    if "value" not in df.columns:
        raise ValueError(f"'value' column not found in {events_path}")
    df = df[~df["value"].isin(config.IGNORE_EVENT_VALUES)]

    samples = df["sample"].astype(int).to_numpy()
    event_codes = df["value"].astype(int).to_numpy()

    # MNE events: n_events x 3 -> [sample, 0, event_id]
    events = np.column_stack([samples, np.zeros_like(samples), event_codes])
    return events


def make_epochs(
    raw: mne.io.BaseRaw,
    subject: str,
) -> mne.Epochs:
    """
    Create MNE Epochs for one subject.

    Parameters
    ----------
    raw : Raw
        Preprocessed & ICA-cleaned raw data.
    subject : str
        Subject ID, e.g. "001".

    Returns
    -------
    epochs : mne.Epochs
    """
    events = load_events(subject)

    # Sanity check: at least some events
    if len(events) == 0:
        raise RuntimeError(f"No events found for subject {subject}.")

    epochs = mne.Epochs(
        raw,
        events=events,
        event_id=config.EVENT_ID,
        tmin=config.TMIN,
        tmax=config.TMAX,
        baseline=config.BASELINE,
        preload=True,
    )

    # Save epochs to derivatives
    epo_fname = config.DERIV_ROOT / f"sub-{subject}_epo.fif"
    epochs.save(epo_fname, overwrite=True)
    print(f"Saved epochs for sub-{subject} to {epo_fname}")

    return epochs