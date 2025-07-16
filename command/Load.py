import typer
import pandas as pd
from pathlib import Path
from common.State import State
from typing import Optional

app = typer.Typer()

MAX_COLS_TO_PRINT_ON_LOAD = 10 

@app.command("load")
def load_data(
    ctx: typer.Context, 
    filename: str = typer.Argument(..., help="要加载的数据文件名"),
    no_header: bool = typer.Option(
        False, 
        "--no-header", 
        "-n",          
        help="若文件无表头，使用此标志"
    ),
    index_col: Optional[int] = typer.Option(
        None,
        "--index-col", 
        "-i",          
        help="指定用作行索引的列号 (例如, 0 代表第一列)。"
    )
):
    state: State = ctx.obj 
    data_dir = Path("data")
    filepath = data_dir / filename
    typer.echo(f"正在查找文件: {filepath}...")
    if not filepath.exists():
        typer.secho(f"文件 '{filename}' 在 'data/' 目录中未找到", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 找到了 
    try:
        file_extension = filepath.suffix.lower()
        df = None
        final_index_col = index_col if index_col is not None else False
        
        if file_extension in ['.csv', '.txt']:
            typer.echo(f"检测到文本文件 ({file_extension})，开始载入")
            header_arg = None if no_header else 'infer'
            df = pd.read_csv(filepath, header=header_arg,index_col=final_index_col)
        elif file_extension in ['.xlsx', '.xls']:
            typer.echo(f"检测到 Excel 文件 ({file_extension})，开始载入")
            excel_header_arg = None if no_header else 0
            df = pd.read_excel(filepath, header=excel_header_arg,index_col=final_index_col)
        else:
            typer.secho(f"不支持的文件类型 '{file_extension}'", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        state.dataframe = df
        state.file_name = filename
        typer.secho(f"成功加载数据 '{filename}'!", fg=typer.colors.GREEN)
        typer.echo(f"数据包含 {len(df)} 行 和 {len(df.columns)} 列")
        cols = df.columns
        if len(cols) > MAX_COLS_TO_PRINT_ON_LOAD:
            cols_to_display = list(map(str, cols[:MAX_COLS_TO_PRINT_ON_LOAD])) + ["..."]
            typer.echo(f"列名 (前 {MAX_COLS_TO_PRINT_ON_LOAD} 个): " + ", ".join(cols_to_display))
        else:
            typer.echo(f"列名: " + ", ".join(map(str, cols)))
        
    except MemoryError:
        typer.secho(f"内存不足: 文件 '{filename}' 过大，无法加载", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"加载文件时出错: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
