import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ctypes
from PIL import Image, ImageTk
import os
import subprocess
import logging
import time
import threading
import keyboard
import webbrowser

class FlatButton(tk.Frame):
    """扁平化按钮类"""
    def __init__(self, parent, text, command, width=140, height=36, corner_radius=8, 
                 bg_color="#E8F4FD", fg_color="#2C5282", active_bg="#D1E7FE", 
                 font=None, icon=None):
        super().__init__(parent, bg=parent["bg"])
        
        self.command = command
        self.bg_color = bg_color
        self.active_bg = active_bg
        self.corner_radius = corner_radius

        # 设置固定大小
        self.configure(width=width, height=height)
        self.pack_propagate(False)
        
        # 创建画布用于绘制圆角矩形
        self.canvas = tk.Canvas(self, width=width, height=height, 
                               highlightthickness=0, bg=parent["bg"])
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绘制圆角矩形
        self.rect = self._draw_rounded_rect(0, 0, width, height, corner_radius, bg_color)
        
        # 添加阴影效果
        self.shadow = self._draw_shadow(0, 0, width, height, corner_radius)
        
        # 添加图标和文字
        x_offset = 12
        if icon:
            self.icon_text = self.canvas.create_text(x_offset, height//2, text=icon, 
                                                   fill=fg_color, font=("Arial", 12))
            x_offset += 20
        
        # 添加文字
        self.text_item = self.canvas.create_text(x_offset + (width - x_offset)//2, height//2, 
                                               text=text, fill=fg_color, 
                                               font=font or ("Microsoft YaHei UI", 10), 
                                               anchor="center")
        
        # 绑定事件
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.is_pressed = False
        
    def _draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        """绘制圆角矩形"""
        points = [x1+r, y1, x2-r, y1, x2, y1+r, x2, y2-r, x2-r, y2, x1+r, y2, x1, y2-r, x1, y1+r]
        return self.canvas.create_polygon(points, fill=color, outline="", smooth=True)
    
    def _draw_shadow(self, x1, y1, x2, y2, r):
        """绘制细微阴影"""
        shadow_points = [x1+r, y1+1, x2-r, y1+1, x2, y1+r+1, x2, y2-r+1, x2-r, y2+1, x1+r, y2+1, x1, y2-r+1, x1, y1+r+1]
        return self.canvas.create_polygon(shadow_points, fill="", outline="", smooth=True, 
                                        stipple="gray50")
    
    def on_enter(self, e):
        """鼠标进入效果"""
        self.canvas.itemconfig(self.rect, fill=self.active_bg)
        self.canvas.config(cursor="hand2")
        
    def on_leave(self, e):
        """鼠标离开效果"""
        self.canvas.itemconfig(self.rect, fill=self.bg_color)
        self.canvas.config(cursor="")
        
    def on_click(self, e):
        """点击效果"""
        self.is_pressed = True
        # 轻微按下效果
        self.canvas.move(self.rect, 0, 1)
        if hasattr(self, 'icon_text'):
            self.canvas.move(self.icon_text, 0, 1)
        self.canvas.move(self.text_item, 0, 1)
        
    def on_release(self, e):
        """释放效果"""
        if self.is_pressed:
            self.is_pressed = False
            # 恢复原位
            self.canvas.move(self.rect, 0, -1)
            if hasattr(self, 'icon_text'):
                self.canvas.move(self.icon_text, 0, -1)
            self.canvas.move(self.text_item, 0, -1)
            
            # 执行命令
            if self.command:
                self.command()

class DoraToolbox:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("朵拉工具箱")
        self.root.geometry("1000x600")
        self.root.resizable(False, False)
        self.touch_clicks = []       # 记录点击时间
        self.touch_mode = False      # 是否进入摸鱼模式
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
            
        # 设置窗口为圆角（Windows 11 风格）
        self.setup_window_effects()
        
        # 当前选中的功能
        self.current_function = "home"
        self.selected_path = ""
        
        self.setup_ui()
        
    def setup_window_effects(self):
        """设置窗口特效（毛玻璃效果）"""
        try:
            # Windows 毛玻璃效果
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.windll.user32.GetParent(self.root.winfo_id()),
                20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
                ctypes.byref(ctypes.c_int(1)),
                ctypes.sizeof(ctypes.c_int(1))
            )
        except:
            pass
            
    def setup_ui(self):
        """设置主界面 - 扁平化设计"""
        # 主框架 - 使用柔和的米白色背景
        main_frame = tk.Frame(self.root, bg="#FAFAFA")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # 左侧功能列表 - 浅灰色背景
        left_frame = tk.Frame(main_frame, bg="#F5F5F5", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        left_frame.pack_propagate(False)
        
        # 功能按钮配置 - 低饱和度柔和色调
        button_configs = [
            {"text": "首页", "func": "home", "bg": "#F0F8FF", "active": "#E0F0FE", "fg": "#4A90E2", "icon": "◈"},
            {"text": "一键分类产品", "func": "classify", "bg": "#F5F9FF", "active": "#E5EFFD", "fg": "#5B8CDB", "icon": "◉"},
            {"text": "一键分类文件", "func": "file_classify", "bg": "#FFF8F0", "active": "#FFF0E0", "fg": "#E67E22", "icon": "◈"},
            {"text": "一键裁切图片", "func": "crop", "bg": "#F8FBF8", "active": "#E8F5E8", "fg": "#6BA05A", "icon": "▢"},
            {"text": "更多功能", "func": "more", "bg": "#F9F7FE", "active": "#E9E5FD", "fg": "#8A7BC5", "icon": "◆"}
        ]
        
        # 添加标题
        title_label = tk.Label(
            left_frame,
            text="功能菜单",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#F5F5F5",
            fg="#666666"
        )
        title_label.pack(pady=(20, 12), padx=20)
        
        # 创建功能按钮
        for config in button_configs:
            btn = FlatButton(
                left_frame,
                text=config["text"],
                command=lambda f=config["func"]: self.switch_function(f),
                width=160,
                height=38,
                corner_radius=8,
                bg_color=config["bg"],
                active_bg=config["active"],
                fg_color=config["fg"],
                font=("Microsoft YaHei UI", 10),
                icon=config["icon"]
            )
            btn.pack(pady=6, padx=20)
            
        # 右侧内容区域 - 纯白背景
        self.content_frame = tk.Frame(main_frame, bg="#FFFFFF")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 显示首页
        self.show_home()
        
    def switch_function(self, func_name):
        """切换功能页面"""
        self.current_function = func_name
        
        # 清除当前内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if func_name == "home":
            self.show_home()
        elif func_name == "classify":
            self.show_classify()
        elif func_name == "file_classify":
            self.show_file_classify()
        elif func_name == "crop":
            self.show_crop()
        elif func_name == "more":
            self.show_more()
            
    def show_home(self):
        """显示首页 - 扁平化设计"""
        home_frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        home_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 主标题
        title_label = tk.Label(
            home_frame,
            text="朵拉工具箱",
            font=("Microsoft YaHei UI", 28, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(pady=(0, 8))
        
        # 副标题
        subtitle_label = tk.Label(
            home_frame,
            text="简洁高效的图片处理工具",
            font=("Microsoft YaHei UI", 14),
            bg="#FFFFFF",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # 功能卡片区域
        cards_frame = tk.Frame(home_frame, bg="#FFFFFF")
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # 功能卡片配置
        card_configs = [
            {
                "title": "一键分类产品",
                "desc": "根据文件名中的产品名称自动分类",
                "color": "#E8F4FD",
                "text_color": "#4A90E2",
                "icon": "◉"
            },
            {
                "title": "一键分类文件", 
                "desc": "按文件类型自动分类，支持文档、图片、视频等",
                "color": "#FFF8F0",
                "text_color": "#E67E22",
                "icon": "◈"
            },
            {
                "title": "更多功能",
                "desc": "持续更新的实用工具",
                "color": "#F5F3FF",
                "text_color": "#8A7BC5",
                "icon": "◆"
            }
        ]
        
        # 创建功能卡片
        for i, config in enumerate(card_configs):
            card = self.create_function_card(cards_frame, config)
            card.grid(row=0, column=i, padx=12, pady=8, sticky="nsew")
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # 底部说明文字
        desc_frame = tk.Frame(home_frame, bg="#edf4fa", height=80)
        desc_frame.pack(fill=tk.X, pady=(40, 0))
        desc_frame.pack_propagate(False)
        
        desc_text = tk.Label(
            desc_frame,
            text="选择左侧功能开始使用 | 支持 JPG、PNG、GIF 等常见格式 | 操作简单，处理高效",
            font=("Microsoft YaHei UI", 11),
            bg="#edf4fa",
            fg="#777777"
        )
        desc_text.pack(pady=20)
        
    def create_function_card(self, parent, config):
        """创建功能卡片"""
        card = tk.Frame(parent, bg=config["color"], relief=tk.FLAT)
        card.configure(highlightbackground="#E0E0E0", highlightthickness=1)
        
        # 图标
        icon_label = tk.Label(
            card,
            text=config["icon"],
            font=("Arial", 24),
            bg=config["color"],
            fg=config["text_color"]
        )
        icon_label.pack(pady=(20, 8))
        
        # 标题
        title_label = tk.Label(
            card,
            text=config["title"],
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=config["color"],
            fg=config["text_color"]
        )
        title_label.pack(pady=(0, 6))
        
        # 描述
        desc_label = tk.Label(
            card,
            text=config["desc"],
            font=("Microsoft YaHei UI", 11),
            bg=config["color"],
            fg=config["text_color"],
            wraplength=180,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20), padx=16)
        
        return card
        
    def show_classify(self):
        """显示图片分类界面 - 扁平化设计"""
        classify_frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        classify_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 标题
        title_label = tk.Label(
            classify_frame,
            text="一键分类产品",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(pady=(0, 8))
        
        # 副标题
        subtitle_label = tk.Label(
            classify_frame,
            text="根据文件名中的产品名称自动分类整理，如：产品名称(1).jpg",
            font=("Microsoft YaHei UI", 12),
            bg="#FFFFFF",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # 路径选择区域
        path_frame = tk.Frame(classify_frame, bg="#FFFFFF")
        path_frame.pack(fill=tk.X, pady=20)
        
        # 路径输入框
        self.classify_path_var = tk.StringVar()
        path_entry = tk.Entry(
            path_frame,
            textvariable=self.classify_path_var,
            font=("Microsoft YaHei UI", 11),
            width=50,
            relief=tk.FLAT,
            bd=0,
            bg="#edf4fa",
            fg="#333333",
            insertbackground="#666666"
        )
        path_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=8)
        
        # 浏览按钮
        browse_btn = FlatButton(
            path_frame,
            text="浏览文件夹",
            command=lambda: self.browse_folder(self.classify_path_var),
            width=100,
            height=36,
            corner_radius=8,
            bg_color="#E8F4FD",
            active_bg="#D1E7FE",
            fg_color="#4A90E2",
            font=("Microsoft YaHei UI", 10)
        )
        browse_btn.pack(side=tk.LEFT)
        
        # 开始处理按钮
        start_btn = FlatButton(
            classify_frame,
            text="开始分类",
            command=self.start_classify,
            width=160,
            height=44,
            corner_radius=10,
            bg_color="#4A90E2",
            active_bg="#3A7BC8",
            fg_color="#FFFFFF",
            font=("Microsoft YaHei UI", 12, "bold")
        )
        start_btn.pack(pady=40)
        
        # 结果显示区域
        self.classify_result_var = tk.StringVar()
        self.classify_result_var.set("请选择图片文件夹")
        
        result_frame = tk.Frame(classify_frame, bg="#edf4fa", height=60)
        result_frame.pack(fill=tk.X, pady=20)
        result_frame.pack_propagate(False)
        
        result_label = tk.Label(
            result_frame,
            textvariable=self.classify_result_var,
            font=("Microsoft YaHei UI", 11),
            bg="#edf4fa",
            fg="#666666"
        )
        result_label.pack(pady=18)
        
    def show_file_classify(self):
        """显示文件分类界面 - 扁平化设计"""
        file_classify_frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        file_classify_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 标题
        title_label = tk.Label(
            file_classify_frame,
            text="一键分类文件",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(pady=(0, 8))
        
        # 副标题
        subtitle_label = tk.Label(
            file_classify_frame,
            text="按文件类型自动分类，支持文档、图片、视频、音频等",
            font=("Microsoft YaHei UI", 12),
            bg="#FFFFFF",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # 路径选择区域
        path_frame = tk.Frame(file_classify_frame, bg="#FFFFFF")
        path_frame.pack(fill=tk.X, pady=20)
        
        # 路径输入框
        self.file_classify_path_var = tk.StringVar()
        path_entry = tk.Entry(
            path_frame,
            textvariable=self.file_classify_path_var,
            font=("Microsoft YaHei UI", 11),
            width=50,
            relief=tk.FLAT,
            bd=0,
            bg="#edf4fa",
            fg="#333333",
            insertbackground="#666666"
        )
        path_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=8)
        
        # 浏览按钮
        browse_btn = FlatButton(
            path_frame,
            text="浏览文件夹",
            command=lambda: self.browse_folder(self.file_classify_path_var),
            width=100,
            height=36,
            corner_radius=8,
            bg_color="#FFF8F0",
            active_bg="#FFF0E0",
            fg_color="#E67E22",
            font=("Microsoft YaHei UI", 10)
        )
        browse_btn.pack(side=tk.LEFT)
        
        # 开始处理按钮
        start_btn = FlatButton(
            file_classify_frame,
            text="开始分类",
            command=self.start_file_classify,
            width=160,
            height=44,
            corner_radius=10,
            bg_color="#E67E22",
            active_bg="#D35400",
            fg_color="#FFFFFF",
            font=("Microsoft YaHei UI", 12, "bold")
        )
        start_btn.pack(pady=40)
        
        # 结果显示区域
        self.file_classify_result_var = tk.StringVar()
        self.file_classify_result_var.set("请选择要分类的文件夹")
        
        result_frame = tk.Frame(file_classify_frame, bg="#edf4fa", height=60)
        result_frame.pack(fill=tk.X, pady=20)
        result_frame.pack_propagate(False)
        
        result_label = tk.Label(
            result_frame,
            textvariable=self.file_classify_result_var,
            font=("Microsoft YaHei UI", 11),
            bg="#edf4fa",
            fg="#666666"
        )
        result_label.pack(pady=18)
        
    def show_crop(self):
        """显示图片裁切界面 - 扁平化设计"""
        crop_frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        crop_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 标题
        title_label = tk.Label(
            crop_frame,
            text="一键裁切图片",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(pady=(0, 8))
        
        # 副标题
        subtitle_label = tk.Label(
            crop_frame,
            text="批量处理图片：移除背景、裁切内容、调整尺寸并保存到'处理后图片'目录",
            font=("Microsoft YaHei UI", 12),
            bg="#FFFFFF",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # 路径选择区域
        path_frame = tk.Frame(crop_frame, bg="#FFFFFF")
        path_frame.pack(fill=tk.X, pady=20)
        
        # 路径输入框
        self.crop_path_var = tk.StringVar()
        path_entry = tk.Entry(
            path_frame,
            textvariable=self.crop_path_var,
            font=("Microsoft YaHei UI", 11),
            width=50,
            relief=tk.FLAT,
            bd=0,
            bg="#edf4fa",
            fg="#333333",
            insertbackground="#666666"
        )
        path_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=8)
        
        # 浏览按钮
        browse_btn = FlatButton(
            path_frame,
            text="浏览文件夹",
            command=lambda: self.browse_folder(self.crop_path_var),
            width=100,
            height=36,
            corner_radius=8,
            bg_color="#F0F8F0",
            active_bg="#E0F0E0",
            fg_color="#6BA05A",
            font=("Microsoft YaHei UI", 10)
        )
        browse_btn.pack(side=tk.LEFT)
        
        # 开始处理按钮
        start_btn = FlatButton(
            crop_frame,
            text="开始处理",
            command=self.start_crop,
            width=160,
            height=44,
            corner_radius=10,
            bg_color="#6BA05A",
            active_bg="#5A904A",
            fg_color="#FFFFFF",
            font=("Microsoft YaHei UI", 12, "bold")
        )
        start_btn.pack(pady=40)
        
        # 结果显示区域
        self.crop_result_var = tk.StringVar()
        self.crop_result_var.set("请选择图片文件夹")
        
        result_frame = tk.Frame(crop_frame, bg="#edf4fa", height=60)
        result_frame.pack(fill=tk.X, pady=20)
        result_frame.pack_propagate(False)
        
        result_label = tk.Label(
            result_frame,
            textvariable=self.crop_result_var,
            font=("Microsoft YaHei UI", 11),
            bg="#edf4fa",
            fg="#666666"
        )
        result_label.pack(pady=18)
        
    def show_more(self):
        """显示更多功能界面 - 扁平化设计"""
        more_frame = tk.Frame(self.content_frame, bg="#FFFFFF")
        more_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 标题
        title_label = tk.Label(
            more_frame,
            text="更多功能",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(pady=(0, 8))

        subtitle_label = tk.Label(
            more_frame,
            text="精彩功能正在路上",
            font=("Microsoft YaHei UI", 12),
            bg="#FFFFFF",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 60))
        
        # 开发中图标
        icon_frame = tk.Frame(more_frame, bg="#F5F3FF", width=120, height=120)
        icon_frame.pack(pady=20)
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(
            icon_frame,
            text="◆",
            font=("Arial", 48),
            bg="#F5F3FF",
            fg="#8A7BC5"
        )
        icon_label.pack(expand=True)
        
        self.start_btn = FlatButton(
            more_frame,
            text="催更",
            command=self.start_touchfish,
            width=160,
            height=44,
            corner_radius=10,
            bg_color="#FFD700",
            active_bg="#5A904A",
            fg_color="#FFFFFF",
            font=("Microsoft YaHei UI", 12, "bold")
        )
        self.start_btn.pack(pady=20)
        # 说明文字
        desc_label = tk.Label(
            more_frame,
            text="更多实用功能正在开发中...",
            font=("Microsoft YaHei UI", 13),
            bg="#FFFFFF",
            fg="#777777",
            justify=tk.CENTER
        )
        desc_label.pack(pady=30)

    def browse_folder(self, path_var):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            path_var.set(folder_path)
            
    def start_classify(self):
        """开始图片分类"""
        folder_path = self.classify_path_var.get()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择图片文件夹路径！")
            return
            
        self.classify_result_var.set("正在处理中...")
        self.root.update()
        
        try:
            # 调用图片分类脚本
            result = self.process_images(folder_path, "classify")
            self.classify_result_var.set(f"处理完成！共处理了 {result} 张图片，所在根目录已生成产品列表日志")
            messagebox.showinfo("完成", f"图片分类完成！\n共处理了 {result} 张图片")
        except Exception as e:
            self.classify_result_var.set("处理失败")
            messagebox.showerror("错误", f"处理过程中出现错误：\n{str(e)}")
            
    def start_crop(self):
        """开始图片裁切"""
        folder_path = self.crop_path_var.get()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择图片文件夹路径！")
            return

        self.crop_result_var.set("正在载入模型，请不要到处乱点...")
        self.root.update()

        try:
            import threading
            thread = threading.Thread(target=self.crop_wrapper, args=(folder_path, self.update_progress))
            thread.start()
            self.root.after(100, lambda: self.check_thread(thread))
        except Exception as e:
            self.crop_result_var.set("处理失败")
            messagebox.showerror("错误", f"处理过程中出现错误：\n{str(e)}")

    def check_thread(self, thread):
        """检查线程是否完成"""
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread))
        else:
            thread.join()
            
    def update_progress(self, message):
        """更新进度显示，线程安全"""
        self.root.after(0, lambda: self.crop_result_var.set(message))

    def crop_wrapper(self, folder, callback):
        """线程包装函数，调用 process_folder"""
        from image_cropper import process_folder
        result = process_folder(folder, overwrite_original=False, callback=callback)
        self.root.after(0, lambda: self.handle_result(result))

    def handle_result(self, result):
        """处理最终结果"""
        if not isinstance(result, int):
            self.crop_result_var.set(f"处理失败: {result}")
            messagebox.showerror("错误", f"处理过程中出现错误：\n{result}")
            return
        self.crop_result_var.set(f"处理完成！共处理了 {result} 张图片")
        messagebox.showinfo("完成", f"图片裁切完成！\n共处理了 {result} 张图片")

    def start_file_classify(self):
        """开始文件分类"""
        folder_path = self.file_classify_path_var.get()
        if not folder_path:
            messagebox.showwarning("提示", "请先选择要分类的文件夹路径！")
            return
            
        self.file_classify_result_var.set("正在处理中...")
        self.root.update()
        
        try:
            # 调用文件分类器
            from file_classifier import FileClassifier
            classifier = FileClassifier()
            result = classifier.classify_files(folder_path)
            self.file_classify_result_var.set(f"处理完成！共处理了 {result} 个文件")
            messagebox.showinfo("完成", f"文件分类完成！\n共处理了 {result} 个文件")
        except Exception as e:
            self.file_classify_result_var.set("处理失败")
            messagebox.showerror("错误", f"处理过程中出现错误：\n{str(e)}")
            
    def process_images(self, folder_path, operation):
        """处理图片的通用方法"""
        try:
            if operation == "classify":
                # 导入图片分类器
                from image_classifier import ImageClassifier
                classifier = ImageClassifier()
                return classifier.classify_images(folder_path)
                
            elif operation == "crop":
                # 导入图片裁切器
                from image_cropper import ImageCropper
                cropper = ImageCropper()
                return cropper.crop_images(folder_path)
                
            else:
                # 默认统计图片数量
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                image_count = 0
                
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            image_count += 1
                            
                return image_count
                
        except ImportError as e:
            # 如果导入失败，使用简单的统计方法
            logger = logging.getLogger(__name__)
            logger.warning(f"导入处理模块失败: {e}，使用基础统计功能")
            
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            image_count = 0
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        image_count += 1
                        
            return image_count

    def start_touchfish(self):
        """催更按钮点击逻辑"""
        now = time.time()
        # 记录点击时间
        self.touch_clicks.append(now)

        # 只保留 5 秒内的点击
        self.touch_clicks = [t for t in self.touch_clicks if now - t <= 5]
        # 已经进入“摸鱼模式”
        if self.touch_mode:
            self.touch_mode = False
            threading.Thread(target=self.open_touchfish_site).start()
            return

        if len(self.touch_clicks) >= 7:
            self.touch_mode = True
            return

    def open_touchfish_site(self):
        webbrowser.open("https://fakeupdate.net/win10ue/")
        time.sleep(2)  # 等浏览器启动一下
        keyboard.press_and_release("f11")   # 进入全屏
        messagebox.showinfo("提示", "已成功开启摸鱼模式！按F11退出")

    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DoraToolbox()
    app.run()