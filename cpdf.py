#!/usr/bin/env python

import click
import glob
import pyprind
import questionary
import subprocess
from typing import List, Tuple
from pathlib import Path
from questionary import Style

custom_style = Style([
    ('question', 'fg: salmon'),
    ('qmark', 'fg:red bold')
])

compress_type = ["ebook", "screen", "printer", "prepress", "default"]


def verify_output(default: str, out: str) -> str:
    output = input("输入文件名（默认：{}）： ".format(default))
    if not output:
        output = out
    elif not output.endswith(".pdf"):
        output += ".pdf"
    out_file = Path(output)
    if out_file.is_file() and not questionary.confirm("输出文件已存在，想要覆盖吗？", style=custom_style, qmark="!").ask():
        return ""
    return output

@click.command(add_help_option=False)
@click.option('-c', '--compress', is_flag=True, help='压缩 PDF 文件')
@click.option('-m', '--merge', is_flag=True, help='合并 PDF 文件')
@click.option('-v', '--version', is_flag=True, help='显示版本号')
@click.help_option('-h', '--help', help='显示此帮助信息')
def cli(compress: bool, merge: bool, version: bool) -> None:
    choices = ["合并 pdf", "压缩 pdf", "退出"]
    if version:
        click.echo('Version 1.1')
        return
    click.echo("欢迎使用 pdf 工具")
    if compress:
        pdf_files = glob.glob("*.pdf")
        compress_pdf(pdf_files)
    elif merge:
        pdf_files = glob.glob("*.pdf")
        merge_pdf(pdf_files)
    while True:
        pdf_files = glob.glob("*.pdf")
        choice = questionary.select(
            "你想要：",
            choices=choices
        ).ask()
        if choice == choices[0]:
            merge_pdf(pdf_files)
        elif choice == choices[1]:
            compress_pdf(pdf_files)
        elif choice == choices[2]:
            break
        else:
            click.echo("无效选项")


def merge_pdf(pdf_files: List[str]) -> None:
    """合并"""
    print(pdf_files)
    merging_files = questionary.checkbox(
        "选择想要合并的 pdf",
        choices=pdf_files
    ).ask()

    if not merging_files:
        click.echo("没有文件输入！")
        return
    output = verify_output("merged.pdf", "merged.pdf")
    if not output:
        return
    input_files_str = ' '.join(merging_files)
    command = f'gs -q -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile="{output}" {input_files_str} -c quit'
    subprocess.run(command, shell=True)

    click.echo(f"合并成功！. 输出文件：{output}")


def compress_pdf(pdf_files: List[str]) -> None:
    """压缩 pdf"""
    compressing_file = questionary.select(
        "选择想要压缩的 PDF",
        choices=pdf_files
    ).ask()
    if not compressing_file:
        click.echo("未选择文件！")
        return
    output = verify_output("原文件名.compressed.pdf",
                           f'{Path(compressing_file).stem}.compressed.pdf')
    if not output:
        return
    c_type = questionary.select("选择压缩方式：", compress_type).ask()
    initial_size = Path(compressing_file).stat().st_size
    status = 0
    n = int(initial_size)
    bar = pyprind.ProgBar(n, title='压缩中...')
    command = f'gs -q -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/"{c_type}" -dNOPAUSE -dQUIET -dBATCH -sOutputFile="{output}" "{compressing_file}" -c quit'
    subprocess.run(command, shell=True)
    for i in range(n):
        bar.update()
        status += 1
    print(bar)
    print("\n压缩成功！\n")

    def calc_size(size: int) -> Tuple[float, str]:
        if size < 1_000_000:
            f_size = size / 1000
            unit = "KB"
        else:
            f_size = size / 1000_000
            unit = "MB"
        return (f_size, unit)

    final_size = Path(output).stat().st_size
    compression_percentage = (1 - final_size / initial_size) * 100
    print(
        f"{compressing_file} : {calc_size(initial_size)[0]:.2f}{calc_size(initial_size)[1]} -> {calc_size(final_size)[0]:.2f}{calc_size(final_size)[1]}, \033[31m-{compression_percentage:.2f}%\033[0m\n")

if __name__ == '__main__':
    cli()
