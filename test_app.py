import tkinter as tk
from tkinter import messagebox
import os
import sys

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_app():
    """测试主应用是否能正常启动"""
    try:
        # 导入主应用
        from main import DoraToolbox
        
        # 创建应用实例但不运行
        app = DoraToolbox()
        
        # 测试基本功能
        print("应用初始化成功")
        print(f"窗口标题: {app.root.title()}")
        print(f"窗口尺寸: {app.root.geometry()}")
        
        # 测试功能切换
        app.switch_function("home")
        print("切换到首页成功")
        
        app.switch_function("classify")
        print("切换到分类页面成功")
        
        app.switch_function("more")
        print("切换到更多功能页面成功")
        
        # 关闭应用
        app.root.destroy()
        
        print("所有测试通过！应用可以正常运行")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_main_app()