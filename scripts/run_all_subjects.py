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

def main():
    mne.set_log_level("INFO")

    for subject in config.SUBJECTS:
        print(f"\n{'=' * 20} Running subject {subject} {'=' * 20}")
        run_for_subject(subject)

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

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION FINISHED SUCCESSFULLY.")
    print(f"All derivatives and figures are available in: {config.DERIV_ROOT}")
    print("=" * 80)

    print("To run the group-level cluster statistics, please execute 'cluster_perm_test_group.py'.")

if __name__ == "__main__":
    main()