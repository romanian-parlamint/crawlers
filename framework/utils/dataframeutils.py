#!/usr/bin/env python
"""Utility functions for pandas.DataFrame objects."""
from pathlib import Path
import pandas as pd
import csv


def save_data_frame(data_frame: pd.DataFrame,
                    file_name: str,
                    append: bool = False):
    """Save the provided data frame into specified CSV file.

    Parameters
    ----------
    data_frame: pandas.DataFrame, required
        The data frame to save.
    file_name: str, required
        The path of the CSV file where to save the data frame.
    append: bool, optional
        If set to True the data will be appended to existing CSV file;
        otherwise the file will be overwritten.
    """
    output_file = Path(file_name)
    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)
    write_mode = 'a' if append else 'w'
    data_frame.to_csv(file_name, quoting=csv.QUOTE_NONNUMERIC, mode=write_mode)
