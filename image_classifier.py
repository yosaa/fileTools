import os
import re
import shutil
import logging
from pathlib import Path
import csv

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageClassifier:
    """图片分类器 - 根据文件名中的产品名称进行分类"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
    def classify_images(self, folder_path):
        """
        对文件夹中的图片进行分类，根据文件名中括号前的产品名称
        
        Args:
            folder_path (str): 图片文件夹路径
            
        Returns:
            int: 处理的图片数量
        """
        logger.info(f"开始分类图片，文件夹路径: {folder_path}")
        
        if not os.path.exists(folder_path):
            raise ValueError(f"文件夹不存在: {folder_path}")
            
        # 获取所有图片文件
        image_files = self._get_image_files(folder_path)
        logger.info(f"找到 {len(image_files)} 张图片")
        
        if not image_files:
            logger.warning("未找到任何图片文件")
            return 0
            
        moved_count, created_products = self._classify_by_product_name(image_files, folder_path)
        try:
            self._export_product_log(folder_path, created_products)
        except Exception as e:
            logger.warning(f"导出产品名称日志失败: {e}")
        
        logger.info(f"图片分类完成，共处理 {moved_count} 张图片")
        return moved_count
        
    def _get_image_files(self, folder_path):
        """获取文件夹中的所有图片文件"""
        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = Path(file)
                if file_path.suffix.lower() in self.supported_formats:
                    image_files.append(os.path.join(root, file))
        return image_files
        
    def _classify_by_product_name(self, image_files, base_folder):
        logger.info("根据文件名中的产品名称进行分类")
        pattern = r'(.+?)\(\d+\)'
        moved_count = 0
        created_products = set()
        for image_file in image_files:
            try:
                file_name = os.path.basename(image_file)
                match = re.search(pattern, file_name)
                if match:
                    product_name = match.group(1).strip()
                    product_folder = os.path.join(base_folder, product_name)
                    if not os.path.exists(product_folder):
                        os.makedirs(product_folder)
                        created_products.add(product_name)
                        logger.info(f"创建产品文件夹: {product_name}")
                    new_file_path = os.path.join(product_folder, file_name)
                    if os.path.exists(new_file_path):
                        base_name = Path(file_name).stem
                        ext = Path(file_name).suffix
                        counter = 1
                        while os.path.exists(new_file_path):
                            new_file_name = f"{base_name}_{counter}{ext}"
                            new_file_path = os.path.join(product_folder, new_file_name)
                            counter += 1
                    shutil.move(image_file, new_file_path)
                    moved_count += 1
                    logger.info(f"移动文件: {file_name} -> {product_name} 文件夹")
                else:
                    logger.warning(f"无法匹配产品名称: {file_name}，跳过处理")
            except Exception as e:
                logger.error(f"处理文件失败 {image_file}: {str(e)}")
        return moved_count, sorted(created_products)

    def _export_product_log(self, base_folder, created_products):
        if not created_products:
            return
        base_folder = Path(base_folder)
        base_name = base_folder.name
        xlsx_path = base_folder / "本次分类的产品名称日志.xlsx"
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "日志"
            ws.append(["目录名称", "产品名称"])
            for name in created_products:
                ws.append([base_name, name])
            wb.save(str(xlsx_path))
            logger.info(f"已导出Excel日志: {xlsx_path}")
        except ImportError:
            csv_path = base_folder / "本次分类的产品名称日志.csv"
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "产品名称"])
                for name in created_products:
                    writer.writerow([base_name, name])
            logger.info(f"未安装openpyxl，已导出CSV日志: {csv_path}")
        
def main():
    """测试函数"""
    classifier = ImageClassifier()
    
    # 测试路径
    test_folder = r"C:\Users\youce_yosaa\Desktop\test_images"  # 修改为你的测试文件夹路径
    if os.path.exists(test_folder):
        count = classifier.classify_images(test_folder)
        print(f"处理了 {count} 张图片")
    else:
        print(f"测试文件夹不存在: {test_folder}")
        print("请创建一个包含类似 '产品名称(1).jpg' 格式文件的测试文件夹")

if __name__ == "__main__":
    main()
