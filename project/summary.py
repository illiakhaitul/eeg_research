"""
Summary logging module.
Handles exporting subject-level metrics to JSON for aggregate analysis.
"""
import json
from pathlib import Path
import config


def save_subject_summary(
    subject: str,
    symmetry_mean: float,
    random_mean: float,
    spn_mean: float,
):
    """
    Save key SPN metrics and preprocessing metadata to a structured JSON file.
    """
    out_dir = config.get_subject_deriv_dir(subject)
    summary_path = out_dir / f"sub-{subject}_summary.json"

    summary = {
        "subject": subject,
        "bad_channels": config.BAD_CHANNELS_MAP.get(subject, []),
        "ica_exclude": config.ICA_EXCLUDE_MAP.get(subject, []),
        "spn_roi_main": config.SPN_ROI_MAIN,
        "symmetry_mean_uv": float(symmetry_mean),
        "random_mean_uv": float(random_mean),
        "spn_mean_uv": float(spn_mean),
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved subject summary to {summary_path}")