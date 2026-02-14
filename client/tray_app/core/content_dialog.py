"""
内容管理界面
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QComboBox, QSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, pyqtSignal
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class ContentManagerDialog(QDialog):
    """内容管理对话框"""
    
    content_changed = pyqtSignal(list)  # 内容列表改变信号
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.contents = config.get("contents", [])
        self.content_dir = Path("contents")
        
        self._setup_ui()
        self._load_contents()
    
    def _setup_ui(self):
        self.setWindowTitle("内容管理")
        self.setMinimumSize(700, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                font-size: 13px;
            }
            QPushButton#addBtn {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QPushButton#removeBtn {
                background-color: #f38ba8;
                color: #1e1e2e;
            }
            QPushButton#saveBtn {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }
            QPushButton#cancelBtn {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QListWidget {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QGroupBox {
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox, QSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("📁 内容管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # 内容列表
        list_group = QGroupBox("播放列表")
        list_layout = QVBoxLayout(list_group)
        
        self.content_list = QListWidget()
        self.content_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.content_list)
        
        # 列表操作按钮
        list_btn_layout = QHBoxLayout()
        
        self.up_btn = QPushButton("⬆️ 上移")
        self.up_btn.clicked.connect(self._move_up)
        
        self.down_btn = QPushButton("⬇️ 下移")
        self.down_btn.clicked.connect(self._move_down)
        
        list_btn_layout.addWidget(self.up_btn)
        list_btn_layout.addWidget(self.down_btn)
        list_btn_layout.addStretch()
        
        list_layout.addLayout(list_btn_layout)
        layout.addWidget(list_group)
        
        # 添加内容区域
        add_group = QGroupBox("添加内容")
        add_layout = QVBoxLayout(add_group)
        
        # 类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["图片", "视频", "时钟"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        type_layout.addStretch()
        add_layout.addLayout(type_layout)
        
        # 文件选择（图片/视频）
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("文件:"))
        
        self.file_label = QLabel("未选择")
        self.file_label.setStyleSheet("color: #6c7086;")
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_btn)
        
        add_layout.addLayout(file_layout)
        
        # 时钟设置
        clock_layout = QHBoxLayout()
        clock_layout.addWidget(QLabel("时钟模式:"))
        
        self.clock_mode_combo = QComboBox()
        self.clock_mode_combo.addItems(["仅时间", "日期+时间"])
        clock_layout.addWidget(self.clock_mode_combo)
        clock_layout.addStretch()
        
        add_layout.addLayout(clock_layout)
        
        # 时长设置
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("显示时长:"))
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 300)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" 秒")
        duration_layout.addWidget(self.duration_spin)
        
        self.loop_checkbox = QPushButton("循环播放")
        self.loop_checkbox.setCheckable(True)
        self.loop_checkbox.setChecked(True)
        self.loop_checkbox.setStyleSheet("padding: 4px 8px;")
        duration_layout.addWidget(self.loop_checkbox)
        
        duration_layout.addStretch()
        add_layout.addLayout(duration_layout)
        
        # 添加按钮
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        
        add_btn = QPushButton("➕ 添加到列表")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self._add_content)
        add_btn_layout.addWidget(add_btn)
        
        add_layout.addLayout(add_btn_layout)
        layout.addWidget(add_group)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        remove_btn = QPushButton("🗑️ 删除选中")
        remove_btn.setObjectName("removeBtn")
        remove_btn.clicked.connect(self._remove_content)
        btn_layout.addWidget(remove_btn)
        
        save_btn = QPushButton("💾 保存")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 初始化状态
        self._on_type_changed(0)
        self.selected_file = None
    
    def _on_type_changed(self, index):
        """类型改变"""
        content_type = ["image", "video", "clock"][index]
        
        # 显示/隐藏相关控件
        is_file_type = content_type in ["image", "video"]
        is_clock = content_type == "clock"
        
        self.file_label.setVisible(is_file_type)
        self.browse_btn.setVisible(is_file_type)
        self.clock_mode_combo.setVisible(is_clock)
        
        if is_clock:
            self.duration_spin.setValue(10)
        elif content_type == "video":
            self.duration_spin.setValue(30)
        else:
            self.duration_spin.setValue(30)
    
    def _browse_file(self):
        """浏览文件"""
        content_type = ["image", "video", "clock"][self.type_combo.currentIndex()]
        
        if content_type == "image":
            filter_str = "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif);;所有文件 (*.*)"
        else:
            filter_str = "视频文件 (*.mp4 *.wmv *.avi);;所有文件 (*.*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", filter_str
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(Path(file_path).name)
            self.file_label.setStyleSheet("color: #a6e3a1;")
    
    def _add_content(self):
        """添加内容"""
        content_type = ["image", "video", "clock"][self.type_combo.currentIndex()]
        
        if content_type in ["image", "video"] and not self.selected_file:
            QMessageBox.warning(self, "提示", "请先选择文件")
            return
        
        content = {
            "type": content_type,
            "duration": self.duration_spin.value() if content_type != "video" or not self.loop_checkbox.isChecked() else None
        }
        
        if content_type == "image":
            content["path"] = self.selected_file
        elif content_type == "video":
            content["path"] = self.selected_file
        elif content_type == "clock":
            content["mode"] = "datetime" if self.clock_mode_combo.currentIndex() == 1 else "time_only"
            content["timezone"] = "Asia/Shanghai"
        
        self.contents.append(content)
        self._refresh_list()
        
        # 重置
        self.selected_file = None
        self.file_label.setText("未选择")
        self.file_label.setStyleSheet("color: #6c7086;")
    
    def _remove_content(self):
        """删除选中内容"""
        current_row = self.content_list.currentRow()
        if current_row >= 0:
            self.contents.pop(current_row)
            self._refresh_list()
    
    def _move_up(self):
        """上移"""
        current_row = self.content_list.currentRow()
        if current_row > 0:
            self.contents[current_row], self.contents[current_row - 1] = \
                self.contents[current_row - 1], self.contents[current_row]
            self._refresh_list()
            self.content_list.setCurrentRow(current_row - 1)
    
    def _move_down(self):
        """下移"""
        current_row = self.content_list.currentRow()
        if current_row < len(self.contents) - 1:
            self.contents[current_row], self.contents[current_row + 1] = \
                self.contents[current_row + 1], self.contents[current_row]
            self._refresh_list()
            self.content_list.setCurrentRow(current_row + 1)
    
    def _refresh_list(self):
        """刷新列表"""
        self.content_list.clear()
        
        type_names = {"image": "🖼️ 图片", "video": "🎬 视频", "clock": "🕐 时钟"}
        
        for i, content in enumerate(self.contents):
            if content["type"] == "clock":
                text = f"{i+1}. {type_names['clock']} - {content.get('mode', 'time_only')}"
            else:
                path = Path(content.get("path", ""))
                text = f"{i+1}. {type_names.get(content['type'], content['type'])} - {path.name}"
                if content.get("duration"):
                    text += f" ({content['duration']}秒)"
            
            item = QListWidgetItem(text)
            self.content_list.addItem(item)
    
    def _load_contents(self):
        """加载现有内容"""
        self._refresh_list()
    
    def _save(self):
        """保存"""
        if not self.contents:
            QMessageBox.warning(self, "提示", "播放列表不能为空")
            return
        
        self.config["contents"] = self.contents
        self.content_changed.emit(self.contents)
        self.accept()
    
    def get_contents(self):
        """获取内容列表"""
        return self.contents
