"""
Group-level Time-Frequency (ERD) Visualization module.
Analyzes alpha-band desynchronization to replicate Figure 3 of the original study.
Uses modern MNE .compute_tfr() API.
"""

import sys
from pathlib import Path

# Ensure the root path is established for local imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import mne
import numpy as np
import matplotlib.pyplot as plt
import config

def plot_group_alpha_erd():
    """
    Computes and plots the Grand Average Time-Frequency representation (ERD).
    
    We utilize the modern .compute_tfr(method="morlet") API to 
    analyze the 10-14 Hz alpha band. Replicating Makin et al. (2012), we 
    visualize the Event-Related Desynchronization (ERD) over posterior 
    electrodes, providing a frequency-domain proof of symmetry processing.
    """
    print("=" * 80)
    print("Generating Grand Average Alpha-Band ERD (Modern API)")
    print("=" * 80)

    tfr_list = []

    # 1. Collect and compute TFR for each subject
    for subject in config.SUBJECTS:
        out_dir = config.get_subject_deriv_dir(subject)
        epo_file = out_dir / f"sub-{subject}_epo.fif"
        
        if not epo_file.exists():
            continue
            
        epochs = mne.read_epochs(epo_file, preload=True, verbose=False)
        
        # Define frequencies for Morlet Wavelets
        freqs = np.arange(5, 31, 1)  # 5Hz to 30Hz
        n_cycles = freqs / 2.0       
        
        # Compute Power (TFR) using the modern API
        tfr = epochs.compute_tfr(
            method="morlet", 
            freqs=freqs, 
            n_cycles=n_cycles, 
            average=True, 
            picks=config.SPN_ROI_MAIN
        )
        tfr_list.append(tfr)

    if not tfr_list:
        raise RuntimeError("No epoch files found. Run run_all_subjects.py first.")

    # 2. Compute Grand Average TFR
    grand_avg_tfr = mne.grand_average(tfr_list)

    # 3. Plot the Spectrogram
    # We apply a log-ratio baseline (dB) to isolate the 
    # desynchronization (ERD) occurring post-stimulus.
    fig, ax = plt.subplots(figsize=(8, 5))
    grand_avg_tfr.plot(
        baseline=config.BASELINE, 
        mode='logratio', 
        title=f"Grand Average Alpha ERD (10-14 Hz) at {', '.join(config.SPN_ROI_MAIN)}",
        axes=ax,
        show=False,
        combine='mean'
    )

    # 4. Save to the group figures directory
    out_dir = config.get_group_fig_dir()
    out_path = out_dir / "Grand_Average_Alpha_ERD_Spectrogram.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Success! ERD spectrogram saved to {out_path}")

if __name__ == "__main__":
    mne.set_log_level("WARNING")
    plot_group_alpha_erd()