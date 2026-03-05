import mne

import config


def preprocess_raw(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """
    Apply band-pass filtering, notch filter, and rereferencing.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Original raw EEG data (preload=True).

    Returns
    -------
    raw_proc : mne.io.BaseRaw
        Preprocessed copy of the data.
    """
    raw_proc = raw.copy()

    # 1) Band-pass filter (your change vs authors)
    raw_proc.filter(
        l_freq=config.L_FREQ,
        h_freq=config.H_FREQ,
        fir_design="firwin",
        verbose=True,
    )

    # 2) Notch filter for line noise (50 Hz)
    if config.NOTCH_FREQS:
        raw_proc.notch_filter(
            freqs=config.NOTCH_FREQS,
            fir_design="firwin",
            verbose=True,
        )
        
    if hasattr(config, 'RESAMPLE_FREQ') and config.RESAMPLE_FREQ is not None:
        print(f"Resampling data to {config.RESAMPLE_FREQ} Hz...")
        raw_proc.resample(config.RESAMPLE_FREQ)

    # 3) Set EEG average reference
    raw_proc.set_eeg_reference("average", verbose=True)

    # 4) (Optional) you can add automatic bad channel detection here.
    # For Milestone 3 we keep it simple and rely on raw_proc.info['bads'].

    return raw_proc