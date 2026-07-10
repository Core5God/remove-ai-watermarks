# 水印清除助手 Windows 安装版

这是基于你本地 `remove-ai-watermarks-webui` 制作的 Windows 桌面封装工程。用户安装完成后，双击“水印清除助手”即可自动打开操作页面，无需自行安装 Python、命令行或依赖。

## 成品能力

- 一次选择最多 10 张图片，处理后可单张下载
- 可选择一键处理、可见水印、不可见标记或清除元数据
- 使用者上传的图片临时保存于 `%LOCALAPPDATA%\ShuiYinQingChuZhuShou\uploads`，不写入安装目录
- 右侧有可展开的“小红书推荐”角标，视觉和交互参考 `motion.beastle.cn`
- 点击角标内按钮会打开 `XIAOHONGSHU_URL` 指定的主页

## 你需要确认的一处内容

在 [app.py](app.py) 顶部，将 `XIAOHONGSHU_URL` 改为你的**真实小红书主页分享链接**，再构建安装包。当前先指向 `https://motion.beastle.cn/`，用于避免错误跳转到未知账号。

## 生成 Windows 安装程序

推荐把本文件夹放进 GitHub 仓库，然后在 GitHub 的 `Actions` 页面手动运行 `Build Windows installer`。它会在 Windows 环境生成可下载的 `水印清除助手-安装程序-v1.0.0.exe`。

也可以在一台 Windows 电脑上安装 Python 3.11 与 Inno Setup 6 后，双击或运行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\installer\build.ps1
```

成品会生成在 `release` 文件夹。

## 已知限制

- 不可见标记处理依赖较大的 AI 模型，首次使用可能需要联网下载，并占用较多磁盘空间。
- 没有 NVIDIA 显卡时，复杂图片会使用 CPU，处理时间会明显变长。
- 目前当前电脑是 macOS，无法在这里可靠生成或签名 Windows `.exe`。本工程附带 Windows 自动构建流程，可在 Windows 或 GitHub Actions 产出真正安装包。
