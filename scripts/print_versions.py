import sys

try:
    import click

    click_ver = click.__version__
except Exception as e:
    click_ver = f"error: {e}"

try:
    import typer

    typer_ver = typer.__version__
except Exception as e:
    typer_ver = f"error: {e}"

print(f"python: {sys.version}")
print(f"click: {click_ver}")
print(f"typer: {typer_ver}")
