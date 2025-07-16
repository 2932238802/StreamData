
import typer
import pandas as pd
from pathlib import Path
from common.State import State
from typing import Optional

app = typer.Typer()
@app.command("clear")
def Clear(ctx: typer.Context):
    state:State = ctx.obj
    
    state.dataframe=None
    state.file_name=""
    state.result_df=None
    
    typer.secho("内部存储数据已经清空",fg=typer.colors.GREEN)