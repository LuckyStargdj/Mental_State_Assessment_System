import socket
import csv
import subprocess
import multiprocessing
import time


def worker():

    # 调用.exe文件
    exe_path = r'D:\pycharmWork\eeg\20240604.exe'  # 替换为你的.exe文件路径
    result = subprocess.run([exe_path], capture_output=True, text=True)

    # 输出返回码
    print(f'Return code: {result.returncode}')

    # 输出标准输出
    print(f'Stdout: {result.stdout}')

    # 输出错误输出
    print(f'Stderr: {result.stderr}')



if __name__ == '__main__':
    worker()
    # p = multiprocessing.Process(target=worker)
    # p.start()