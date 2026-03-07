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

def compute_evokeds(epochs: mne.Epochs, subject: str) -> Dict[str, mne.Evoked]:
    evokeds = {}

    for cond_name in config.EVENT_ID.keys():
        if cond_name not in epochs.event_id:
            print(f"Warning: condition '{cond_name}' not found in epochs.")
            continue
        evokeds[cond_name] = epochs[cond_name].average()

    # --- Compute SPN ---
    if "symmetry" in evokeds and "random" in evokeds:

        picks = ["PO7", "PO8"]

        sym = evokeds["symmetry"].copy().pick(picks)
        rnd = evokeds["random"].copy().pick(picks)

        spn = sym.copy()
        spn.data = sym.data - rnd.data

        spn_value = spn.copy().crop(0.3,1.0).data.mean(axis=1).mean()
        print(f"SPN (symmetry - random) 300–1000ms PO7/PO8: {spn_value:.4f} µV")

        # --- Difference wave plot for SPN verification ---
        diff = mne.combine_evoked(
            [evokeds["symmetry"], evokeds["random"]],
            weights=[1, -1]
        )
        fig = diff.plot(
            picks=["PO7", "PO8"],
            titles="SPN difference wave (symmetry - random)",
            show=False
        )

        spn_fig_path = config.FIG_ROOT / f"sub-{subject}_spn_diff.png"
        fig.savefig(spn_fig_path, dpi=300, bbox_inches="tight")
        print(f"Saved SPN difference figure to {spn_fig_path}")

    return evokeds


def save_evokeds(evokeds: Dict[str, mne.Evoked], subject: str) -> None:
    """
    Save Evoked objects to derivatives folder.
    """
    for name, ev in evokeds.items():
        ev_fname = config.DERIV_ROOT / f"sub-{subject}_evoked-{name}.fif"
        ev.save(ev_fname, overwrite=True)
        print(f"Saved evoked '{name}' for sub-{subject} to {ev_fname}")