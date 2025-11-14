import os
import sys
import io
from PIL import Image

# Try to import rembg, handle error if not available
try:
    import rembg
    REMBG_AVAILABLE = True 
except ImportError:
    REMBG_AVAILABLE = False
    print("警告: 未安装rembg库，将使用简单背景替换")
    print("请运行process_images.bat安装所需库")
    print()

def process_images(input_folder, overwrite_original=False):
    """
    处理指定文件夹中的所有图片，包括子文件夹
    
    Args:
        input_folder: 输入文件夹路径
        overwrite_original: 是否覆盖原图，如果为False则创建新文件
    """
    # Counter for processed images
    processed_count = 0
    
    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.lower().endswith(supported_formats):
                try:
                    # Read the image
                    input_path = os.path.join(root, filename)
                    
                    if overwrite_original:
                        output_path = input_path
                    else:
                        # 在同目录下创建"处理后图片"目录
                        output_dir = os.path.join(root, "处理后图片")
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        # Keep original filename but change extension to .png
                        output_filename = os.path.splitext(filename)[0] + '.png'
                        output_path = os.path.join(output_dir, output_filename)
                    
                    print(f"Processing: {input_path}")
                    
                    if REMBG_AVAILABLE:
                        # Read image as bytes
                        with open(input_path, 'rb') as f:
                            input_bytes = f.read()
                        
                        # Remove background using rembg
                        output_bytes = rembg.remove(input_bytes)
                        
                        # Convert result to PIL Image
                        image = Image.open(io.BytesIO(output_bytes))
                        
                        # Place on white background
                        white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
                        white_bg.paste(image, mask=image.split()[-1])
                        image = white_bg.convert("RGB")
                    else:
                        return "rembg 库未安装，无法移除背景"
                        # Fallback: just load the image and convert to RGB
                        # image = Image.open(input_path).convert("RGB")
                    
                    # Crop to content (non-white pixels)
                    bbox = image.getbbox()
                    if bbox:
                        # Crop to content
                        cropped = image.crop(bbox)
                    else:
                        # If no content found, use the whole image
                        cropped = image
                    
                    # 将主体放大150%，保持比例
                    width, height = cropped.size
                    
                    # 计算放大150%后的尺寸
                    new_width = int(width * 3)
                    new_height = int(height * 3)
                    
                    # 确保不超过1000x1000画布
                    scale_factor = min(1000 / new_width, 1000 / new_height, 1.0)
                    if scale_factor < 1.0:
                        new_width = int(new_width * scale_factor)
                        new_height = int(new_height * scale_factor)
                    
                    # 放大图片
                    resized = cropped.resize((new_width, new_height), Image.LANCZOS)
                    
                    # 创建 1000x1000 白底画布并居中贴图
                    final_image = Image.new("RGB", (1000, 1000), (255, 255, 255))
                    x = (1000 - new_width) // 2
                    y = (1000 - new_height) // 2
                    final_image.paste(resized, (x, y))
                    
                    # Add watermark if logo.jpg exists
                    logo_path = "logo.jpg"
                    if os.path.exists(logo_path):
                        try:
                            logo = Image.open(logo_path).convert("RGBA")
                            # Reduce opacity to 30% (50% reduced by 20%)
                            logo_with_transparency = Image.new("RGBA", logo.size)
                            for x_wm in range(logo.size[0]):
                                for y_wm in range(logo.size[1]):
                                    r, g, b, a = logo.getpixel((x_wm, y_wm))
                                    logo_with_transparency.putpixel((x_wm, y_wm), (r, g, b, int(a * 0.3)))
                            
                            # Resize logo to 500x500 while maintaining aspect ratio
                            logo_width, logo_height = logo_with_transparency.size
                            max_logo_size = 500
                            if logo_width > logo_height:
                                new_logo_width = max_logo_size
                                new_logo_height = int(logo_height * max_logo_size / logo_width)
                            else:
                                new_logo_height = max_logo_size
                                new_logo_width = int(logo_width * max_logo_size / logo_height)
                            
                            logo_resized = logo_with_transparency.resize((new_logo_width, new_logo_height), Image.LANCZOS)
                            
                            # Paste logo in center
                            logo_x = (1000 - new_logo_width) // 2
                            logo_y = (1000 - new_logo_height) // 2
                            final_image = final_image.convert("RGBA")
                            final_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
                            final_image = final_image.convert("RGB")
                        except Exception as e:
                            print(f"Warning: Could not add watermark: {str(e)}")
                    
                    # 根据原始文件格式保存
                    if overwrite_original:
                        # 保持原始格式
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext in ['.jpg', '.jpeg']:
                            final_image.save(output_path, 'JPEG', quality=95)
                        elif file_ext == '.png':
                            final_image.save(output_path, 'PNG')
                        elif file_ext == '.bmp':
                            final_image.save(output_path, 'BMP')
                        elif file_ext in ['.tiff', '.tif']:
                            final_image.save(output_path, 'TIFF')
                        elif file_ext == '.webp':
                            final_image.save(output_path, 'WebP')
                        else:
                            final_image.save(output_path, 'PNG')
                    else:
                        # 保存为PNG格式
                        final_image.save(output_path, 'PNG')
                    
                    print(f"Processed: {input_path}")
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Error processing {input_path}: {str(e)}")
    
    print(f"Total processed images: {processed_count}")
    return processed_count

def process_folder(input_folder, overwrite_original=True):
    """
    处理指定文件夹中的所有图片，包括子文件夹，并覆盖原图
    
    Args:
        input_folder: 输入文件夹路径
        overwrite_original: 是否覆盖原图，默认为True
    """
    if not os.path.exists(input_folder):
        print(f"错误: 文件夹 {input_folder} 不存在")
        return 0
    
    print(f"开始处理文件夹: {input_folder}")
    if not REMBG_AVAILABLE:
        print("注意: 未检测到rembg库，将不进行背景移除")
        print("建议运行process_images.bat安装完整功能")
        print()
    else:
        print("正在移除背景并处理图片...")
    
    count = process_images(input_folder, overwrite_original)
    print(f"所有图片处理完成! 共处理 {count} 张图片")
    return count

if __name__ == "__main__":
    input_folder = "."
    output_folder = "./processed"
    print("Starting image processing...")
    if not REMBG_AVAILABLE:
        print("注意: 未检测到rembg库，将不进行背景移除")
        print("建议运行process_images.bat安装完整功能")
        print()
    else:
        print("This may take a while as it's removing backgrounds...")
    process_images(input_folder, False)  # 默认不覆盖原图
    print("All images processed!")
    input("Press Enter to exit...")