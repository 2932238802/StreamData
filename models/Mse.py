import typer
import numpy as np
from common.State import State
import pandas as pd
from pathlib import Path
import time

app = typer.Typer(
    name="mse", 
    help="均方差 训练模型",
    no_args_is_help=True
)

def Mse(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    errors = y_pred - y_true
    squared_errors = errors ** 2  
    mse = np.mean(squared_errors)
    return mse

@app.callback(invoke_without_command=True)
def Run():
    pass
    


