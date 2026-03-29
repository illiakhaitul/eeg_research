"""
Main pipeline execution script for individual subjects.
To run for a specific subject, use the command line:
python run_subject.py --subject 0XX 
where 0XX is the subject ID, e.g. "001", "005", etc.
Therefore example command looks like: python run_subject.py --subject 005
This script will execute the entire preprocessing and analysis pipeline for the specified subject.
"""

from pathlib import Path
import sys
import argparse
import mne

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Refer step 7: This import is necessary to access ERP_CHANNELS in step 7 if uncommented to analyze cluster permutation test per subject which we did for reference for some individual subjects.
import config 
from project.io import load_raw
from project.preprocessing import preprocess_raw
from project.ica import fit_ica, apply_ica
from project.epochs import make_epochs
from project.erp import compute_evokeds, save_evokeds
from project.summary import save_subject_summary
from project import viz, cluster_perm_test_subject # Refer step 7: We import this module to run the cluster permutation test at the individual subject level, which is a more exploratory analysis to identify potential SPN effects in each subject before we do the rigorous group-level test in cluster_perm_test_group.py.


def run_for_subject(subject: str) -> None:
    print("=" * 80)
    print(f"Running pipeline for sub-{subject}")
    print("=" * 80)

    # 1) Load raw BIDS data
    raw = load_raw(subject)
    print(raw)

    # 2) Preprocess: channel rejection, band-pass, resample, rereference
    raw_filt = preprocess_raw(raw, subject=subject)

    # 3) Fit ICA and inspect components
    ica = fit_ica(raw_filt, subject)

    # 4) Apply ICA using the Mapping in config.py
    # This function checks config.ICA_EXCLUDE_MAP for the subject ID.
    # We implemented manual, targeted exclusion of specific IC components 
    # (via our config map) to ensure we precisely removed biological artifacts 
    # (blinks, cardiac) while strictly preserving the true cortical SPN generators.
    raw_clean = apply_ica(raw_filt, ica, subject=subject)

    # 5) Create epochs
    epochs = make_epochs(raw_clean, subject)

    # 6) Compute ERPs
    evokeds, metrics = compute_evokeds(epochs, subject)
    save_evokeds(evokeds, subject)

    if metrics is not None:
        save_subject_summary(
            subject=subject,
            symmetry_mean=metrics["symmetry_mean_uv"],
            random_mean=metrics["random_mean_uv"],
            spn_mean=metrics["spn_mean_uv"],
        )
    
    # 7) Cluster permutation test for SPN (symmetry vs random)
    # cluster_perm_test_subject.run_cluster_permutation_test(
    #     epochs,
    #     subject,
    #     condition_a="random",
    #     condition_b="symmetry",
    #     picks=config.ERP_CHANNELS,
    #     n_permutations=1000,
    #     alpha=0.05,
    # )

    # 8) Figures for analysis
    viz.plot_psd_before_after(raw, raw_filt, subject)
    viz.plot_raw_vs_clean(raw, raw_clean, subject)
    viz.plot_ica_components(ica, subject)
    viz.plot_ica_sources(ica, raw_filt, subject)
    viz.plot_erp(evokeds, subject)
    viz.plot_erp_comparison(evokeds, subject)
    viz.plot_butterfly(evokeds, subject)

    print(f"Finished pipeline for sub-{subject}\n")

def main():
    parser = argparse.ArgumentParser(description="Run EEG pipeline for one subject")
    parser.add_argument("--subject", required=True, help='Subject ID, e.g. "001"')
    args = parser.parse_args()

    mne.set_log_level("INFO")
    run_for_subject(args.subject)


if __name__ == "__main__":
    main()