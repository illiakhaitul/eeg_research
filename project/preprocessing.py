import mne

import config

def preprocess_raw(raw: mne.io.BaseRaw, subject: str = None) -> mne.io.BaseRaw:
    raw_proc = raw.copy()

    # Set channel types
    emg_map = {ch: 'emg' for ch in raw_proc.ch_names if 'EXG' in ch}
    raw_proc.set_channel_types(emg_map)

    # Only EEG
    raw_proc.pick_types(eeg=True, exclude=[])

    # Apply montage
    montage = mne.channels.make_standard_montage("biosemi64")
    raw_proc.set_montage(montage, on_missing="ignore")

    if subject and subject in config.BAD_CHANNELS_MAP:
        raw_proc.info['bads'] = config.BAD_CHANNELS_MAP[subject]
        raw_proc.interpolate_bads(reset_bads=True)

    # Filter
    raw_proc.filter(l_freq=config.L_FREQ, h_freq=config.H_FREQ)

    # Resample
    if hasattr(config, "RESAMPLE_FREQ") and config.RESAMPLE_FREQ is not None:
        current_sfreq = raw_proc.info["sfreq"]
        if current_sfreq != config.RESAMPLE_FREQ:
            print(f"Resampling data from {current_sfreq} Hz to {config.RESAMPLE_FREQ} Hz...")
            raw_proc.resample(config.RESAMPLE_FREQ)

    raw_proc.set_eeg_reference("average")

    return raw_proc