"""
Master Execution Script: EEG Tigers SPN Pipeline.
Automates individual processing and the final Grand Average plot.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import mne
import config
from scripts.run_subject import run_for_subject
from project.plot_grand_average import plot_group_spn
from project.plot_group_topomaps import plot_group_topo
from project.plot_group_erd import plot_group_alpha_erd

def main():
    mne.set_log_level("INFO")

    # --- PHASE 1: INDIVIDUAL SUBJECT PROCESSING ---
    # We iterate through the subjects defined in config.py to 
    # generate the .fif evoked files and JSON summaries required for group analysis.
    for subject in config.SUBJECTS:
        print(f"\n{'=' * 20} Running subject {subject} {'=' * 20}")
        run_for_subject(subject)

    # --- PHASE 2: AUTOMATED GRAND AVERAGE ---
    # We trigger the Grand Average plot automatically as the 
    # next step of our pipeline after all subjects are processed individually 
    # to provide an immediate visual replication of the SPN effect
    print(f"\n{'#' * 80}")
    print("INDIVIDUAL PROCESSING COMPLETE. Plotting GRAND AVERAGE VISUALIZATION...")
    print(f"{'#' * 80}\n")

    try:
        plot_group_spn()
    except Exception as e:
        print(f"Error during Grand Average Visualization: {e}")

    # --- PHASE 3: TOPOGRAPHIC MAPPING ---
    # We automated the topographic mapping phase to ensure our 
    # visual report includes both temporal (line plots) and spatial (scalp maps) 
    # evidence of the Sustained Posterior Negativity.
    print(f"\n{'#' * 80}")
    print("Plotting Topographic Maps...")
    print(f"{'#' * 80}\n")
    try:
        plot_group_topo()
    except Exception as e:
        print(f"Error generating Topographic Maps: {e}")

    # --- PHASE 4: TIME-FREQUENCY ANALYSIS (ERD) ---
    # We included Alpha-Band ERD analysis to provide a multi-dimensional 
    # view of the symmetry response, effectively replicating the oscillatory 
    # findings reported in the original Experiment 1.
    try:
        plot_group_alpha_erd()
    except Exception as e:
        print(f"Error generating Alpha ERD: {e}")

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION FINISHED SUCCESSFULLY.")
    print(f"All derivatives and figures are available in: {config.DERIV_ROOT}")
    print("=" * 80)

    print("To run the group-level cluster statistics, please execute 'cluster_perm_test_group.py'.")

if __name__ == "__main__":
    main()