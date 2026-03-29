"""
Preprocessing module.
Handles filtering, bad channel interpolation, and robust artifact removal.
"""

import mne
import config

def preprocess_raw(raw: mne.io.BaseRaw, subject: str = None) -> mne.io.BaseRaw:
    """
    Apply preprocessing steps including non-EEG channel removal,
    band-pass filtering, and rereferencing.
    """
    raw_proc = raw.copy()

    # ==== 1. SET CHANNEL TYPES ====
    # Explicitly mark EXG as non-EEG to prevent them from being picked below
    # We actively chose to drop the EXG (muscle/EMG) channels 
    # because we found them to be inconsistently labeled(was not labelled specifically) in this dataset. 
    emg_map = {ch: 'emg' for ch in raw_proc.ch_names if 'EXG' in ch}
    raw_proc.set_channel_types(emg_map)

    # ====  2. PICK ONLY EEG ====
    # This removes EXG channels from the current 'raw_proc' object
    raw_proc.pick_types(eeg=True, exclude=[])

    # ==== 3. APPLY MONTAGE ====
    montage = mne.channels.make_standard_montage("biosemi64")
    raw_proc.set_montage(montage, on_missing="ignore")

    # ==== 4. MARK & INTERPOLATE explicitly mapped bad channels ====
    if subject and subject in config.BAD_CHANNELS_MAP:
        raw_proc.info['bads'] = config.BAD_CHANNELS_MAP[subject]
        if raw_proc.info['bads']:
            raw_proc.interpolate_bads(reset_bads=True)

    # ==== 5. FILTER ====
    # We upgraded the original authors' 25 Hz low-pass filter to a 
    # strict 0.5 - 30.0 Hz band-pass filter. We made this choice to effectively 
    # remove slow-wave drifts and sweat artifacts while preserving the core 
    # frequencies required to accurately measure the SPN effect.
    raw_proc.filter(l_freq=config.L_FREQ, h_freq=config.H_FREQ)

    # ==== 6. RESAMPLE ====
    if hasattr(config, "RESAMPLE_FREQ") and config.RESAMPLE_FREQ is not None:
        current_sfreq = raw_proc.info["sfreq"]
        if current_sfreq != config.RESAMPLE_FREQ:
            print(f"Resampling data from {current_sfreq} Hz to {config.RESAMPLE_FREQ} Hz...")
            raw_proc.resample(config.RESAMPLE_FREQ)

    raw_proc.set_eeg_reference("average")

    return raw_proc