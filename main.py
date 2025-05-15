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
    parser.add_argument("--timeout", type=int, default=10, help="单个文件处理超时时间（默认10秒）")
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
        func = partial(fbx_to_glb, args.blender, fbx2glb_script, args.output, args.timeout)
        with Pool(args.processes) as pool:
            results = pool.map(func, input_files)

        # 统计成功/失败
        success_count = sum(1 for r in results if r[0])
        failed_count = len(input_files) - success_count
        failed_files = [r[1] for r in results if not r[0]]
        error_messages = [r[2] for r in results if not r[0]]

        # 打印结果摘要
        print("\n" + "=" * 50)
        print("Conversion Summary".center(50))
        print("=" * 50)
        print(f"Total files processed: {len(input_files)}")
        print(f"Successfully converted: {success_count}")
        print(f"Failed conversions: {failed_count}")
        print(f"Success rate: {success_count / len(input_files) * 100:.1f}%")
        print("-" * 50)

        # 打印详细失败信息（如果有）
        if failed_files:
            print("\nFailure Details:")
            for i, (file, error) in enumerate(zip(failed_files, error_messages), 1):
                print(f"\n{i}. File: {file}")
                print(f"   Error: {error}")

        # 打印性能统计
        end_time = time.time()
        elapsed_time = end_time - start_time
        files_per_second = len(input_files) / elapsed_time if elapsed_time > 0 else float('inf')

        print("\n" + "-" * 50)
        print("Performance Statistics".center(50))
        print("-" * 50)
        print(f"Total execution time: {elapsed_time:.2f} seconds")
        print(f"Processing rate: {files_per_second:.2f} files/second")
        print(f"Number of workers used: {args.processes}")
        print("=" * 50 + "\n")


def fbx_to_glb(blender_path, script_path, output_dir, timeout, fbx, max_retries=2):
    """修改为接收所有必要参数"""
    for attempt in range(max_retries):
        try:
            if getattr(sys, 'frozen', False):
                log = os.path.join(os.path.dirname(sys.executable), "log.txt")
            else:
                log = os.path.join(os.path.dirname(__file__), "log.txt")
            cmd = [
                blender_path,
                "-b",
                "-P", script_path,
                "--",
                "--fbx", fbx,
                "--output", output_dir,
                "--log", log
            ]
            subprocess.run(cmd, check=True, timeout=timeout, shell=True)
            return True, fbx, None
        except Exception  as e:
            err_msg = f"Attempt {attempt + 1} failed for {fbx}: {str(e)}"
    return False, fbx, err_msg


if __name__ == "__main__":
    freeze_support()
    main()
