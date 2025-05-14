import argparse
import os
import subprocess
import sys
from multiprocessing import Pool, cpu_count

blender = ""
fbx2glb_script = ""
output = ""


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
    parser.add_argument("--blender", type=str, required=True, help="blender.exe路径")
    parser.add_argument("--fbx", type=str, required=True, help="输入FBX文件路径")
    parser.add_argument("--input", type=str, required=False, help="输入目录路径")
    parser.add_argument("--output", type=str, required=True, help="输出目录路径")
    args = parser.parse_args()
    global fbx2glb_script, blender, output
    output = args.output
    fbx2glb_script = resource_path("fbx2glb.py")
    blender = args.blender
    fbx_to_glb(args.fbx)


def fbx_to_glb(fbx):
    """处理FBX文件"""
    cmd = [
        blender,
        "-b",  # 后台模式
        "-P", fbx2glb_script,  # 指定Python脚本
        "--",
        "--fbx", fbx,
        "--output", output,
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

