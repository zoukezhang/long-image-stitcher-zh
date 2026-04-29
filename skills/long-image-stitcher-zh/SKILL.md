---
name: "long-image-stitcher-zh"
description: "将多张图片按竖排或横排拼接为一张长图并导出。用户需要把多张截图/照片拼接成一张图（支持方向、对齐、间距、背景）时调用。"
---

# 长图拼接（竖排/横排，多图）

## OpenClaw 安装

前置条件：

- 本机可用的 Python 3

安装方式（二选一）：

1. 作为本地 Skills 目录的一部分使用
   - 确保该目录存在于你的 OpenClaw Skills 工作区/仓库中：skills/long-image-stitcher-zh/
2. 如果你的 OpenClaw CLI 支持安装命令
   - 在包含该技能目录的路径下执行安装（示例命令以你的环境为准）：

```bash
openclaw skills install ./skills/long-image-stitcher-zh
```

依赖安装（脚本运行需要 Pillow）：

```bash
python3 -m pip install -r skills/long-image-stitcher-zh/scripts/requirements.txt
```

## OpenClaw 使用

你可以直接用自然语言描述需求，关键是把以下信息说清楚：

- direction：竖排（vertical）或横排（horizontal）
- 图片来源：文件夹路径或图片路径列表，并说明顺序规则（按文件名数字排序/按时间/手动指定）
- 输出：输出文件名与格式（png/jpg）以及保存位置
- “保持原分辨率不缩放”：等价于 normalize=pad（不缩放，只补背景对齐）
- “全屏/铺满宽度（竖排）或铺满高度（横排）”：等价于 normalize=scale（等比缩放到统一宽/高后再拼接，可能会影响清晰度）

示例：

- “把 ‘导出图片’ 文件夹下的图片按文件名顺序竖排拼接成一张长图，保持原分辨率不缩放，输出到 ‘导出图片/拼接_竖屏.png’。”
- “把 ‘拼图素材’ 文件夹里的图片竖排拼接，每张都铺满宽度再拼接，输出到 ‘拼图素材/拼接_竖排_全宽.png’。”
- “把 a.png、b.png、c.png 横向拼接做对比图，间距 16px，白色背景，输出为 jpg。”

## 适用场景

- 多张截图需要拼成一张长图（竖向）
- 多张图片需要横向拼接做对比图（横向）
- 需要控制对齐方式、间距、背景色，并输出为 PNG/JPG

## 工作流

1. 收集用户输入
   - 拼接方向：竖排（vertical）或横排（horizontal）
   - 图片列表与顺序：明确文件路径，并确认最终顺序
   - 输出路径：建议包含扩展名（.png 或 .jpg）
   - 可选参数：间距、背景色、对齐方式、尺寸归一策略
2. 执行脚本进行拼接
3. 输出文件并回传结果位置

## 参数约定

- direction：vertical | horizontal
- align：start | center | end
  - vertical：对齐影响每张图在水平方向的放置位置
  - horizontal：对齐影响每张图在垂直方向的放置位置
- normalize：pad | scale
  - pad：不缩放，按最大边补背景并对齐（默认，适合截图不想被缩放）
  - scale：按最大宽/高等比缩放到同一宽/高（适合希望边缘齐整）
- spacing：图片之间的像素间距（默认 0）
- background：背景色（如 #ffffff）或 transparent（仅建议配合 PNG）

## 命令行用法

脚本位置：

- skills/long-image-stitcher-zh/scripts/stitch_images.py

安装依赖（需要 Pillow）：

```bash
python3 -m pip install -r skills/long-image-stitcher-zh/scripts/requirements.txt
```

竖排拼接示例（默认 pad + center 对齐）：

```bash
python3 skills/long-image-stitcher-zh/scripts/stitch_images.py \
  --direction vertical \
  --output output_vertical.png \
  a.png b.png c.png
```

横排拼接示例（带间距与背景色）：

```bash
python3 skills/long-image-stitcher-zh/scripts/stitch_images.py \
  --direction horizontal \
  --spacing 16 \
  --background "#ffffff" \
  --output output_horizontal.jpg \
  left.png right.png
```

竖排拼接示例（scale 归一宽度，让边缘更齐整）：

```bash
python3 skills/long-image-stitcher-zh/scripts/stitch_images.py \
  --direction vertical \
  --normalize scale \
  --output output_scaled.png \
  01.png 02.png 03.png
```

## 交互要点（给 Agent）

- 如果用户只说“拼接成一张长图”，默认：direction=vertical、normalize=pad、align=center、spacing=0、background=transparent（输出 png）
- 如果输出是 jpg 且 background=transparent，需要提醒用户改成 png 或指定背景色
- 如果图片数量较多或分辨率很高，优先输出 png（无损），并提醒可能占用较大内存
