from pathlib import Path
from typing import Optional

import numpy as np
import mne
from mne.stats import spatio_temporal_cluster_test
from mne.channels import find_ch_adjacency

import config


def run_cluster_permutation_test(
    epochs: mne.Epochs,
    subject: str,
    condition_a: str = "random",
    condition_b: str = "symmetry",
    picks: Optional[list[str]] = None,
    n_permutations: int = 1000,
    alpha: float = 0.05,
):
    """
    Run cluster-based permutation test for ERP differences between two conditions.

    Parameters
    ----------
    epochs : mne.Epochs
        Epoched EEG data.
    subject : str
        Subject ID.
    condition_a : str
        First condition name.
    condition_b : str
        Second condition name.
    picks : list[str] | None
        EEG channels to include. If None, use all EEG channels.
    n_permutations : int
        Number of permutations.
    alpha : float
        Significance threshold for reporting clusters.

    Returns
    -------
    results : dict
        Dictionary with test results.
    """

    print("=" * 80)
    print(f"Running cluster permutation test for sub-{subject}")
    print(f"Conditions: {condition_a} vs {condition_b}")
    print("=" * 80)

    # 1) Keep only EEG channels
    if picks is None:
        picks = mne.pick_types(epochs.info, eeg=True, eog=False, exclude="bads")
    else:
        picks = mne.pick_channels(epochs.ch_names, include=picks)

    if len(picks) == 0:
        raise RuntimeError("No EEG channels available for cluster test.")

    # 2) Extract data for both conditions
    epochs_a = epochs[condition_a].copy().pick(picks)
    epochs_b = epochs[condition_b].copy().pick(picks)

    X_a = epochs_a.get_data()  # shape: (n_epochs, n_channels, n_times)
    X_b = epochs_b.get_data()

    # 3) Reorder to shape expected by spatio_temporal_cluster_test:
    #    (n_epochs, n_times, n_channels)
    X_a = np.transpose(X_a, (0, 2, 1))
    X_b = np.transpose(X_b, (0, 2, 1))

    # 4) Channel adjacency matrix
    adjacency, ch_names = find_ch_adjacency(epochs_a.info, ch_type="eeg")

    # 5) Run test
    X = [X_a, X_b]

    T_obs, clusters, cluster_p_values, H0 = spatio_temporal_cluster_test(
        X,
        adjacency=adjacency,
        n_permutations=n_permutations,
        threshold=None,
        tail=0,           # two-sided
        n_jobs=1,
        out_type="mask",
    )

    # 6) Find significant clusters
    significant_idx = np.where(cluster_p_values < alpha)[0]

    print(f"Number of clusters found: {len(clusters)}")
    print(f"Number of significant clusters (p < {alpha}): {len(significant_idx)}")

    for i in significant_idx:
        print(f"  Cluster {i}: p = {cluster_p_values[i]:.5f}")

    # 7) Save numeric results
    out_dir = config.DERIV_ROOT / "stats"
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / f"sub-{subject}_T_obs.npy", T_obs)
    np.save(out_dir / f"sub-{subject}_cluster_p_values.npy", cluster_p_values)

    # Save summary text
    summary_path = out_dir / f"sub-{subject}_cluster_test_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Subject: sub-{subject}\n")
        f.write(f"Conditions: {condition_a} vs {condition_b}\n")
        f.write(f"n_permutations: {n_permutations}\n")
        f.write(f"alpha: {alpha}\n")
        f.write(f"n_clusters: {len(clusters)}\n")
        f.write(f"n_significant_clusters: {len(significant_idx)}\n")
        for i in significant_idx:
            f.write(f"Cluster {i}: p = {cluster_p_values[i]:.6f}\n")

    print(f"Saved cluster test summary to {summary_path}")

    return {
        "T_obs": T_obs,
        "clusters": clusters,
        "cluster_p_values": cluster_p_values,
        "significant_idx": significant_idx,
        "adjacency": adjacency,
        "channel_names": ch_names,
    }