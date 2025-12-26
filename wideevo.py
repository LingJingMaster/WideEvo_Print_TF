#!/usr/bin/env python3
"""
WideEvo - 富士打印机照片伪装工具
将任意照片转换为富士打印机可识别的格式

功能：
1. 将非4:3比例的照片裁剪为4:3
2. 将非JPEG格式转换为JPEG
3. 复制模版照片的EXIF信息（不包括缩略图/预览图）
4. 按DSCF0001.JPG格式命名输出文件
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


# EXIF模版照片路径
TEMPLATE_PATH = Path(__file__).parent / "template.jpg"

# 需要从模版复制的EXIF标签（相机识别相关）
EXIF_TAGS = [
    "Make",
    "Model",
    "Software",
    "InternalSerialNumber",
    "SerialNumber",
    "LensMake",
    "LensModel",
    "LensSerialNumber",
    "FujiFilmVersion",
    "ExifVersion",
]


def check_dependencies():
    """检查必要的依赖是否已安装"""
    # 检查 exiftool
    try:
        subprocess.run(["exiftool", "-ver"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 exiftool，请先安装: brew install exiftool")
        sys.exit(1)
    
    # 检查 ImageMagick (convert 命令)
    try:
        subprocess.run(["magick", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 ImageMagick，请先安装: brew install imagemagick")
        sys.exit(1)


def get_image_dimensions(image_path: Path) -> tuple[int, int]:
    """获取图片尺寸"""
    result = subprocess.run(
        ["magick", "identify", "-format", "%w %h", str(image_path)],
        capture_output=True,
        text=True,
        check=True
    )
    width, height = map(int, result.stdout.strip().split())
    return width, height


def crop_to_4_3(input_path: Path, output_path: Path) -> bool:
    """
    将图片裁剪为4:3比例（居中裁剪）
    返回是否进行了裁剪
    """
    width, height = get_image_dimensions(input_path)
    
    target_ratio = 4 / 3
    current_ratio = width / height
    
    # 判断是横向还是纵向
    if current_ratio > 1:
        # 横向照片，目标比例 4:3
        target_ratio = 4 / 3
    else:
        # 纵向照片，目标比例 3:4
        target_ratio = 3 / 4
    
    # 检查是否已经是4:3或3:4
    if abs(current_ratio - target_ratio) < 0.01:
        # 已经是目标比例，只需复制/转换
        subprocess.run(
            ["magick", str(input_path), "-quality", "95", str(output_path)],
            check=True
        )
        return False
    
    # 计算裁剪尺寸
    if current_ratio > target_ratio:
        # 太宽了，需要裁剪宽度
        new_width = int(height * target_ratio)
        new_height = height
    else:
        # 太高了，需要裁剪高度
        new_width = width
        new_height = int(width / target_ratio)
    
    # 居中裁剪
    subprocess.run(
        [
            "magick", str(input_path),
            "-gravity", "center",
            "-crop", f"{new_width}x{new_height}+0+0",
            "+repage",
            "-quality", "95",
            str(output_path)
        ],
        check=True
    )
    
    return True


def copy_exif_from_template(template_path: Path, target_path: Path):
    """从模版照片复制EXIF信息到目标照片"""
    if not template_path.exists():
        print(f"警告: 模版文件不存在: {template_path}")
        print("将跳过EXIF复制，照片可能无法被打印机识别")
        return
    
    # 构建exiftool命令
    tag_args = [f"-{tag}" for tag in EXIF_TAGS]
    
    cmd = [
        "exiftool",
        "-TagsFromFile", str(template_path),
        *tag_args,
        "-overwrite_original",
        str(target_path)
    ]
    
    subprocess.run(cmd, capture_output=True, check=True)


def get_next_filename(output_dir: Path) -> Path:
    """获取下一个可用的文件名 (DSCF0001.JPG, DSCF0002.JPG, ...)"""
    index = 1
    while True:
        filename = f"DSCF{index:04d}.JPG"
        filepath = output_dir / filename
        if not filepath.exists():
            return filepath
        index += 1


def process_image(input_path: Path, output_dir: Path, verbose: bool = False) -> Path:
    """处理单张图片"""
    output_path = get_next_filename(output_dir)
    
    if verbose:
        print(f"处理: {input_path.name} -> {output_path.name}")
    
    # 1. 裁剪为4:3并转换为JPEG
    cropped = crop_to_4_3(input_path, output_path)
    if verbose and cropped:
        print(f"  - 已裁剪为4:3比例")
    
    # 2. 复制EXIF信息
    copy_exif_from_template(TEMPLATE_PATH, output_path)
    if verbose:
        print(f"  - 已复制EXIF信息")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="WideEvo - 富士打印机照片伪装工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s photo.png                    # 处理单张照片
  %(prog)s *.jpg                        # 处理多张照片
  %(prog)s photo.png -o ./output        # 指定输出目录
        """
    )
    
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="要处理的图片文件"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path.cwd(),
        help="输出目录 (默认: 当前目录)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    
    args = parser.parse_args()
    
    # 检查是否提供了图片
    if not args.images:
        parser.print_help()
        return
    
    # 检查依赖
    check_dependencies()
    
    # 检查模版
    if not TEMPLATE_PATH.exists():
        print(f"错误: 模版文件不存在: {TEMPLATE_PATH}")
        sys.exit(1)
    
    # 创建输出目录
    args.output.mkdir(parents=True, exist_ok=True)
    
    # 处理图片
    processed = []
    for image_path in args.images:
        if not image_path.exists():
            print(f"跳过: 文件不存在: {image_path}")
            continue
        
        try:
            output_path = process_image(image_path, args.output, args.verbose)
            processed.append((image_path, output_path))
        except Exception as e:
            print(f"错误: 处理 {image_path} 失败: {e}")
    
    # 输出结果
    if processed:
        print(f"\n完成! 已处理 {len(processed)} 张照片")
        if args.verbose:
            for src, dst in processed:
                print(f"  {src.name} -> {dst.name}")
        print(f"输出目录: {args.output.absolute()}")


if __name__ == "__main__":
    main()
