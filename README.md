**可以将fbx从ascii转成二进制，然后使用blender转成glb格式**

## FbxConverter:fbx从ascii转二进制

下载安装autodesk的[fdx sdk python](https://damassets.autodesk.net/content/dam/autodesk/www/files/fbx202037_fbxpythonsdk_win.
exe)后，在cmd中执行以下命令：
`python -m pip install "D:\Program Files\Autodesk\FBX\FBX Python SDK\2020.3.7\fbx-2020.3.7-cp310-none-win_amd64.whl"`

添加了setting.json，可以删除fbx中指定的节点，也可以自定义json的路径

## Fbx2glb:将fbx转成glb格式

首先要安装blender

fbx2glb使用blender的bpy库导入fbx然后转成glb

main调用blender.exe执行fbx2glb.py
