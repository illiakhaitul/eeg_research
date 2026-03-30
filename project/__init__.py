"""
EEG Tigers SPN Pipeline
A modernized replication of Makin et al. (2012) using MNE-Python.

We designed this package to be highly modular. The core preprocessing 
and ERP extraction are handled by the main pipeline scripts.
"""
__all__ = ["io", "preprocessing", "ica", "epochs", "erp", "viz", "cluster_perm_test_subject", "plot_grand_average", "plot_group_topomaps", "summary"]