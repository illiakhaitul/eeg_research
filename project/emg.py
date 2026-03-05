import mne
import numpy as np
from typing import Dict
import pandas as pd

import config


def compute_emg_zscore(epochs: mne.Epochs) -> pd.DataFrame:
    """
    Process EXG5 (ZM) and EXG7 (CS) channels to calculate Z-scored EMG activity 
    for each trial and condition, following the authors' general methodology:
    1. Filter the EMG channels (High-pass).
    2. Rectify the signal (absolute value).
    3. Calculate Z-score based on the baseline period.
    4. Average the Z-score across the post-stimulus period (e.g., 500ms bins).
    
    Returns a DataFrame of Z-scores, ready for statistical analysis.
    """
    
    # 1. Define EMG channels based on resolved mapping in config.py
    emg_channels = {
        'ZM': config.EMG_ZM_CH,
        'CS': config.EMG_CS_CH,
    }
    
    # Check if channels are present in epochs
    present_emg_channels = {
        name: ch for name, ch in emg_channels.items() if ch in epochs.ch_names
    }
    if not present_emg_channels:
        print("WARNING: EMG channels not found in epochs. Skipping EMG analysis.")
        return pd.DataFrame()

    # 2. Filter (20 Hz High-pass) - operate on a copy of epochs
    epochs_emg = epochs.copy().pick_channels(list(present_emg_channels.values()))
    epochs_emg.filter(l_freq=config.EMG_HPF, h_freq=None, fir_design='firwin', verbose=False)
    
    # 3. Rectify (Absolute Value)
    emg_data = np.abs(epochs_emg.get_data())  # Shape: (n_epochs, n_channels, n_times)
    
    # 4. Calculate Z-score
    # Find baseline indices
    tmin_idx, tmax_idx = [
        np.argmin(np.abs(epochs_emg.times - t)) for t in config.BASELINE
    ]

    # Calculate mean and std of the baseline period for each epoch
    baseline_data = emg_data[:, :, tmin_idx:tmax_idx]
    baseline_mean = np.mean(baseline_data, axis=2, keepdims=True)
    baseline_std = np.std(baseline_data, axis=2, keepdims=True)
    
    # Avoid division by zero
    baseline_std[baseline_std == 0] = 1e-6
    
    # Z-score normalization
    z_scored_emg = (emg_data - baseline_mean) / baseline_std

    # 5. Average Z-scores over the post-stimulus period
    # We take the mean from t=0 (approx tmax_idx of baseline) to end
    post_stim_data = z_scored_emg[:, :, tmax_idx:]
    emg_means = np.mean(post_stim_data, axis=2)
    
    # Create the results DataFrame
    results_df = pd.DataFrame(
        data=emg_means,
        columns=list(present_emg_channels.keys())
    )
    
    # Create Reverse Mapping for Event Names ---
    # config.EVENT_ID is {'random': 1, 'symmetry': 3}
    # We need {1: 'random', 3: 'symmetry'} to look up names by integer code.
    id_to_ident = {v: k for k, v in config.EVENT_ID.items()}
    
    # Map the integer event codes (from epochs.events column 2) to names
    results_df['condition'] = [
        id_to_ident[event_code] for event_code in epochs_emg.events[:, 2]
    ]
    
    results_df['trial_number'] = np.arange(len(epochs_emg)) + 1
    
    print(f"Computed Z-scored EMG activity for {len(results_df)} trials.")
    return results_df


def save_emg_results(df: pd.DataFrame, subject: str):
    """Save the final EMG DataFrame to derivatives."""
    if not df.empty:
        fname = config.DERIV_ROOT / f"sub-{subject}_emg_zscores.csv"
        df.to_csv(fname, index=False)
        print(f"Saved EMG Z-scores to {fname}")

def compute_and_save_emg_summary(df: pd.DataFrame, subject: str) -> None:
    """
    Calculates the mean EMG response per condition and saves it to a summary CSV.
    """
    if df.empty:
        print("EMG DataFrame is empty. Skipping summary.")
        return

    # Group by condition and calculate the mean for ZM and CS
    # We select only numeric columns to avoid errors
    summary_df = df.groupby('condition')[['ZM', 'CS']].mean().reset_index()
    
    # Calculate the Difference (Symmetry - Random) for quick inspection
    # This involves a bit of pivoting
    try:
        diff_val_zm = summary_df.loc[summary_df['condition'] == 'symmetry', 'ZM'].values[0] - \
                      summary_df.loc[summary_df['condition'] == 'random', 'ZM'].values[0]
        
        diff_val_cs = summary_df.loc[summary_df['condition'] == 'symmetry', 'CS'].values[0] - \
                      summary_df.loc[summary_df['condition'] == 'random', 'CS'].values[0]
        
        print("\n" + "="*40)
        print(f"EMG SUMMARY FOR SUB-{subject}")
        print("="*40)
        print(summary_df)
        print("-" * 40)
        print(f"ZM Difference (Sym - Rand): {diff_val_zm:.4f} " + ("(CORRECT)" if diff_val_zm > 0 else "(REVERSED)"))
        print(f"CS Difference (Sym - Rand): {diff_val_cs:.4f}")
        print("="*40 + "\n")
        
    except IndexError:
        print("Could not calculate differences (missing conditions).")

    # Save to CSV
    out_file = config.DERIV_ROOT / f"sub-{subject}_emg_summary.csv"
    summary_df.to_csv(out_file, index=False)
    print(f"Saved EMG summary stats to {out_file}")