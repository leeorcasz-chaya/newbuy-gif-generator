# NewBuy GIF Generator

自动生成 Web3 项目 "NEW BUY" 动图的工具。

## 功能

- 从视频/图片素材生成炫酷的 GIF
- 添加 "NEW BUY" 文字特效（闪烁、渐变）
- 显示代币信息（名称、金额、钱包地址）
- 支持自定义特效和 emoji

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 如果需要视频处理，安装 ffmpeg
brew install ffmpeg  # macOS
# 或
apt-get install ffmpeg  # Linux
```

## 使用

```bash
python generate.py --input video.mp4 --token "PEPE" --amount "1000" --output newbuy.gif
```

## 参数

- `--input`: 输入视频或图片
- `--token`: 代币名称
- `--amount`: 购买金额
- `--wallet`: 钱包地址（可选）
- `--output`: 输出 GIF 文件名
- `--duration`: GIF 时长（秒）
- `--fps`: 帧率

## 示例

```bash
# 基础版本
python generate.py --input doge.mp4 --token "DOGE" --amount "10000"

# 完整版本
python generate.py \
  --input moon.mp4 \
  --token "SHIB" \
  --amount "1000000" \
  --wallet "0x1234...5678" \
  --duration 3 \
  --fps 15
```

## License

MIT
