"""
Group-level Grand Average Topographic Visualization module.
Generates spatial scalp maps to demonstrate the posterior distribution of the SPN.
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

def plot_group_topo():
    """
    Computes and plots Grand Average Topographic maps for Symmetry vs Random.
    
    We developed this script to visually demonstrate the spatial 
    distribution of the SPN effect across the scalp. By plotting the difference 
    (Symmetry - Random), we provide spatial evidence that the regularity-sensitive 
    networks are localized in the extrastriate visual cortex, consistent with 
    the LORETA findings in the paper.
    """
    print("=" * 80)
    print("Generating Grand Average Topographic Maps")
    print("=" * 80)

    evokeds_diff = []

    # 1. Collect all individual difference waves
    for subject in config.SUBJECTS:
        out_dir = config.get_subject_deriv_dir(subject)
        ev_sym_file = out_dir / f"sub-{subject}_evoked-symmetry-ave.fif"
        ev_ran_file = out_dir / f"sub-{subject}_evoked-random-ave.fif"
        
        if not ev_sym_file.exists() or not ev_ran_file.exists():
            continue
            
        ev_sym = mne.read_evokeds(ev_sym_file, condition=0, verbose=False)
        ev_ran = mne.read_evokeds(ev_ran_file, condition=0, verbose=False)
        
        # Calculate difference wave: Symmetry - Random
        # We explicitly compute the difference to isolate the 
        # Sustained Posterior Negativity (SPN) from general visual processing.
        diff = mne.combine_evoked([ev_sym, ev_ran], weights=[1, -1])
        evokeds_diff.append(diff)

    if not evokeds_diff:
        raise RuntimeError("No evoked files found. Run run_all_subjects.py first.")

    # 2. Compute Grand Average Difference
    grand_avg_diff = mne.grand_average(evokeds_diff)

    # 3. Plot Topomaps for each defined time window
    # We iterate through our time windows to show the spatial evolution 
    # of the SPN, replicating the mapping approach in the original study.
    for t_start, t_end in config.TOPO_TIME_WINDOWS:
        # Calculate center for plotting
        t_mid = (t_start + t_end) / 2
        
        fig = grand_avg_diff.plot_topomap(
            times=t_mid,
            average=t_end - t_start,
            ch_type='eeg',
            show=False,
            contours=0,
            sensors=True,
            res=128,
            colorbar=True
        )
        
        # setting the title via Matplotlib to avoid API errors
        fig.suptitle(f"SPN Difference (Sym-Ran): {int(t_start*1000)}-{int(t_end*1000)} ms", fontsize=12)
        
        # 4. Save to the group figures directory
        out_dir = config.get_group_fig_dir()
        out_path = out_dir / f"Grand_Average_Topo_{int(t_start*1000)}_{int(t_end*1000)}ms.png"
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Success! Topographic map saved to {out_path}")

if __name__ == "__main__":
    mne.set_log_level("WARNING")
    plot_group_topo()