import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
import mne

import config
from project.erp import compute_spn_metrics 

class TestPipelineSanity(unittest.TestCase):

    def setUp(self):
        """
        Set up dummy EEG data before each test.
        We create fake 'Evoked' objects with known flat microvolt values.
        """
        # Create dummy metadata: 3 channels, 256 Hz
        self.info = mne.create_info(ch_names=['PO7', 'PO8', 'Oz'], sfreq=256, ch_types=['eeg']*3)
        
        # Fake Symmetry Data: Flat 5 µV signal (5e-6 Volts)
        data_sym = np.ones((3, 256)) * 5e-6
        self.evoked_sym = mne.EvokedArray(data_sym, self.info, tmin=0.0)
        
        # Fake Random Data: Flat 2 µV signal (2e-6 Volts)
        data_ran = np.ones((3, 256)) * 2e-6
        self.evoked_ran = mne.EvokedArray(data_ran, self.info, tmin=0.0)
        
        self.evokeds_dict = {'symmetry': self.evoked_sym, 'random': self.evoked_ran}
        self.roi = ['PO7', 'PO8']

    def test_spn_math_logic(self):
        """
        Test if the SPN difference is correctly calculated.
        If Symmetry is 5µV and Random is 2µV, the SPN MUST be 3µV.
        """
        sym_mean, ran_mean, spn_mean = compute_spn_metrics(self.evokeds_dict, self.roi)
        
        # Check that the extracted means match our dummy data
        self.assertAlmostEqual(sym_mean, 5.0, places=4, msg="Symmetry mean extraction failed")
        self.assertAlmostEqual(ran_mean, 2.0, places=4, msg="Random mean extraction failed")
        
        # Check the core SPN math (5 - 2 = 3)
        self.assertAlmostEqual(spn_mean, 3.0, places=4, msg="SPN subtraction logic failed")

    def test_preprocessing_parameters(self):
        """
        Test that critical upgraded parameters haven't been accidentally overwritten.
        """
        # Baseline must be strictly pre-stimulus to avoid VEP bleeding
        self.assertEqual(config.BASELINE, (-0.2, 0.0), "Baseline must be -200 to 0 ms")
        
        # Filters must be 0.5 to 30.0 Hz to capture SPN cleanly
        self.assertEqual(config.L_FREQ, 0.5, "High-pass filter must be 0.5 Hz")
        self.assertEqual(config.H_FREQ, 30.0, "Low-pass filter must be 30.0 Hz")

if __name__ == '__main__':
    unittest.main()