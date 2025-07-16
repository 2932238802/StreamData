import typer
import numpy as np
from common.State import State
import pandas as pd
from pathlib import Path
import time

app = typer.Typer(
    name="ne", 
    help="使用正规方程训练模型 默认使用第一列作为目标列",
    no_args_is_help=True
)

def NE(X, y):
    """
    内部函数：使用正规方程求解线性回归模型的参数 theta
    """
    typer.secho(f"开始处理数据... 输入特征矩阵 X 的形状: {X.shape}")
    m = X.shape[0]
    X_b = np.c_[np.ones((m, 1)), X] 
    typer.secho(f"添加截距项后, X_b 的形状: {X_b.shape}")
    typer.secho("正在计算 (X_b.T @ X_b)...")
    XTX = X_b.T @ X_b
    typer.secho(f"正在计算 {XTX.shape} 矩阵的逆...")
    XTX_inv = np.linalg.inv(XTX)
    typer.secho("正在计算最终的 theta...")
    theta = XTX_inv @ X_b.T @ y
    
    return theta

@app.callback(invoke_without_command=True)
def Run(
    ctx: typer.Context,
    target_column: str = typer.Option("0", "--column", "-c", help="目标列(y)的标识符 可以是名称或索引。此项为必需"),
    output_filename: str = typer.Option("ne_result.xlsx", "--output", "-o", help="保存结果的Excel文件名"),
    target_file: str = typer.Option(
        None, 
        "--target-file", 
        "-tf", 
        help="如果目标(y)在单独的文件中 请指定此项它将被追加为最后一列"
    ),
):
    if ctx.invoked_subcommand is not None:
        return

    state: State = ctx.obj
    if state.dataframe is None:
        typer.secho("错误：请先使用 'load' 命令加载特征数据 (X)", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    df = state.dataframe.copy()
    target_identifier = target_column

    if target_file:
        typer.echo(f"正在处理目标文件: '{target_file}'加载并合并中...")
        data_dir = Path("data")
        target_filepath = data_dir / target_file
        if not target_filepath.exists():
            typer.secho(f"错误: 目标文件 '{target_file}' 在 'data/' 目录中未找到", fg=typer.colors.RED)
            raise typer.Exit(1)
        
        try:
            y_df = pd.read_excel(target_filepath, header=None) if target_filepath.suffix.lower() in ['.xlsx', '.xls'] else pd.read_csv(target_filepath, header=None)
            
            if len(df) != len(y_df):
                typer.secho(f"错误: 行数不匹配主数据有 {len(df)} 行 但目标文件有 {len(y_df)} 行", fg=typer.colors.RED)
                raise typer.Exit(1)
            
            # 为新的目标列创建一个唯一的名称 如果没有列明的话
            # 将目标数据作为新的一列追加到主数据框中
            y_col_name = f"__target_from_{Path(target_file).stem}__" 
            df[y_col_name] = y_df.iloc[:, 0].values
            target_identifier = str(df.shape[1] - 1) 
            typer.secho(f"成功: 已将 '{target_file}' 的数据追加为新的一列", fg=typer.colors.GREEN)
            typer.echo(f"   目标列已自动设定为最后一列 (索引: {target_identifier})")
        except Exception as e:
            typer.secho(f"处理目标文件时出错: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)

    y = None
    X = None
    target_col_name = None

    if target_identifier.isdigit() or (target_identifier.startswith('-') and target_identifier[1:].isdigit()):
        try:
            col_index = int(target_identifier)
            if not (-len(df.columns) <= col_index < len(df.columns)):
                 raise IndexError("列位置超出范围")
            target_col_name = df.columns[col_index]
            typer.echo(f"按位置 '{col_index}' 识别目标列: '{target_col_name}'")
        except (ValueError, IndexError):
            typer.secho(f"无效的列位置 '{target_identifier}'有效范围是 0 到 {len(df.columns)-1} 或 -1 到 {-len(df.columns)}", fg=typer.colors.RED)
            raise typer.Exit(1)
    else:
        if target_identifier not in df.columns:
            typer.secho(f"目标列名 '{target_identifier}' 在数据中未找到", fg=typer.colors.RED)
            raise typer.Exit(1)
        target_col_name = target_identifier
        typer.echo(f"按名称识别目标列: '{target_col_name}'")
    typer.echo(f"开始正规方程计算目标列: '{target_col_name}'")
    
    try:
        y = df[[target_col_name]].to_numpy()
        X = df.drop(columns=[target_col_name]).to_numpy()
        if X.shape[1] == 0:
            typer.secho("特征集(X)为空 无法进行计算", fg=typer.colors.RED)
            raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"数据准备出错: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    # 执行核心算法
    start_time = time.time()
    try:
        typer.echo(f"正在处理 {X.shape[0]}行 x {X.shape[1]}列 的特征数据...")
        theta = NE(X, y) 
    except np.linalg.LinAlgError:
        typer.secho("\n计算失败: 奇异矩阵该矩阵不可逆请检查特征是否存在线性相关性 例如 重复的列或全为0的列）", fg=typer.colors.RED)
        raise typer.Exit(1)
    end_time = time.time()
    typer.echo(f"计算耗时: {end_time - start_time:.2f} 秒")
    
    # 保存到本地的全剧里面 
    theta_df = pd.DataFrame(theta, columns=['theta_value'])
    theta_df.index = ['intercept'] + [f'theta_for_feature_{i}' for i in range(X.shape[1])]
    state.result_df = theta_df # 这里保存到 那个 全局里面
    typer.secho(f"训练完成！模型参数已经保存到result_df 可以通过show 展示 ", fg=typer.colors.GREEN)
    
    typer.echo("\n正在使用刚训练好的模型进行预测...") # 预测的
    m = X.shape[0]
    X_b = np.c_[np.ones((m, 1)), X]
    predictions = X_b @ theta #立即进行预测
    
    res_dir = Path("res")
    res_dir.mkdir(exist_ok=True)
    output_path = res_dir / output_filename # 这里是 平凑一下路径
    predictions_df = pd.DataFrame(predictions, columns=['预测值']) # 这里预测值
    predictions_df.to_excel(output_path, index=False) # 保存预测结果到文件 output_path
    typer.secho(f"\n预测完成！{len(predictions)} 条预测结果已保存到: {output_path}", fg=typer.colors.GREEN)
