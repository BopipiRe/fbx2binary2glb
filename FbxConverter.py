import os
import sys
from fbx import *


def initialize_fbx_manager():
    """初始化FBX SDK管理器"""
    manager = FbxManager.Create()
    if not manager:
        raise Exception("Failed to create FBX Manager")

    # 创建IOSettings对象
    ios = FbxIOSettings.Create(manager, IOSROOT)
    manager.SetIOSettings(ios)

    return manager


def load_ascii_fbx(manager, filepath):
    """加载ASCII FBX文件"""
    # 创建导入器
    importer = FbxImporter.Create(manager, "")

    # 初始化导入器
    if not importer.Initialize(filepath, -1, manager.GetIOSettings()):
        error = importer.GetStatus().GetErrorString()
        importer.Destroy()
        raise Exception(f"Failed to initialize importer: {error}")

    # 检查是否为ASCII格式
    if not importer.IsFBX():
        importer.Destroy()
        raise Exception("File is not in FBX format")

    # 创建场景并导入
    scene = FbxScene.Create(manager, "Scene")
    if not importer.Import(scene):
        error = importer.GetStatus().GetErrorString()
        importer.Destroy()
        scene.Destroy()
        raise Exception(f"Failed to import scene: {error}")

    importer.Destroy()
    return scene


def save_binary_fbx(manager, scene, output_path):
    """保存为二进制FBX文件"""
    # 创建导出器
    exporter = FbxExporter.Create(manager, "")

    # 初始化导出器为二进制格式
    if not exporter.Initialize(output_path, 0, manager.GetIOSettings()):
        error = exporter.GetStatus().GetErrorString()
        exporter.Destroy()
        raise Exception(f"Failed to initialize exporter: {error}")

    # 设置导出选项 - 使用Globals中的常量
    manager.GetIOSettings().SetBoolProp(EXP_FBX_MATERIAL, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_TEXTURE, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_EMBEDDED, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_SHAPE, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_GOBO, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_ANIMATION, True)
    manager.GetIOSettings().SetBoolProp(EXP_FBX_GLOBAL_SETTINGS, True)
    # manager.GetIOSettings().SetBoolProp(EXP_FBX_EXTRACT_EMBEDDED_DATA, True)  # 确保提取嵌入数据

    # 执行导出
    if not exporter.Export(scene):
        error = exporter.GetStatus().GetErrorString()
        exporter.Destroy()
        raise Exception(f"Failed to export scene: {error}")

    exporter.Destroy()


def convert_ascii_to_binary(input_path, output_path):
    """主转换函数"""
    # 验证文件路径
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 初始化FBX SDK
    manager = initialize_fbx_manager()
    scene = None

    try:
        # 加载ASCII FBX
        scene = load_ascii_fbx(manager, input_path)

        # 保存为二进制FBX
        save_binary_fbx(manager, scene, output_path)

        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except Exception as e:
        print(f"Conversion failed: {str(e)}", file=sys.stderr)
        return False
    finally:
        # 清理资源
        if scene:
            scene.Destroy()
        if manager:
            manager.Destroy()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fbx_converter.py <input_ascii.fbx> <output_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, os.path.basename(input_file))
    # input_file = r"E:\文档\WeChat Files\wxid_jod27ip63ff312\FileStorage\File\2025-05\3d_bui_6km2\new_bs_041_poly.fbx"
    # output_file = r"D:\小米云盘\new_self.fbx"
    if convert_ascii_to_binary(input_file, output_file):
        sys.exit(0)
    else:
        sys.exit(1)
