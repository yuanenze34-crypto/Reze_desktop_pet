# 蕾塞桌宠 · Reze Desktop Pet

Windows 离线桌面伙伴：透明逐帧动画、自主行走与睡眠、点击表情、拖动与重力落地、气泡、聊天、设置及托盘菜单。

GitHub 仓库包含源码、素材和构建脚本，不包含 `.venv`、`build` 或 `dist`。首次克隆请按下方步骤安装依赖；运行 `build.bat` 后才会生成 EXE。

## 直接使用

打包版：打开 `dist/RezeDesktopPet/RezeDesktopPet.exe`。移动到其他电脑时，请复制整个 `RezeDesktopPet` 文件夹，不能只复制 EXE。

源码版：双击 `run.bat`（当前项目已准备好 `.venv`）。需要查看报错时运行：

```powershell
.\.venv\Scripts\python.exe main.py
```

新电脑开发环境建议 Python 3.13：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe main.py
```

## 操作

- 单击：随机开心、害羞或生气，以及一句气泡台词。
- 按住左键拖动：松手后下落，触地播放落地动画。
- 双击：打开离线聊天窗口。支持问候、工作学习、睡眠等关键词；不是大模型。
- 右键：聊天、暂停/恢复自主活动、大小、置顶、设置及退出。
- 托盘：右键同样可操作，双击打开聊天。
- 关闭聊天窗口不会退出桌宠；通过右键菜单退出。

暂停仅暂停自主活动，表情动画和拖动后的重力仍工作。默认大小 180 px，支持 100–360 px，Qt 自动处理显示缩放。角色透明像素通过原生窗口区域排除鼠标命中。

## 素材

`assets/reze/` 中有 9 组共 42 张 256×256 RGBA PNG，真实透明背景。由内置 imagegen 参照用户提供的展示板生成新图集，再机械切分、统一缩放和底部对齐；不是直接把带文字的展示板当动画使用。

原始透明图集：`assets/source/atlas.png`；实际提示词：`assets/source/prompt.txt`；预览：`assets/source/contact-sheet.png` 和同目录 9 个 GIF。

| 文件夹 | 帧数 |
|---|---:|
| idle | 6 |
| walk_right / walk_left | 各 6 |
| sleep / happy / shy / angry | 各 4 |
| drag | 2 |
| fall_land | 6 |

左行由右行镜像，因此发髻和服装细节也会镜像。生成素材仍存在细节漂移、动作幅度不均和循环接缝；这是一套可运行的初版，并非人工精修的动画。GIF 仅用于预览，程序使用保留完整 alpha 的 PNG。

替换素材：按原目录和 `000.png`、`001.png` 等命名覆盖，重启程序即可。保持 256×256、角色脚底基线 y=240，并为特效留边距。缺失或损坏的动画回退 idle；idle 也缺失时显示明确标注“素材缺失”的简单占位图。图片仅加载缓存一次，不在每帧解码。

## 配置和结构

用户设置保存在 `%LOCALAPPDATA%/RezeDesktopPet/settings.json`，损坏或非法值自动回退默认值。可用 `REZE_SETTINGS_DIR` 环境变量更改目录。`config/dialogue.json` 可编辑台词；默认设置定义在 `pet/settings.py`，`config/settings.json` 是示例。

`pet/` 包含窗口、动画、素材缓存、状态机、物理和配置；`ui/` 包含聊天、气泡与设置；`ai/` 提供 `AIProvider` 抽象接口及离线实现。未来接远程模型需在后台线程执行，不能阻塞 GUI。当前没有联网对话、屏幕读取或开机自启。

## 验证与打包

```powershell
.\.venv\Scripts\python.exe tools/prepare_assets.py
.\.venv\Scripts\python.exe tools/validate_assets.py
.\.venv\Scripts\python.exe -m pytest -q
.\build.bat
```

素材检查覆盖数量、命名、尺寸、RGBA、透明区域及边距；测试覆盖配置损坏与持久化、缺失素材、状态机、动画、重力以及 Qt 鼠标交互。`main.py --smoke-test` 会显示窗口并在三秒后退出。

已在当前 Windows 11 环境执行 8 项测试，全部通过；源码三秒启动检查正常退出，并检查了实际 Qt 控件渲染图 `assets/source/widget-preview.png`。桌面检查工具未枚举到启动的窗口，因此没有完成桌面截图视觉验收。多显示器热插拔、不同 DPI 混用、所有第三方应用下的点击穿透，以及无 Python 的干净机器部署仍需进一步实机检查。
