"""
Group-level cluster permutation statistical analysis module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import numpy as np
import mne
from mne.stats import spatio_temporal_cluster_1samp_test
from mne.channels import find_ch_adjacency

import config

def run_group_cluster_test(alpha=config.CLUSTER_ALPHA, n_permutations=config.CLUSTER_PERMUTATIONS):
    """
    We upgraded the original authors' methodology from standard ANOVAs 
    in pre-selected time windows to a rigorous Spatio-Temporal Cluster 
    Permutation Test. We chose this approach because it elegantly controls for the 
    multiple comparisons problem across both space (channels) and time (ms), giving 
    us highly robust group-level inferences without overly conservative penalties.
    """
    print("=" * 80)
    print(f"Running GROUP-LEVEL cluster permutation test across {len(config.SUBJECTS)} subjects")
    print("=" * 80)

    # ==== 1. Initialize list to store the difference arrays ====
    diff_data = []
    
    # We use the ROI(Region of Interest) defined in config to make the test statistically powerful
    picks_roi = config.ERP_CHANNELS 
    times = None
    info = None

    # ==== 2. Loops through all subjects and extract the difference wave ====
    for subject in config.SUBJECTS:
        out_dir = config.get_subject_deriv_dir(subject)
        ev_sym_file = out_dir / f"sub-{subject}_evoked-symmetry-ave.fif"
        ev_ran_file = out_dir / f"sub-{subject}_evoked-random-ave.fif"
        
        # Ensures files exist
        if not ev_sym_file.exists() or not ev_ran_file.exists():
            print(f"Warning: Evoked files missing for sub-{subject}. Skipping.")
            continue
            
        # Load evokeds
        ev_sym = mne.read_evokeds(ev_sym_file, condition=0, verbose=False)
        ev_ran = mne.read_evokeds(ev_ran_file, condition=0, verbose=False)
        
        # Calculate the difference wave (Symmetry - Random)
        diff = mne.combine_evoked([ev_sym, ev_ran], weights=[1, -1])
        
        # Keep only the channels in our ROI
        picks_available = [ch for ch in picks_roi if ch in diff.ch_names]
        if not picks_available:
            print(f"Warning: No ROI channels found for sub-{subject}. Skipping.")
            continue
        diff.pick(picks_available)
        
        # Save times and info from the first subject to use later
        if times is None:
            times = diff.times
            info = diff.info
            
        # Extract data: shape (n_channels, n_times)
        data = diff.get_data()
        
        # Transpose to shape expected by the stats function: (n_times, n_channels)
        data_t = np.transpose(data)
        diff_data.append(data_t)

    # ==== 3. Convert list to 3D numpy array: (n_subjects, n_times, n_channels) ====
    if not diff_data:
        raise RuntimeError("No subjects had valid evoked files/channels for group test.")
    X = np.array(diff_data)
    print(f"Data array shape for stats: {X.shape} (Subjects, Times, Channels)")

    # ==== 4. Generate the spatial adjacency matrix for our specific ROI ====
    adjacency, ch_names = find_ch_adjacency(info, ch_type="eeg")

    # ==== 5. Run the 1-sample cluster permutation test ====
    # We explicitly locked the random seed here to guarantee that our 
    # permutations and statistical p-values are reproducible.
    print("Computing clusters...")
    T_obs, clusters, cluster_p_values, H0 = spatio_temporal_cluster_1samp_test(
        X,
        adjacency=adjacency,
        n_permutations=n_permutations,
        tail=0,
        n_jobs=-1,
        out_type="mask",
        seed=97,
    )

    # ==== 6. Identify significant clusters ====
    significant_idx = np.where(cluster_p_values < alpha)[0]
    
    print("\n--- STATISTICAL RESULTS ---")
    print(f"Total clusters found: {len(clusters)}")
    print(f"Significant clusters (p < {alpha}): {len(significant_idx)}")

    # ==== 7. Save results for the final report ====
    out_dir = config.DERIV_ROOT / "stats"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "group_level_cluster_test_summary.txt"
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("GROUP-LEVEL SPATIO-TEMPORAL CLUSTER PERMUTATION TEST\n")
        f.write("=" * 60 + "\n")
        f.write(f"N Subjects: {X.shape[0]}\n")
        f.write(f"ROI Channels: {ch_names}\n")
        f.write(f"Permutations: {n_permutations}\n")
        f.write(f"Alpha Level: {alpha}\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total clusters identified: {len(clusters)}\n")
        f.write(f"Significant clusters: {len(significant_idx)}\n\n")
        
        # Detail the exact timing and location of the significant clusters
        for i in significant_idx:
            c_mask = clusters[i] # Boolean mask of shape (n_times, n_channels)
            
            # Find the time indices where this cluster is active
            time_indices = np.where(c_mask.any(axis=1))[0]
            t_start = times[time_indices[0]] * 1000 # Convert to ms
            t_end = times[time_indices[-1]] * 1000  # Convert to ms
            
            # Find the channels involved in this cluster
            chan_indices = np.where(c_mask.any(axis=0))[0]
            sig_chans = [ch_names[idx] for idx in chan_indices]
            
            cluster_info = (
                f"Cluster #{i} | p-value = {cluster_p_values[i]:.5f}\n"
                f"  Time Window: {t_start:.1f} ms to {t_end:.1f} ms\n"
                f"  Channels involved: {', '.join(sig_chans)}\n"
            )
            print(cluster_info)
            f.write(cluster_info + "\n")

    print(f"Group statistical summary saved to {summary_path}")

if __name__ == "__main__":
    mne.set_log_level("WARNING")
    run_group_cluster_test()