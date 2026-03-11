# we can delete this file now since i have created other two files for better structure.

from pathlib import Path
import sys
import mne

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import config
from project.io import load_raw
from project.preprocessing import preprocess_raw
from project.ica import fit_ica, apply_ica
from project.epochs import make_epochs
from project.erp import compute_evokeds, save_evokeds
from project import viz, emg, stest
import matplotlib.pyplot as plt


""" ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT)) """

def run_for_subject(subject: str) -> None:
    print("=" * 80)
    print(f"Running pipeline for sub-{subject}")
    print("=" * 80)

    # Load raw BIDS data
    raw = load_raw(subject)
    print(raw)
    """ raw.plot(block=True) """

    # Preprocess: band-pass, notch, reref
    raw_filt = preprocess_raw(raw, subject=subject)
    
    # Fit ICA
    ica = fit_ica(raw_filt, subject)

    viz.plot_ica_components(ica, subject)
    viz.plot_ica_sources(ica, raw_filt, subject)

    # Apply ICA using the Mapping in config.py
    raw_clean = apply_ica(raw_filt, ica, subject=subject)

    # Create epochs
    epochs = make_epochs(raw_clean, subject)
    
    epochs.plot_drop_log()

    # Compute ERPs
    evokeds, metrics = compute_evokeds(epochs,subject)
    save_evokeds(evokeds, subject)
    
    # stest.run_cluster_permutation_test(
    #     epochs,
    #     subject,
    #     condition_a="random",
    #     condition_b="symmetry",
    #     picks=config.ERP_CHANNELS,   # or None for all EEG channels
    #     n_permutations=1000,
    #     alpha=0.05,
    # )

    # Compute EMG Z-scores
    emg_df = emg.compute_emg_zscore(epochs)
    emg.save_emg_results(emg_df, subject)
    emg.compute_and_save_emg_summary(emg_df, subject)

    viz.plot_psd_before_after(raw, raw_filt, subject)
    viz.plot_raw_vs_clean(raw, raw_clean, subject)
    viz.plot_ica_components(ica, subject)
    viz.plot_erp(evokeds, subject)
    viz.plot_erp_comparison(evokeds, subject)
    viz.plot_butterfly(evokeds, subject)

    print(f"Finished pipeline for sub-{subject}\n")

def main():
    mne.set_log_level("INFO")
    for subject in config.SUBJECTS:
        run_for_subject(subject)


if __name__ == "__main__":
    main()