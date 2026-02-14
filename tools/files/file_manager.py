#!/usr/bin/env python3
"""
文件批量处理工具
重命名/移动/复制/清理
"""

import os
import shutil
import hashlib
import time
from pathlib import Path
from typing import List, Callable, Optional
from datetime import datetime


class FileManager:
    """文件管理器"""
    
    @staticmethod
    def get_files(directory: str, extensions: List[str] = None) -> List[str]:
        """获取文件列表"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for f in filenames:
                if extensions is None or any(f.endswith(f'.{ext}') for ext in extensions):
                    files.append(os.path.join(root, f))
        return files
    
    @staticmethod
    def get_file_hash(filepath: str) -> str:
        """获取文件MD5哈希"""
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    @staticmethod
    def batch_rename(directory: str, pattern: str = None,
                     prefix: str = '', suffix: str = '',
                     start: int = 1) -> int:
        """批量重命名
        
        Args:
            directory: 目录路径
            pattern: 自定义格式 (如: "file_{i}")
            prefix: 前缀
            suffix: 后缀
            start: 起始编号
        """
        files = FileManager.get_files(directory)
        count = 0
        
        for i, filepath in enumerate(files):
            dirname = os.path.dirname(filepath)
            ext = os.path.splitext(filepath)[1]
            filename = os.path.splitext(os.path.basename(filepath))[0]
            
            if pattern:
                new_name = pattern.format(i=i + start, date=datetime.now().strftime('%Y%m%d'))
            else:
                new_name = f"{prefix}{filename}{suffix}{ext}"
            
            new_path = os.path.join(dirname, new_name)
            os.rename(filepath, new_path)
            count += 1
        
        print(f"已重命名 {count} 个文件")
        return count
    
    @staticmethod
    def batch_move(directory: str, target_dir: str,
                   condition: Callable[[str], bool] = None):
        """批量移动"""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        count = 0
        files = FileManager.get_files(directory)
        
        for filepath in files:
            if condition is None or condition(filepath):
                shutil.move(filepath, target_dir)
                count += 1
        
        print(f"已移动 {count} 个文件到 {target_dir}")
        return count
    
    @staticmethod
    def batch_copy(directory: str, target_dir: str,
                   pattern: str = None):
        """批量复制"""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        count = 0
        files = FileManager.get_files(directory)
        
        for filepath in files:
            if pattern is None or pattern in filepath:
                shutil.copy2(filepath, target_dir)
                count += 1
        
        print(f"已复制 {count} 个文件")
        return count
    
    @staticmethod
    def clean_duplicates(directory: str, keep: str = 'first') -> int:
        """清理重复文件
        
        Args:
            directory: 目录
            keep: 保留策略 ('first' | 'last' | 'largest')
        """
        files = FileManager.get_files(directory)
        hashes = {}
        deleted = 0
        file_sizes = {}
        
        # 收集文件信息
        for filepath in files:
            file_hash = FileManager.get_file_hash(filepath)
            file_sizes[filepath] = os.path.getsize(filepath)
            
            if file_hash in hashes:
                hashes[file_hash].append(filepath)
            else:
                hashes[file_hash] = [filepath]
        
        # 删除重复
        for file_hash, file_list in hashes.items():
            if len(file_list) > 1:
                if keep == 'first':
                    to_delete = file_list[1:]
                elif keep == 'last':
                    to_delete = file_list[:-1]
                else:  # largest
                    file_list.sort(key=lambda x: file_sizes[x], reverse=True)
                    to_delete = file_list[:-1]
                
                for filepath in to_delete:
                    os.remove(filepath)
                    deleted += 1
        
        print(f"已删除 {deleted} 个重复文件")
        return deleted
    
    @staticmethod
    def organize_by_type(directory: str):
        """按类型整理文件"""
        for filepath in FileManager.get_files(directory):
            ext = Path(filepath).suffix[1:] or 'unknown'
            target = os.path.join(directory, ext)
            
            if not os.path.exists(target):
                os.makedirs(target)
            
            shutil.move(filepath, target)
        
        print("文件整理完成")
    
    @staticmethod
    def organize_by_date(directory: str):
        """按日期整理文件"""
        for filepath in FileManager.get_files(directory):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            date_folder = mtime.strftime('%Y-%m-%d')
            target = os.path.join(directory, date_folder)
            
            if not os.path.exists(target):
                os.makedirs(target)
            
            shutil.move(filepath, target)
        
        print("文件按日期整理完成")
    
    @staticmethod
    def find_files(directory: str, pattern: str) -> List[str]:
        """按名称模式查找文件"""
        import fnmatch
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))
        
        return files
    
    @staticmethod
    def count_files(directory: str) -> Dict[str, int]:
        """统计文件数量"""
        counts = {}
        files = FileManager.get_files(directory)
        
        for filepath in files:
            ext = Path(filepath).suffix.lower()
            counts[ext] = counts.get(ext, 0) + 1
        
        return counts
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict:
        """获取文件信息"""
        stat = os.stat(filepath)
        return {
            'path': filepath,
            'name': os.path.basename(filepath),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'hash': FileManager.get_file_hash(filepath)
        }


# 示例使用
if __name__ == "__main__":
    # 整理文件
    # FileManager.organize_by_type('/path/to/dir')
    
    # 清理重复
    # FileManager.clean_duplicates('/path/to/dir')
    
    # 批量重命名
    # FileManager.batch_rename('/path/to/dir', prefix='file_')
    
    # 统计文件
    # counts = FileManager.count_files('/path/to/dir')
    # for ext, count in counts.items():
    #     print(f"{ext}: {count}")
    
    print("文件管理工具已就绪！")
