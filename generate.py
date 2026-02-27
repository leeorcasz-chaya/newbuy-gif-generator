#!/usr/bin/env python3
"""
NewBuy GIF Generator - 生成 Web3 "NEW BUY" 动图
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageFilter
    import imageio
except ImportError:
    print("❌ 缺少依赖库，请运行: pip install -r requirements.txt")
    sys.exit(1)

import subprocess
import tempfile
import math
import random


def extract_frames_from_video(video_path, max_frames=30, target_size=(600, 200)):
    """从视频提取帧"""
    print(f"📹 正在从视频提取帧...")
    
    # 检查 ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 需要安装 ffmpeg: brew install ffmpeg")
        sys.exit(1)
    
    temp_dir = tempfile.mkdtemp()
    output_pattern = os.path.join(temp_dir, 'frame_%04d.png')
    
    # 使用 ffmpeg 提取帧
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'fps={max_frames}/3,scale={target_size[0]}:{target_size[1]}:force_original_aspect_ratio=decrease,pad={target_size[0]}:{target_size[1]}:(ow-iw)/2:(oh-ih)/2',
        '-frames:v', str(max_frames),
        output_pattern
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)
    
    # 读取生成的帧
    frames = []
    for i in range(1, max_frames + 1):
        frame_path = os.path.join(temp_dir, f'frame_{i:04d}.png')
        if os.path.exists(frame_path):
            frames.append(Image.open(frame_path).convert('RGBA'))
    
    print(f"✓ 提取了 {len(frames)} 帧")
    return frames


def add_text_overlay(frame, text, position, font_size=60, color=(255, 255, 255), 
                     stroke_width=3, stroke_color=(0, 0, 0), glow=False):
    """在帧上添加文字"""
    draw = ImageDraw.Draw(frame)
    
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # 发光效果
    if glow:
        for offset in range(1, 6):
            glow_alpha = int(255 * (1 - offset / 6))
            glow_color = (*color[:3], glow_alpha)
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    if dx != 0 or dy != 0:
                        draw.text((position[0] + dx, position[1] + dy), text, 
                                font=font, fill=glow_color)
    
    # 描边
    if stroke_width > 0:
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((position[0] + dx, position[1] + dy), text, 
                            font=font, fill=stroke_color)
    
    # 主文字
    draw.text(position, text, font=font, fill=color)
    
    return frame


def create_flash_effect(frame, intensity=0.5):
    """创建闪光效果"""
    flash = Image.new('RGBA', frame.size, (255, 255, 255, int(255 * intensity)))
    return Image.alpha_composite(frame, flash)


def generate_newbuy_gif(input_path, token_name=None, amount=None, wallet=None, 
                       output_path='newbuy.gif', duration=3, fps=20, size=(600, 200)):
    """生成 NEW BUY GIF"""
    
    print(f"🎨 开始生成 NEW BUY GIF...")
    print(f"   尺寸: {size[0]}x{size[1]}")
    
    # 判断输入类型
    input_ext = Path(input_path).suffix.lower()
    
    if input_ext in ['.mp4', '.mov', '.avi', '.webm']:
        # 视频输入
        frames = extract_frames_from_video(input_path, max_frames=int(duration * fps), target_size=size)
    elif input_ext in ['.gif']:
        # GIF 输入
        img = Image.open(input_path)
        frames = [frame.copy().convert('RGBA').resize(size) 
                 for frame in ImageSequence.Iterator(img)]
        frames = frames[:int(duration * fps)]
    else:
        # 静态图片输入 - 创建缩放动画
        img = Image.open(input_path).convert('RGBA')
        frames = []
        total_frames = int(duration * fps)
        
        for i in range(total_frames):
            # 创建画布
            canvas = Image.new('RGBA', size, (0, 0, 0, 0))
            
            # 计算缩放动画（呼吸效果）
            scale = 1.0 + 0.1 * math.sin(i * 2 * math.pi / total_frames)
            
            # 计算新尺寸（保持宽高比）
            img_ratio = img.width / img.height
            canvas_ratio = size[0] / size[1]
            
            if img_ratio > canvas_ratio:
                # 图片更宽，以宽度为准
                new_width = int(size[0] * scale)
                new_height = int(new_width / img_ratio)
            else:
                # 图片更高，以高度为准
                new_height = int(size[1] * scale)
                new_width = int(new_height * img_ratio)
            
            # 确保不小于画布
            if new_width < size[0]:
                new_width = size[0]
                new_height = int(new_width / img_ratio)
            if new_height < size[1]:
                new_height = size[1]
                new_width = int(new_height * img_ratio)
            
            # 缩放图片
            scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 居中裁剪
            left = (new_width - size[0]) // 2
            top = (new_height - size[1]) // 2
            cropped = scaled_img.crop((left, top, left + size[0], top + size[1]))
            
            # 添加轻微旋转
            rotation = 2 * math.sin(i * 2 * math.pi / total_frames)
            rotated = cropped.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=False)
            
            canvas.paste(rotated, (0, 0))
            frames.append(canvas)
    
    if not frames:
        print("❌ 无法提取帧")
        return
    
    # 处理每一帧
    processed_frames = []
    total_frames = len(frames)
    
    for i, frame in enumerate(frames):
        # 复制帧并转换为 RGBA
        new_frame = frame.copy().convert('RGBA')
        
        # 计算动画进度
        progress = i / total_frames
        
        # 1. 添加动态背景特效层
        effect_layer = Image.new('RGBA', size, (0, 0, 0, 0))
        effect_draw = ImageDraw.Draw(effect_layer)
        
        # 渐变色背景波纹
        for y in range(size[1]):
            wave_offset = int(10 * math.sin(y * 0.1 + i * 0.3))
            alpha = int(30 * (1 + math.sin(i * 0.2 + y * 0.05)))
            color = (
                int(100 + 155 * math.sin(i * 0.1)),
                int(50 + 205 * math.sin(i * 0.15 + 2)),
                int(150 + 105 * math.sin(i * 0.12 + 4)),
                alpha
            )
            effect_draw.rectangle([(wave_offset, y), (size[0] + wave_offset, y + 1)], fill=color)
        
        # 合成背景特效
        new_frame = Image.alpha_composite(new_frame, effect_layer)
        
        # 2. 添加光晕粒子效果
        particle_layer = Image.new('RGBA', size, (0, 0, 0, 0))
        particle_draw = ImageDraw.Draw(particle_layer)
        
        num_particles = 15
        for p in range(num_particles):
            # 粒子运动轨迹
            x = int((p * 40 + i * 15) % (size[0] + 100)) - 50
            y = int(size[1] * 0.5 + 60 * math.sin(p + i * 0.2))
            
            # 粒子大小和透明度
            particle_size = 3 + int(3 * math.sin(p + i * 0.3))
            particle_alpha = int(150 * (1 + math.sin(p * 0.5 + i * 0.25)) / 2)
            
            # 彩色粒子
            particle_color = (
                int(200 + 55 * math.sin(p)),
                int(150 + 105 * math.sin(p + 2)),
                int(100 + 155 * math.sin(p + 4)),
                particle_alpha
            )
            
            particle_draw.ellipse(
                [(x - particle_size, y - particle_size), 
                 (x + particle_size, y + particle_size)],
                fill=particle_color
            )
        
        new_frame = Image.alpha_composite(new_frame, particle_layer)
        
        # 3. NEW BUY 文字动画（居中偏下）
        text_y = int(size[1] * 0.65)  # 居中偏下位置
        
        # 文字缩放和闪烁
        if i % 6 < 4:  # 4帧显示，2帧隐藏（更明显的闪烁）
            # 缩放动画
            text_scale = 1.0 + 0.15 * math.sin(i * 0.4)
            font_size = int(45 * text_scale)
            
            # 颜色循环（金色 -> 白色 -> 粉色 -> 青色）
            phase = (i % 20) / 20
            if phase < 0.25:
                color = (255, 215, 0)  # 金色
            elif phase < 0.5:
                color = (255, 255, 255)  # 白色
            elif phase < 0.75:
                color = (255, 105, 180)  # 粉色
            else:
                color = (0, 255, 255)  # 青色
            
            # 发光强度变化
            glow = (i % 10) < 5
            
            # Y轴弹跳动画
            bounce_offset = int(5 * abs(math.sin(i * 0.5)))
            text_position = (size[0] // 2 - 100, text_y - bounce_offset)
            
            new_frame = add_text_overlay(
                new_frame,
                "🔥 NEW BUY 🔥",
                text_position,
                font_size=font_size,
                color=color,
                stroke_width=4,
                stroke_color=(0, 0, 0),
                glow=glow
            )
        
        # 4. 添加边缘光效
        edge_layer = Image.new('RGBA', size, (0, 0, 0, 0))
        edge_draw = ImageDraw.Draw(edge_layer)
        
        # 顶部和底部渐变光带
        for edge_y in range(10):
            alpha = int(80 * (1 - edge_y / 10) * (1 + math.sin(i * 0.3)) / 2)
            edge_color = (255, 255, 255, alpha)
            edge_draw.rectangle([(0, edge_y), (size[0], edge_y + 1)], fill=edge_color)
            edge_draw.rectangle([(0, size[1] - edge_y - 1), (size[0], size[1] - edge_y)], fill=edge_color)
        
        new_frame = Image.alpha_composite(new_frame, edge_layer)
        
        processed_frames.append(new_frame.convert('RGB'))
        
        # 进度显示
        if (i + 1) % 5 == 0 or i == total_frames - 1:
            print(f"   处理进度: {i + 1}/{total_frames} 帧")
    
    # 保存 GIF
    print(f"💾 保存 GIF 到: {output_path}")
    imageio.mimsave(
        output_path,
        processed_frames,
        duration=1000/fps,  # 毫秒
        loop=0  # 无限循环
    )
    
    print(f"✅ 完成！生成了 {len(processed_frames)} 帧的 GIF")
    print(f"📊 文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description='生成 Web3 NEW BUY 动图')
    parser.add_argument('--input', '-i', required=True, help='输入视频/图片路径')
    parser.add_argument('--token', '-t', help='代币名称（可选）')
    parser.add_argument('--amount', '-a', help='购买金额（可选）')
    parser.add_argument('--wallet', '-w', help='钱包地址（可选）')
    parser.add_argument('--output', '-o', default='newbuy.gif', help='输出文件名')
    parser.add_argument('--duration', '-d', type=float, default=3, help='GIF 时长（秒）')
    parser.add_argument('--fps', '-f', type=int, default=20, help='帧率')
    parser.add_argument('--width', type=int, default=600, help='宽度（像素）')
    parser.add_argument('--height', type=int, default=200, help='高度（像素）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ 输入文件不存在: {args.input}")
        sys.exit(1)
    
    generate_newbuy_gif(
        args.input,
        args.token,
        args.amount,
        args.wallet,
        args.output,
        args.duration,
        args.fps,
        (args.width, args.height)
    )


if __name__ == '__main__':
    main()
