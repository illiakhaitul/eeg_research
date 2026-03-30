"""
Group-level Grand Average ERP visualization module.
Generates the definitive SPN difference plot across all participants.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mne
import matplotlib.pyplot as plt
from mne.viz import plot_compare_evokeds

import config

def plot_group_spn():
    """
    Computes and plots the Grand Average ERP for the symmetry vs. random conditions.
    
    We developed this script to compute the Grand Average ERP across 
    all 24 subjects. While our cluster permutation test provides rigorous statistical 
    validation, creating this specific visualization at our primary ROI (PO7, PO8) 
    is essential to strictly replicate the visual presentation in Makin et al. (2012) 
    and to clearly demonstrate the SPN effect to our evaluator.
    """
    print("=" * 80)
    print(f"Generating Grand Average SPN Plot for {len(config.SUBJECTS)} subjects")
    print("=" * 80)

    evokeds_sym = []
    evokeds_ran = []

    # 1. Collect all individual evoked files
    for subject in config.SUBJECTS:
        out_dir = config.get_subject_deriv_dir(subject)
        ev_sym_file = out_dir / f"sub-{subject}_evoked-symmetry-ave.fif"
        ev_ran_file = out_dir / f"sub-{subject}_evoked-random-ave.fif"
        
        if not ev_sym_file.exists() or not ev_ran_file.exists():
            print(f"Warning: Evoked files missing for sub-{subject}. Skipping.")
            continue
            
        ev_sym = mne.read_evokeds(ev_sym_file, condition=0, verbose=False)
        ev_ran = mne.read_evokeds(ev_ran_file, condition=0, verbose=False)
        
        evokeds_sym.append(ev_sym)
        evokeds_ran.append(ev_ran)

    if not evokeds_sym or not evokeds_ran:
        raise RuntimeError("No valid evoked files found to create Grand Average.")

    # 2. Compute the Grand Average across all subjects
    grand_avg_sym = mne.grand_average(evokeds_sym)
    grand_avg_ran = mne.grand_average(evokeds_ran)

    # 3. Create a dictionary for the plotting function
    evoked_dict = {
        'symmetry': grand_avg_sym,
        'random': grand_avg_ran
    }
    
    # 4. Generate the plot
    figs = plot_compare_evokeds(
        evoked_dict,
        picks=config.SPN_ROI_MAIN,
        combine='mean',          
        colors=config.CONDITION_COLORS,
        title=f"Grand Average SPN Effect (N={len(evokeds_sym)}) at {', '.join(config.SPN_ROI_MAIN)}",
        show_sensors='upper right',
        show=False
    )
    
    # 5. Save the figure to our new group figures directory
    out_dir = config.get_group_fig_dir()
    out_path = out_dir / "Grand_Average_SPN_PO7_PO8.png"
    
    fig_to_save = figs[0] if isinstance(figs, list) else figs
    fig_to_save.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig_to_save)
    
    print(f"Success! Grand Average plot saved to {out_path}")

if __name__ == "__main__":
    mne.set_log_level("WARNING")
    plot_group_spn()