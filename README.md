# 《女神异闻录Q2 迷宫电影院》汉化

## 基本说明
**注意：本补丁仅用作技术交流，请用于正版游戏。**

本项目是对《女神异闻录Q2 迷宫电影院》（<span lang="ja">ペルソナQ2 ニュー シネマ ラビリンス</span>）的简体中文本地化。

## 构建方式
本项目采用 GitHub Actions 自动构建。您也可以手动构建，步骤如下：

1. 安装 [.NET 8.0 SDK](https://dotnet.microsoft.com/zh-cn/download/dotnet/8.0) 和 [Python 3.12+](https://www.python.org/downloads/)。
2. 将字体文件保存在`files/fonts/`文件夹下，并命名为`FZFWQingYinTiJWB.ttf`。推荐使用 [方正FW轻吟体B](https://www.foundertype.com/index.php/FontInfo/index/id/4985) 作为字体，请自行获取授权。
3. 在本项目的根目录下使用 [PowerShell](https://learn.microsoft.com/zh-cn/powershell/) 运行：

``` powershell
python -m pip install -r requirements.txt
. scripts\build_patch.ps1
```

构建完成后，补丁文件夹将保存在`out/`文件夹下。

## 当前进度
- [x] 将修改后的文件打包为`.cpk`文件，用于 Luma 重定向补丁和 Citra 模拟器
- [x] 导出`.bf`和`.bmd`文件中的文本至`.json`文件
- [x] 将`.json`文件与`.csv`文件互相转换
- [x] 将`.json`文件导入回`.bf`和`.bmd`文件
- [x] 根据`.csv`文件中的翻译生成新的码表和字库
- [ ] 处理其他格式文件中包含的文本
- [ ] 导出/导入图片文件

## 致谢
- [3dstools](https://github.com/ObsidianX/3dstools)，作者：[ObsidianX](https://github.com/ObsidianX)
- [Atlus-Script-Tools](https://github.com/tge-was-taken/Atlus-Script-Tools)，作者：[tge-was-taken](https://github.com/tge-was-taken)
- [PersonaEditor](https://github.com/Meloman19/PersonaEditor)，作者：[Meloman19](https://github.com/Meloman19)
- [Persona-Modding](https://github.com/lraty-li/Persona-Modding)，作者：[lraty-li](https://https://github.com/lraty-li)
- [CRI File System Tools](https://www.welovepes.com/2020/10/crifilesystemtools.html)
