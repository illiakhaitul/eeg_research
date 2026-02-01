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
from project import viz


""" ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT)) """

def run_for_subject(subject: str) -> None:
    print("=" * 80)
    print(f"Running pipeline for sub-{subject}")
    print("=" * 80)

    # 1) Load raw BIDS data
    raw = load_raw(subject)
    print(raw)

    # 2) Preprocess: band-pass, notch, reref
    raw_filt = preprocess_raw(raw)

    # 3) Fit ICA and inspect components
    ica = fit_ica(raw_filt, subject)

    # --- IMPORTANT STEP FOR YOU (outside of script) -----------------------
    # At this point you should:
    #   1) run this script once,
    #   2) open the saved ICA components figure,
    #   3) decide which components are artefacts (e.g. [0, 1]),
    #   4) put their indices into config.ICA_EXCLUDE.
    # For Milestone 3 you can keep ICA_EXCLUDE=[] or manually fill it.
    # ----------------------------------------------------------------------

    # 4) Apply ICA
    raw_clean = apply_ica(raw_filt, ica, exclude=config.ICA_EXCLUDE)

    # 5) Create epochs
    epochs = make_epochs(raw_clean, subject)

    # 6) Compute ERPs
    evokeds = compute_evokeds(epochs)
    save_evokeds(evokeds, subject)

    # 7) Figures for Milestone 3
    viz.plot_psd_before_after(raw, raw_filt, subject)
    viz.plot_raw_vs_clean(raw, raw_clean, subject)
    viz.plot_ica_components(ica, subject)
    viz.plot_erp(evokeds, subject)
    viz.plot_butterfly(evokeds, subject)

    print(f"Finished pipeline for sub-{subject}\n")


def main():
    mne.set_log_level("INFO")
    for subject in config.SUBJECTS:
        run_for_subject(subject)


if __name__ == "__main__":
    main()