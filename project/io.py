from pathlib import Path
from typing import Dict

import mne
from mne_bids import BIDSPath, read_raw_bids

import config


def make_bids_path(subject: str) -> BIDSPath:
    """
    Create a BIDSPath for a given subject (task 'jacobsen', eeg, bdf).
    """
    return BIDSPath(
        subject=subject,
        task="jacobsen",
        datatype="eeg",
        suffix="eeg",
        extension=".bdf",
        root=config.BIDS_ROOT,
    )


def load_raw(subject: str) -> mne.io.BaseRaw:
    """
    Load raw EEG data for one subject from the BIDS dataset.

    Uses mne-bids to respect all metadata (channels.tsv, electrodes, coordsystem).
    Returns a Raw object with preload=True.
    """
    bids_path = make_bids_path(subject)

    raw = read_raw_bids(bids_path)
    raw.load_data()
    
    try:
        montage = mne.channels.make_standard_montage("biosemi64")
        raw.set_montage(montage, on_missing="ignore")
        print("Applied standard BioSemi64 montage.")
    except Exception as e:
        print("WARNING: could not set montage:", e)
    return raw


def get_events_tsv_path(subject: str) -> Path:
    """
    Return the path to sub-XXX_task-jacobsen_events.tsv.
    """
    sub = f"sub-{subject}"
    eeg_dir = config.BIDS_ROOT / sub / "eeg"
    events_path = eeg_dir / f"{sub}_task-jacobsen_events.tsv"
    if not events_path.exists():
        raise FileNotFoundError(f"Events file not found: {events_path}")
    return events_path