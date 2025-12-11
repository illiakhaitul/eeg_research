from typing import Dict

import matplotlib.pyplot as plt
import mne, os


import config

def make_subject_figdir(subject: str):
    out_dir = os.path.join(
        "D:/VUZ/uni/code_rest/EEG_Lecture/ds004347/derivatives/eegtigers/figures",
        f"sub-{subject}"
    )
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def plot_psd_before_after(
    raw_before: mne.io.BaseRaw,
    raw_after: mne.io.BaseRaw,
    subject: str,
) -> None:
    """
    Compare the power spectral density (PSD) before and after preprocessing.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    raw_before.plot_psd(ax=axes[0], show=False)
    axes[0].set_title("PSD - raw")
    raw_after.plot_psd(ax=axes[1], show=False)
    axes[1].set_title("PSD - filtered")

    fig.suptitle(f"sub-{subject}: PSD before vs after filtering")
    out = config.FIG_ROOT / f"sub-{subject}_psd_before_after.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved PSD figure to {out}")


def plot_raw_vs_clean(
    raw_before: mne.io.BaseRaw,
    raw_after: mne.io.BaseRaw,
    subject: str,
    duration: float = 5.0,
    start: float = 0.0,
) -> None:
    """
    Plot a short segment of raw vs ICA-cleaned data for visual comparison.
    """
    fig = raw_before.plot(
        start=start,
        duration=duration,
        n_channels=20,
        show=False,
        title=f"sub-{subject}: raw (top) vs clean (bottom)",
    )
    out = config.FIG_ROOT / f"sub-{subject}_raw_segment.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)

    fig2 = raw_after.plot(
        start=start,
        duration=duration,
        n_channels=20,
        show=False,
        title=f"sub-{subject}: cleaned segment",
    )
    out2 = config.FIG_ROOT / f"sub-{subject}_clean_segment.png"
    fig2.savefig(out2, dpi=150)
    plt.close(fig2)

    print(f"Saved raw vs clean segment plots to {out} and {out2}")


def plot_ica_components(ica, subject: str):
    """
    Plot ICA components, excluding EXG channels entirely to avoid overlapping
    montage positions. This solves the BioSemi EXG visualization bug.
    """

    # 1) Create a copy of ICA.info (so Raw info remains unchanged)
    info = ica.info.copy()

    # 2) Identify EXG channels
    exg_channels = [ch for ch in info['ch_names'] if ch.startswith("EXG")]

    # 3) Drop EXG channels from info before plotting ICA topographies
    if len(exg_channels) > 0:
        info = mne.pick_info(info, sel=[i for i, ch in enumerate(info['ch_names']) if ch not in exg_channels])

    try:
        # Force ICA to use modified info (only EEG channels)
        ica.info = info

        # We plot all ICA components
        picks = range(ica.n_components_)

        fig = ica.plot_components(picks=picks, show=False)
    except Exception as e:
        print("WARNING: Could not plot ICA components:", e)
        return

    # Save figure
    out_dir = make_subject_figdir(subject)
    fig_path = os.path.join(out_dir, f"sub-{subject}_ica_components.png")
    fig.savefig(fig_path, dpi=150)
    print(f"Saved ICA components figure to {fig_path}")


def plot_erp(
    evokeds: Dict[str, mne.Evoked],
    subject: str,
) -> None:
    """
    Plot ERP for channels of interest for each condition.
    """
    picks = [ch for ch in config.ERP_CHANNELS if ch in evokeds[next(iter(evokeds))].ch_names]

    if not picks:
        print("No ERP channels found in data; skipping ERP plot.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    for name, ev in evokeds.items():
        ev.plot(
            picks=picks,
            axes=ax,
            show=False,
            spatial_colors=True,
            time_unit="s",
        )

    ax.set_title(f"sub-{subject}: ERP at {', '.join(picks)}")
    out = config.FIG_ROOT / f"sub-{subject}_erp.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved ERP figure to {out}")


def plot_butterfly(
    evokeds: Dict[str, mne.Evoked],
    subject: str,
) -> None:
    """
    Butterfly plot (all channels) for each condition.
    """
    for name, ev in evokeds.items():
        fig = ev.plot(
            spatial_colors=True,
            time_unit="s",
            show=False,
            titles=dict(eeg=f"{name} - butterfly"),
        )
        out = config.FIG_ROOT / f"sub-{subject}_butterfly_{name}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"Saved butterfly figure for '{name}' to {out}")