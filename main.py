import typer
import shlex
from common.State import State
from command import Load,Show,Clear  # 导入我们拆分出去的命令模块
from models import Lr,Mse,Ne

app = typer.Typer(no_args_is_help=True)
state = State()

@app.callback()
def MainCallback(ctx: typer.Context):
    ctx.obj = state

app.add_typer(Load.app)
app.add_typer(Show.app)
app.add_typer(Lr.app)
app.add_typer(Mse.app)
app.add_typer(Ne.app)

@app.command()
def shell():
    typer.echo("输入 'exit' 或 'quit' 退出")
    while True:
        try:
            command_str = input("(trainer) > ")
        except UnicodeDecodeError:
            typer.secho("请使用英文或者中文输入", fg=typer.colors.YELLOW)
            continue
        if command_str.lower() in ["quit", "exit"]:
            typer.echo("bye")
            break
        parts = shlex.split(command_str)
        parts[0] = parts[0].lower()
        if not parts:
            continue
        try:
            app(parts, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            typer.secho(f"{e}", fg=typer.colors.RED)

if __name__ == "__main__":
        app()
