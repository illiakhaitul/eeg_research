import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mne
import config
from run_subject import run_for_subject


def main():
    mne.set_log_level("INFO")

    for subject in config.SUBJECTS:
        print(f"\n{'=' * 20} Running subject {subject} {'=' * 20}")
        run_for_subject(subject)


if __name__ == "__main__":
    main()