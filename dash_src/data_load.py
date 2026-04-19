"""
Handle all data loading
"""

import os
import numpy as np
import pandas as pd

import dash_src.utils as utils

from dash_src.configs.main import config

def load_file_text(file_path):
    #TODO add pdf with Mistral
    #TODO: should go to src?
    if os.path.splitext(file_path)[1] == ".txt":
        f = open(file_path, "r")
        text = f.read()
        f.close()
        return text
    else:
        raise NotImplementedError()