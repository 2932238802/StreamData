from common.State import State
import typer
import pandas as pd
app = typer.Typer()
MAX_ROWS_TO_SHOW = 100 
MAX_COLS_TO_SHOW = 30

@app.command("showf")
def show(
    ctx: typer.Context,
    rows: int = typer.Option(5, "--rows", "-r", help="希望显示的行数。"),
    cols: int = typer.Option(None, "--cols", "-c", help="希望显示的列数 (默认自动选择)。"),
    show_result: bool = typer.Option(
        False, 
        "--result", "-r", 
        help="显示上一次命令生成的结果数据，而不是原始数据。"
    )
):
    state: State = ctx.obj
    df_to_show = None
    data_name = ""
    
    if show_result:
        if state.result_df is None:
            typer.secho("🟡 提示: 当前没有结果数据可显示。", fg=typer.colors.YELLOW)
            typer.echo("请先运行一个会产生结果的命令 (例如 'train ne run ...')")
            raise typer.Exit()
        df_to_show = state.result_df
    else:
        if state.dataframe is None:
            typer.secho(" 当前没有加载任何原始数据", fg=typer.colors.YELLOW)
            raise typer.Exit()
        df_to_show = state.dataframe


    typer.secho(f"--- 数据 '{state.file_name}' 概览 ---", bold=True, fg=typer.colors.CYAN)
    num_rows_to_show = min(rows, len(df_to_show), MAX_ROWS_TO_SHOW)
    if rows > num_rows_to_show:
        typer.secho(f"注意: 为防止终端卡顿，显示的行数已从 {rows} 限制为 {num_rows_to_show} 行", fg=typer.colors.YELLOW)
    num_cols_to_show = len(df_to_show.columns) 
    
    if cols is not None: 
        num_cols_to_show = min(cols, len(df_to_show.columns), MAX_COLS_TO_SHOW)
        if cols > num_cols_to_show:
            typer.secho(f"为避免格式混乱，显示的列数已从 {cols} 限制为 {num_cols_to_show} 列", fg=typer.colors.YELLOW)
    else: 
        if len(df_to_show.columns) > MAX_COLS_TO_SHOW:
            num_cols_to_show = MAX_COLS_TO_SHOW
            typer.secho(f"数据列数过多，已自动截取前 {num_cols_to_show} 列进行显示", fg=typer.colors.YELLOW)

    display_df = df_to_show.iloc[:num_rows_to_show, :num_cols_to_show]

    typer.echo(display_df.to_string())
    typer.echo("---")
    typer.echo(f"正在显示: {len(display_df)} 行, {len(display_df.columns)} 列")
    typer.echo(f"数据总量: {len(df_to_show)} 行, {len(df_to_show.columns)} 列")


@app.command("show")
def ShowFileName(ctx: typer.Context):
    state:State = ctx.obj
    typer.secho(f"源文件暂存为{state.file_name if "" else "空"}", bold=True, fg=typer.colors.GREEN)
    typer.secho(f"输出文件暂存为{state.file_name_out if "" else "空"}", bold=True, fg=typer.colors.GREEN)
    

