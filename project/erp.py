from typing import Dict

import mne

import config


# def compute_evokeds(epochs: mne.Epochs) -> Dict[str, mne.Evoked]:
#     """
#     Compute averaged ERP (Evoked) for each condition defined in config.EVENT_ID.
#     """
#     evokeds = {}
#     for cond_name in config.EVENT_ID.keys():
#         if cond_name not in epochs.event_id:
#             print(f"Warning: condition '{cond_name}' not found in epochs.")
#             continue
#         evokeds[cond_name] = epochs[cond_name].average()
#     return evokeds

def compute_spn_metrics(evokeds: Dict[str, mne.Evoked], roi_channels):
    """
    Compute subject-level SPN metrics in microvolts for a given ROI.
    Returns symmetry mean, random mean, and SPN difference mean.
    """
    evoked_sym = evokeds["symmetry"]
    evoked_ran = evokeds["random"]

    # Overall mean across ROI and time (QC-style summary)
    symmetry_mean_uv = evoked_sym.copy().pick(roi_channels).data.mean() * 1e6
    random_mean_uv = evoked_ran.copy().pick(roi_channels).data.mean() * 1e6

    # SPN difference in the main time window
    spn_diff = mne.combine_evoked([evoked_sym, evoked_ran], weights=[1, -1])
    spn_mean_uv = spn_diff.copy().pick(roi_channels).crop(0.3, 1.0).data.mean() * 1e6

    return symmetry_mean_uv, random_mean_uv, spn_mean_uv

def compute_evokeds(epochs: mne.Epochs, subject: str):
    evokeds = {}

    for cond_name in config.EVENT_ID.keys():
        if cond_name not in epochs.event_id:
            print(f"Warning: condition '{cond_name}' not found in epochs.")
            continue
        evokeds[cond_name] = epochs[cond_name].average()

    metrics = None
    # --- Compute SPN ---
    if "symmetry" in evokeds and "random" in evokeds:
        symmetry_mean_uv, random_mean_uv, spn_mean_uv = compute_spn_metrics(
            evokeds,
            config.SPN_ROI_MAIN,
        )

        print(f"--- Main ROI: {config.SPN_ROI_MAIN} ---")
        print(f"Symmetry Mean: {symmetry_mean_uv:.4f} µV")
        print(f"Random Mean:   {random_mean_uv:.4f} µV")
        print(f"Net SPN:       {spn_mean_uv:.4f} µV")

        metrics = {
            "symmetry_mean_uv": symmetry_mean_uv,
            "random_mean_uv": random_mean_uv,
            "spn_mean_uv": spn_mean_uv,
        }

        # --- Difference wave plot for SPN verification ---
        diff = mne.combine_evoked(
            [evokeds["symmetry"], evokeds["random"]],
            weights=[1, -1]
        )
        fig = diff.plot(
            picks=config.SPN_ROI_MAIN,
            titles="SPN difference wave (symmetry - random)",
            show=False
        )
        out_dir = config.get_subject_fig_dir(subject)
        spn_fig_path = out_dir / f"sub-{subject}_spn_diff.png"
        fig.savefig(spn_fig_path, dpi=300, bbox_inches="tight")
        print(f"Saved SPN difference figure to {spn_fig_path}")

    return evokeds, metrics


def save_evokeds(evokeds: Dict[str, mne.Evoked], subject: str) -> None:
    """
    Save Evoked objects to derivatives folder.
    """
    out_dir = config.get_subject_deriv_dir(subject)
    for name, ev in evokeds.items():
        ev_fname = out_dir / f"sub-{subject}_evoked-{name}.fif"        
        ev.save(ev_fname, overwrite=True)
        print(f"Saved evoked '{name}' for sub-{subject} to {ev_fname}")