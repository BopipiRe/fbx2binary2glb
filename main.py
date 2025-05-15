import argparse
import os
import subprocess
import sys
import time
from functools import partial
from multiprocessing import Pool, cpu_count, freeze_support


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
    parser.add_argument("--input", type=str, required=True, help="输入文件路径或目录路径")
    parser.add_argument("--output", type=str, required=True, help="输出目录路径")
    parser.add_argument("--processes", type=int, default=max(1, cpu_count() - 1), help="并发进程数 (默认: CPU核心数-1)")
    args = parser.parse_args()
    fbx2glb_script = resource_path("fbx2glb.py")

    if os.path.isfile(args.input):
        fbx_to_glb(args.blender, fbx2glb_script, args.output, args.input)

    elif args.input:
        input_files = [
            os.path.join(args.input, fname)
            for fname in os.listdir(args.input)
            if fname.lower().endswith('.fbx')
        ]

        if not input_files:
            print("No FBX files found in the input path", file=sys.stderr)
            return

        print(f"Found {len(input_files)} FBX files to process with {args.processes} workers")
        start_time = time.time()
        # 使用多进程池处理
        func = partial(fbx_to_glb, args.blender, fbx2glb_script, args.output)
        with Pool(args.processes) as pool:
            results = pool.map(func, input_files)

        success_count = sum(1 for r in results if r)

        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time
        print(f"\nConversion completed: {success_count} succeeded, {len(results) - success_count} failed")
        print(f"\nTotal execution time: {elapsed_time:.2f} seconds")


def fbx_to_glb(blender_path, script_path, output_dir, fbx):
    """修改为接收所有必要参数"""
    try:
        cmd = [
            blender_path,
            "-b",
            "-P", script_path,
            "--",
            "--fbx", fbx,
            "--output", output_dir,
        ]
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to convert {fbx}")
        return False


if __name__ == "__main__":
    freeze_support()
    main()
