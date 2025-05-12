import argparse
import os
import subprocess
import sys


def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发环境和PyInstaller打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    parser = argparse.ArgumentParser(description="FBX转GLB转换工具")
    parser.add_argument("--blender", type=str, required=True, help="输入blender.exe路径")
    parser.add_argument("--fbx", type=str, required=True, help="输入FBX文件路径")
    parser.add_argument("--output", type=str, required=True, help="输出目录路径")
    args = parser.parse_args()
    fbx2glb_script = resource_path("fbx2glb.py")
    cmd = [
        args.blender,
        "-b",  # 后台模式
        "-P", fbx2glb_script,  # 指定Python脚本
        "--",
        "--input", args.fbx,
        "--output", args.output,
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
