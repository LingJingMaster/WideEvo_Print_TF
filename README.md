# WideEvo - 富士打印机照片伪装工具

一个用于将任意照片转换为富士打印机可识别格式的工具，支持命令行和Web界面两种使用方式。

## 功能特性

- 🖼️ **智能裁剪**: 自动将照片裁剪为4:3或3:4比例（横竖自适应）
- 🔄 **格式转换**: 支持PNG、WebP等格式转换为JPEG
- 📋 **EXIF复制**: 复制富士相机EXIF信息，让打印机识别为原生照片
- 📝 **自动命名**: 按DSCF0001.JPG格式自动命名输出文件
- 🌐 **双模式**: 支持命令行批处理和Web界面操作
- 🔒 **隐私安全**: Web版本在浏览器本地处理，不上传任何照片

## 使用方法

### 方式一：Web界面（推荐）

1. 在浏览器中打开 `Web/index.html`
2. 拖拽或选择要处理的照片
3. 点击"处理所有照片"按钮
4. 下载处理后的照片压缩包

**优点**: 无需安装任何依赖，操作简单直观

### 方式二：命令行

#### 安装依赖

```bash
# macOS
brew install exiftool imagemagick

# Linux (Ubuntu/Debian)
sudo apt install libimage-exiftool-perl imagemagick

# Linux (Fedora)
sudo dnf install perl-Image-ExifTool ImageMagick
```

#### 使用示例

```bash
# 处理单张照片
./wideevo.py photo.png

# 批量处理多张照片
./wideevo.py *.jpg *.png

# 指定输出目录
./wideevo.py photo.png -o ./output

# 显示详细处理信息
./wideevo.py photo.png -v
```

#### 命令行参数

- `images`: 要处理的图片文件（支持多个）
- `-o, --output`: 输出目录（默认：当前目录）
- `-v, --verbose`: 显示详细处理信息
- `-h, --help`: 显示帮助信息

## 工作原理

1. **比例检测**: 识别照片是横向还是纵向
2. **智能裁剪**: 居中裁剪为4:3（横向）或3:4（纵向）比例
3. **格式转换**: 转换为高质量JPEG格式（质量95）
4. **EXIF写入**: 复制模板照片的富士相机EXIF信息
5. **自动命名**: 按DSCF序列号格式命名

## 目录结构

```
WideEvo/
├── wideevo.py          # 命令行主程序
├── template.jpg        # EXIF模板照片（包含富士相机信息）
├── Web/                # Web版本
│   ├── index.html      # 主页面
│   ├── app.js          # 核心逻辑
│   ├── exif-template.js # EXIF模板数据
│   └── style.css       # 样式表
└── README.md           # 说明文档
```

## 技术说明

### 命令行版本

- **Python 3.6+**
- **ExifTool**: 用于EXIF信息读写
- **ImageMagick**: 用于图片裁剪和格式转换

### Web版本

- **纯前端实现**: 使用Canvas API进行图片处理
- **piexifjs**: 用于EXIF信息写入
- **JSZip**: 用于批量下载压缩包
- **本地处理**: 所有操作在浏览器中完成，不上传服务器

## 注意事项

- 确保 `template.jpg` 文件存在，它包含了富士相机的EXIF信息
- 处理后的照片会覆盖部分原始EXIF信息（如拍摄时间保留，但相机型号会被替换）
- Web版本需要现代浏览器支持（Chrome、Firefox、Safari、Edge等）
- 命令行版本仅在macOS和Linux上测试过

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
