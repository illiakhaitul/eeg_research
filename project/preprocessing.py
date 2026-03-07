import mne

import config

def preprocess_raw(raw: mne.io.BaseRaw, subject: str = None) -> mne.io.BaseRaw:
    raw_proc = raw.copy()

    # 1. SET CHANNEL TYPES
    # Explicitly mark EXG as non-EEG to prevent them from being picked below
    emg_map = {ch: 'emg' for ch in raw_proc.ch_names if 'EXG' in ch}
    raw_proc.set_channel_types(emg_map)

    # 2. PICK ONLY EEG
    # This removes EXG channels from the current 'raw_proc' object
    raw_proc.pick_types(eeg=True, exclude=[])

    # 3. APPLY MONTAGE
    montage = mne.channels.make_standard_montage("biosemi64")
    raw_proc.set_montage(montage, on_missing="ignore")

    # 4. MARK & INTERPOLATE
    if subject and subject in config.BAD_CHANNELS_MAP:
        raw_proc.info['bads'] = config.BAD_CHANNELS_MAP[subject]
        # Now interpolation only works on the valid EEG sensors (PO7, PO8, etc.)
        raw_proc.interpolate_bads(reset_bads=True)

    # 5. FILTER (Author Replication)
    raw_proc.filter(l_freq=config.L_FREQ, h_freq=config.H_FREQ)

    # 6. RESAMPLE
    if hasattr(config, "RESAMPLE_FREQ") and config.RESAMPLE_FREQ is not None:
        current_sfreq = raw_proc.info["sfreq"]
        if current_sfreq != config.RESAMPLE_FREQ:
            print(f"Resampling data from {current_sfreq} Hz to {config.RESAMPLE_FREQ} Hz...")
            raw_proc.resample(config.RESAMPLE_FREQ)

    raw_proc.set_eeg_reference("average")

    return raw_proc

# def preprocess_raw(raw: mne.io.BaseRaw, subject: str = None) -> mne.io.BaseRaw:
#     """
#     Apply band-pass filtering, notch filter, and rereferencing.

#     Parameters
#     ----------
#     raw : mne.io.BaseRaw
#         Original raw EEG data (preload=True).

#     Returns
#     -------
#     raw_proc : mne.io.BaseRaw
#         Preprocessed copy of the data.
#     """
#     raw_proc = raw.copy()

#     # 1. MARK BAD CHANNELS
#     if subject and subject in config.BAD_CHANNELS_MAP:
#         raw_proc.info['bads'] = config.BAD_CHANNELS_MAP[subject]
#         print(f"Marked bads for sub-{subject}: {raw_proc.info['bads']}")

#     # 2. APPLY MONTAGE 
#     # This gives MNE the 3D coordinates of the electrodes
#     try:
#         montage = mne.channels.make_standard_montage("biosemi64")
#         raw_proc.set_montage(montage, on_missing="ignore")
#     except Exception as e:
#         print(f"Montage Error: {e}")

#     # 3. INTERPOLATE
#     # Now MNE knows where P2, FC6, etc., are located relative to others
#     if len(raw_proc.info['bads']) > 0:
#         raw_proc.interpolate_bads(reset_bads=True)

#     # 2) Band-pass filter (Authors used 25Hz low-pass, we use 40Hz)
#     raw_proc.filter(l_freq=config.L_FREQ, h_freq=config.H_FREQ, fir_design="firwin")

#     # 2.1 ) Notch filter for line noise (50 Hz)
#     if config.NOTCH_FREQS:
#         raw_proc.notch_filter(
#             freqs=config.NOTCH_FREQS,
#             fir_design="firwin",
#             verbose=True,
#         )

        
#     """ if hasattr(config, 'RESAMPLE_FREQ') and config.RESAMPLE_FREQ is not None:
#         print(f"Resampling data to {config.RESAMPLE_FREQ} Hz...")
#         raw_proc.resample(config.RESAMPLE_FREQ) """
#     # 3) Set EEG average reference
#     raw_proc.set_eeg_reference("average", verbose=True)

#     # 4) (Optional) you can add automatic bad channel detection here.
#     # For Milestone 3 we keep it simple and rely on raw_proc.info['bads'].

#     return raw_proc