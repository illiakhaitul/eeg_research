from typing import Dict

import mne

import config


def compute_evokeds(epochs: mne.Epochs) -> Dict[str, mne.Evoked]:
    """
    Compute averaged ERP (Evoked) for each condition defined in config.EVENT_ID.
    """
    evokeds = {}
    for cond_name in config.EVENT_ID.keys():
        if cond_name not in epochs.event_id:
            print(f"Warning: condition '{cond_name}' not found in epochs.")
            continue
        evokeds[cond_name] = epochs[cond_name].average()
    return evokeds


def save_evokeds(evokeds: Dict[str, mne.Evoked], subject: str) -> None:
    """
    Save Evoked objects to derivatives folder.
    """
    for name, ev in evokeds.items():
        ev_fname = config.DERIV_ROOT / f"sub-{subject}_evoked-{name}.fif"
        ev.save(ev_fname, overwrite=True)
        print(f"Saved evoked '{name}' for sub-{subject} to {ev_fname}")