"""
Visualization module.
Handles automated plotting for QC and final report figures.
"""

from typing import Dict
import matplotlib.pyplot as plt
import mne
from mne.viz import plot_compare_evokeds

import config

def make_subject_figdir(subject: str):
    return config.get_subject_fig_dir(subject)

def plot_psd_before_after(
    raw_before: mne.io.BaseRaw,
    raw_after: mne.io.BaseRaw,
    subject: str,
) -> None:
    """
    Compare the power spectral density (PSD) before and after filtering.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    raw_before.plot_psd(ax=axes[0], show=False)
    axes[0].set_title("PSD - raw")
    raw_after.plot_psd(ax=axes[1], show=False)
    axes[1].set_title("PSD - filtered")

    fig.suptitle(f"sub-{subject}: PSD before vs after filtering")
    out_dir = make_subject_figdir(subject)
    out = out_dir / f"sub-{subject}_psd_before_after.png"
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
    my_scalings = dict(eeg=50e-6) 
    
    fig = raw_before.plot(
        start=start,
        duration=duration,
        n_channels=20,
        scalings=my_scalings,
        show=False,
        title=f"sub-{subject}: raw (top) vs clean (bottom)",
    )
    out_dir = make_subject_figdir(subject)
    out = out_dir / f"sub-{subject}_raw_segment.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)

    fig2 = raw_after.plot(
        start=start,
        duration=duration,
        n_channels=20,
        scalings=my_scalings,
        show=False,
        title=f"sub-{subject}: cleaned segment",
    )
    out_dir = make_subject_figdir(subject)
    out2 = out_dir / f"sub-{subject}_clean_segment.png"
    fig2.savefig(out2, dpi=150)
    plt.close(fig2)

    print(f"Saved raw vs clean segment plots to {out} and {out2}")

def plot_ica_components(ica, subject: str):
    """Plot spatial topographies for all ICA components."""
    # Because our preprocessing pipeline successfully drops the flawed 
    # EXG channels entirely, we can safely plot the ICA components directly.
    try:
        picks = range(ica.n_components_)
        fig = ica.plot_components(picks=picks, show=False)
        out_dir = make_subject_figdir(subject)
        fig_path = out_dir / f"sub-{subject}_ica_components.png"
        fig.savefig(fig_path, dpi=150)
    except Exception as e:
        print("WARNING: Could not plot ICA components:", e)

def plot_ica_sources(ica, raw, subject: str):
    """
    Saves the time-series of ICA components so we can see blinks and heartbeats.
    """
    ranges = [(0, 15), (15, ica.n_components_)]
    
    for i, (start, stop) in enumerate(ranges):
        # We pick the specific range for each plot
        picks = list(range(start, stop))
        fig = ica.plot_sources(raw, picks=picks, show=False)
        
        # Adjusting suffix to distinguish the two files
        suffix = "0-14" if i == 0 else "15-up"
        out_dir = make_subject_figdir(subject)
        out = out_dir / f"sub-{subject}_ica_sources_{suffix}.png"
        
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"Saved ICA sources ({suffix}) to {out}")

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
            window_title=name,
            time_unit="s",
        )

    ax.set_title(f"sub-{subject}: ERP at {', '.join(picks)}")
    out_dir = make_subject_figdir(subject)
    out = out_dir / f"sub-{subject}_erp.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved ERP figure to {out}")
    
def plot_erp_comparison(evokeds: Dict[str, mne.Evoked], subject: str) -> None:
    """
    Plots the comparison (Symmetry vs Random) specifically for the SPN channels (PO7, PO8).
    """
    # 1. Define the specific channels for the SPN effect
    roi_channels = ['PO7', 'PO8']
    
    # Check if these channels exist in the data
    valid_channels = [ch for ch in roi_channels if ch in evokeds[next(iter(evokeds))].ch_names]
    
    if not valid_channels:
        print(f"SPN channels {roi_channels} not found. Skipping comparison plot.")
        return

    # 2. Define colors for the conditions
    colors = {'random': 'red', 'symmetry': 'blue'}
    
    # 3. Create the comparison plot
    figs = plot_compare_evokeds(
        evokeds,
        picks=valid_channels,
        combine='mean',          
        colors=colors,
        title=f"sub-{subject}: SPN Effect (Mean of {', '.join(valid_channels)})",
        show_sensors='upper right',
        show=False
    )
    
    # 4. Save the figure
    out_dir = make_subject_figdir(subject)
    out = out_dir / f"sub-{subject}_SPN_comparison.png"
    
    # Check if 'figs' is a list or single figure
    if isinstance(figs, list):
        fig_to_save = figs[0]
    else:
        fig_to_save = figs
        
    fig_to_save.savefig(out, dpi=150)
    plt.close(fig_to_save)
    print(f"Saved SPN comparison figure to {out}")


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
        out_dir = make_subject_figdir(subject)
        out = out_dir / f"sub-{subject}_butterfly_{name}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"Saved butterfly figure for '{name}' to {out}")