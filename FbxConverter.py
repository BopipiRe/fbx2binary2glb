import argparse
import os
import sys
import json
from fbx import *


def load_config(config_path):
    """从JSON配置文件加载要删除的节点XPath列表"""
    try:
        with open(config_path) as f:
            config = json.load(f)
            return config.get("nodes_remove_by_search", [])
    except Exception as e:
        print(f"Warning: Failed to load config - {str(e)}", file=sys.stderr)
        return []


def initialize_fbx_manager():
    """初始化FBX SDK管理器"""
    manager = FbxManager.Create()
    if not manager:
        raise Exception("Failed to create FBX Manager")

    # 创建IOSettings对象
    ios = FbxIOSettings.Create(manager, IOSROOT)
    manager.SetIOSettings(ios)

    return manager


def delete_nodes_by_xpath(scene, xpath_list):
    """根据XPath删除节点"""
    root_node = scene.GetRootNode()
    nodes_to_delete = []

    for xpath in xpath_list:
        # FBX SDK没有原生XPath支持，转换为递归搜索
        _find_nodes_by_name_pattern(root_node, xpath, nodes_to_delete)

    for node in nodes_to_delete:
        parent = node.GetParent()
        if parent:
            parent.RemoveChild(node)
        node.Destroy()


def _find_nodes_by_name_pattern(node, pattern, result_list):
    """递归查找名称匹配模式的节点"""
    if pattern.lower() == node.GetName().lower():  # 简单模拟XPath包含匹配
        result_list.append(node)

    for i in range(node.GetChildCount()):
        _find_nodes_by_name_pattern(node.GetChild(i), pattern, result_list)


def load_ascii_fbx(manager, filepath):
    """加载ASCII FBX文件"""
    # 创建导入器
    importer = FbxImporter.Create(manager, "")

    # 初始化导入器
    if not importer.Initialize(filepath, -1, manager.GetIOSettings()):
        error = importer.GetStatus().GetErrorString()
        importer.Destroy()
        raise Exception(f"Failed to initialize importer: {str(error)}")

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
        raise Exception(f"Failed to import scene: {str(error)}")

    importer.Destroy()
    return scene


def save_binary_fbx(manager, scene, output_path):
    """保存为二进制FBX文件"""
    exporter = FbxExporter.Create(manager, "")

    # 初始化导出器为二进制格式
    if not exporter.Initialize(output_path, 0, manager.GetIOSettings()):
        error = exporter.GetStatus().GetErrorString()
        exporter.Destroy()
        raise Exception(f"Failed to initialize exporter: {str(error)}")

    # 设置导出选项
    ios = manager.GetIOSettings()
    ios.SetBoolProp(EXP_FBX_MATERIAL, True)
    ios.SetBoolProp(EXP_FBX_TEXTURE, True)
    ios.SetBoolProp(EXP_FBX_EMBEDDED, True)
    ios.SetBoolProp(EXP_FBX_SHAPE, True)
    ios.SetBoolProp(EXP_FBX_GOBO, True)
    ios.SetBoolProp(EXP_FBX_ANIMATION, True)
    ios.SetBoolProp(EXP_FBX_GLOBAL_SETTINGS, True)

    if not exporter.Export(scene):
        error = exporter.GetStatus().GetErrorString()
        exporter.Destroy()
        raise Exception(f"Failed to export scene: {str(error)}")

    exporter.Destroy()


def convert_ascii_to_binary(input_file, output_path, config_path=None):
    """主转换函数"""
    # 处理PyInstaller打包后的资源路径
    if getattr(sys, 'frozen', False):  # 打包后环境
        base_path = os.path.dirname(sys.executable)
    else:  # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 加载配置
    nodes_to_remove = []
    if config_path:
        abs_config_path = os.path.join(base_path, config_path) if not os.path.isabs(config_path) else config_path
        nodes_to_remove = load_config(abs_config_path)

    output_file = os.path.join(output_path, os.path.basename(input_file))
    manager = None
    scene = None

    try:
        manager = initialize_fbx_manager()
        scene = load_ascii_fbx(manager, input_file)

        if nodes_to_remove:
            delete_nodes_by_xpath(scene, nodes_to_remove)

        save_binary_fbx(manager, scene, output_file)
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Conversion failed: {str(e)}", file=sys.stderr)
        return False
    finally:
        if scene:
            scene.Destroy()
        if manager:
            manager.Destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FBX格式转换工具")
    parser.add_argument("--input", type=str, required=True, help="输入文件路径或目录路径")
    parser.add_argument("--output", type=str, required=True, help="输出目录路径")
    parser.add_argument("--config", type=str, default="setting.json",help="配置文件路径（JSON格式）")

    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if os.path.isfile(args.input):
        convert_ascii_to_binary(args.input, args.output, args.config)
    elif args.input:
        for fname in os.listdir(args.input):
            if fname.lower().endswith('.fbx'):
                convert_ascii_to_binary(
                    os.path.join(args.input, fname),
                    args.output,
                    args.config
                )
