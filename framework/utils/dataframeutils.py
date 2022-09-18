#!/usr/bin/env python
"""Utility functions for pandas.DataFrame objects."""
from pathlib import Path
import csv


def save_data_frame(data_frame, file_name):
    """Save the provided data frame into specified CSV file.

    Parameters
    ----------
    data_frame: pandas.DataFrame, required
        The data frame to save.
    file_name: str, required
        The path of the CSV file where to save the data frame.
    """
    output_file = Path(file_name)
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)
    data_frame.to_csv(file_name, quoting=csv.QUOTE_NONNUMERIC)
