import os
import shutil
from pathlib import Path

class FileClassifier:
    """文件分类器 - 按照文件后缀名分类文件"""
    
    def __init__(self):
        # 特殊文件类型分组映射
        self.special_groups = {
            '文档': ['.doc', '.docx', '.txt', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx'],
            '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'],
            '视频': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.rmvb'],
            '音频': ['.mp3', '.wav', '.flac', '.aac', '.wma', '.ogg'],
            '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            '程序': ['.exe', '.msi', '.bat', '.cmd', '.ps1'],
            '代码': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go']
        }
        
        # 创建反向映射，方便查找
        self.extension_to_group = {}
        for group, extensions in self.special_groups.items():
            for ext in extensions:
                self.extension_to_group[ext.lower()] = group
    
    def classify_files(self, folder_path):
        """
        分类指定文件夹中的文件
        
        Args:
            folder_path: 要分类的文件夹路径
            
        Returns:
            int: 处理的文件数量
        """
        if not os.path.exists(folder_path):
            raise ValueError(f"文件夹不存在: {folder_path}")
        
        folder_path = Path(folder_path)
        processed_count = 0
        
        # 获取所有文件（不包括子文件夹）
        files = [f for f in folder_path.iterdir() if f.is_file()]
        
        for file_path in files:
            extension = file_path.suffix.lower()
            
            if extension in self.extension_to_group:
                # 属于特殊分组
                group_name = self.extension_to_group[extension]
                target_folder = folder_path / group_name
            else:
                # 其他文件按扩展名单独分类
                group_name = extension[1:]  # 去掉点号
                target_folder = folder_path / f"其他_{group_name}"
            
            # 创建目标文件夹
            target_folder.mkdir(exist_ok=True)
            
            # 移动文件
            target_path = target_folder / file_path.name
            
            # 如果目标文件已存在，添加数字后缀
            if target_path.exists():
                base_name = file_path.stem
                counter = 1
                while target_path.exists():
                    new_name = f"{base_name}_{counter}{file_path.suffix}"
                    target_path = target_folder / new_name
                    counter += 1
            
            try:
                shutil.move(str(file_path), str(target_path))
                processed_count += 1
                print(f"已移动: {file_path.name} -> {group_name}/")
            except Exception as e:
                print(f"移动失败 {file_path.name}: {e}")
        
        return processed_count
    
    def get_file_statistics(self, folder_path):
        """获取文件统计信息"""
        if not os.path.exists(folder_path):
            return {}
        
        folder_path = Path(folder_path)
        stats = {}
        
        files = [f for f in folder_path.iterdir() if f.is_file()]
        
        for file_path in files:
            extension = file_path.suffix.lower()
            
            if extension in self.extension_to_group:
                group_name = self.extension_to_group[extension]
            else:
                group_name = f"其他_{extension[1:]}"
            
            stats[group_name] = stats.get(group_name, 0) + 1
        
        return stats