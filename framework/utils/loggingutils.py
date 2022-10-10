#!/usr/bin/env python
"""Utility functions for logging."""
import logging


def configure_logging(log_level, log_file=None):
    """Configure logging to write to console, to a file, or both.

    Parameters
    ----------
    log_level: str, required
        The level of messages to display in logs.
    log_file: str, optional
        The path of the log file.
    """
    log_level = getattr(logging, log_level.upper())
    if log_file is not None:
        logging.basicConfig(
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            filename=log_file,
            filemode='w',
            level=log_level)
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter(
            '%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    else:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                            level=log_level)
