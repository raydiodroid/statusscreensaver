"""
配置管理界面
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QGroupBox, QColorDialog, QMessageBox, QScrollArea,
    QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

logger = logging.getLogger(__name__)


class ConfigDialog(QDialog):
    """配置管理对话框"""
    
    # 样式表
    STYLESHEET = """
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
            background-color: #45475a;
            color: #cdd6f4;
        }
        QPushButton:hover {
            background-color: #585b70;
        }
        QPushButton#saveBtn {
            background-color: #a6e3a1;
            color: #1e1e2e;
        }
        QPushButton#saveBtn:hover {
            background-color: #94e2d5;
        }
        QPushButton#cancelBtn {
            background-color: #f38ba8;
            color: #1e1e2e;
        }
        QLineEdit, QSpinBox {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        }
        QLineEdit:focus, QSpinBox:focus {
            border-color: #89b4fa;
        }
        QCheckBox {
            color: #cdd6f4;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #45475a;
            background-color: #313244;
        }
        QCheckBox::indicator:checked {
            background-color: #89b4fa;
            border-color: #89b4fa;
        }
        QTabWidget::pane {
            border: 1px solid #45475a;
            border-radius: 8px;
            background-color: #1e1e2e;
        }
        QTabBar::tab {
            background-color: #313244;
            color: #cdd6f4;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        QTabBar::tab:selected {
            background-color: #89b4fa;
            color: #1e1e2e;
        }
        QTabBar::tab:hover:!selected {
            background-color: #45475a;
        }
        QGroupBox {
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 8px;
            margin-top: 12px;
            padding: 16px;
            padding-top: 24px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: #89b4fa;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #45475a;
            border: none;
            width: 20px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #585b70;
        }
    """
    
    def __init__(self, config, save_callback=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        self.setWindowTitle("⚙️ 设置")
        self.setMinimumSize(600, 550)
        self.resize(650, 600)
        self.setStyleSheet(self.STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("⚙️ 系统设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #89b4fa;")
        layout.addWidget(title)
        
        # 选项卡
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 创建各选项卡
        self.tabs.addTab(self._create_server_tab(), "🌐 服务器")
        self.tabs.addTab(self._create_device_tab(), "💻 设备")
        self.tabs.addTab(self._create_playlist_tab(), "▶️ 播放")
        self.tabs.addTab(self._create_ui_tab(), "🎨 界面")
        self.tabs.addTab(self._create_download_tab(), "📥 下载")
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 保存设置")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_server_tab(self):
        """创建服务器设置选项卡"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 连接设置组
        conn_group = QGroupBox("连接设置")
        conn_layout = QFormLayout(conn_group)
        conn_layout.setSpacing(12)
        
        self.server_url = QLineEdit()
        self.server_url.setPlaceholderText("ws://服务器地址:端口/ws")
        conn_layout.addRow("服务器地址:", self.server_url)
        
        self.server_token = QLineEdit()
        self.server_token.setPlaceholderText("留空则首次连接时自动注册")
        self.server_token.setEchoMode(QLineEdit.EchoMode.Password)
        conn_layout.addRow("认证令牌:", self.server_token)
        
        self.offline_mode = QCheckBox("离线模式（不连接服务器）")
        conn_layout.addRow("", self.offline_mode)
        
        # 测试连接按钮
        test_btn_layout = QHBoxLayout()
        self.test_conn_btn = QPushButton("🔗 测试连接")
        self.test_conn_btn.clicked.connect(self._test_connection)
        test_btn_layout.addStretch()
        test_btn_layout.addWidget(self.test_conn_btn)
        conn_layout.addRow("", test_btn_layout)
        
        layout.addWidget(conn_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(12)
        
        self.reconnect_interval = QSpinBox()
        self.reconnect_interval.setRange(1, 300)
        self.reconnect_interval.setSuffix(" 秒")
        advanced_layout.addRow("重连间隔:", self.reconnect_interval)
        
        self.heartbeat_interval = QSpinBox()
        self.heartbeat_interval.setRange(5, 600)
        self.heartbeat_interval.setSuffix(" 秒")
        advanced_layout.addRow("心跳间隔:", self.heartbeat_interval)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return scroll
    
    def _create_device_tab(self):
        """创建设备设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 设备信息组
        info_group = QGroupBox("设备信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(12)
        
        self.device_name = QLineEdit()
        self.device_name.setPlaceholderText("输入设备名称")
        info_layout.addRow("设备名称:", self.device_name)
        
        self.device_location = QLineEdit()
        self.device_location.setPlaceholderText("例如：会议室A、前台大厅")
        info_layout.addRow("设备位置:", self.device_location)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        return widget
    
    def _create_playlist_tab(self):
        """创建播放设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 播放选项组
        play_group = QGroupBox("播放选项")
        play_layout = QFormLayout(play_group)
        play_layout.setSpacing(12)
        
        self.auto_play = QCheckBox("自动播放")
        play_layout.addRow("", self.auto_play)
        
        self.shuffle = QCheckBox("随机播放")
        play_layout.addRow("", self.shuffle)
        
        self.interval = QSpinBox()
        self.interval.setRange(1, 3600)
        self.interval.setSuffix(" 秒")
        play_layout.addRow("切换间隔:", self.interval)
        
        layout.addWidget(play_group)
        layout.addStretch()
        
        return widget
    
    def _create_ui_tab(self):
        """创建界面设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 显示设置组
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout(display_group)
        display_layout.setSpacing(12)
        
        # 背景颜色
        bg_color_layout = QHBoxLayout()
        self.bg_color = "#000000"
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 32)
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}; border-radius: 4px;")
        self.bg_color_btn.clicked.connect(self._choose_bg_color)
        bg_color_layout.addWidget(self.bg_color_btn)
        bg_color_layout.addStretch()
        display_layout.addRow("背景颜色:", bg_color_layout)
        
        # 错误显示时间
        self.error_display_time = QSpinBox()
        self.error_display_time.setRange(1, 60)
        self.error_display_time.setSuffix(" 秒")
        display_layout.addRow("错误显示时间:", self.error_display_time)
        
        layout.addWidget(display_group)
        layout.addStretch()
        
        return widget
    
    def _create_download_tab(self):
        """创建下载设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 下载设置组
        download_group = QGroupBox("内容下载")
        download_layout = QFormLayout(download_group)
        download_layout.setSpacing(12)
        
        self.download_enabled = QCheckBox("启用自动下载")
        download_layout.addRow("", self.download_enabled)
        
        self.content_server = QLineEdit()
        self.content_server.setPlaceholderText("http://服务器地址:端口")
        download_layout.addRow("内容服务器:", self.content_server)
        
        self.check_interval = QSpinBox()
        self.check_interval.setRange(60, 86400)
        self.check_interval.setSuffix(" 秒")
        download_layout.addRow("检查间隔:", self.check_interval)
        
        self.download_dir = QLineEdit()
        self.download_dir.setPlaceholderText("contents/downloaded")
        download_layout.addRow("下载目录:", self.download_dir)
        
        layout.addWidget(download_group)
        layout.addStretch()
        
        return widget
    
    def _choose_bg_color(self):
        """选择背景颜色"""
        color = QColorDialog.getColor(QColor(self.bg_color), self, "选择背景颜色")
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}; border-radius: 4px;")
    
    def _load_config(self):
        """加载配置到界面"""
        # 服务器设置
        server = self.config.get("server", {})
        self.server_url.setText(server.get("url", ""))
        self.server_token.setText(server.get("token") or "")
        self.offline_mode.setChecked(server.get("offline_mode", True))
        self.reconnect_interval.setValue(server.get("reconnect_interval", 5))
        self.heartbeat_interval.setValue(server.get("heartbeat_interval", 30))
        
        # 设备设置
        device = self.config.get("device", {})
        self.device_name.setText(device.get("name", "未命名设备"))
        self.device_location.setText(device.get("location", ""))
        
        # 播放设置
        playlist = self.config.get("playlist", {})
        self.auto_play.setChecked(playlist.get("auto_play", True))
        self.shuffle.setChecked(playlist.get("shuffle", False))
        self.interval.setValue(playlist.get("interval", 30))
        
        # 界面设置
        ui = self.config.get("ui", {})
        self.bg_color = ui.get("background_color", "#000000")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color}; border-radius: 4px;")
        self.error_display_time.setValue(ui.get("error_display_time", 5))
        
        # 下载设置
        download = self.config.get("download", {})
        self.download_enabled.setChecked(download.get("enabled", False))
        self.content_server.setText(download.get("content_server", ""))
        self.check_interval.setValue(download.get("check_interval", 300))
        self.download_dir.setText(download.get("download_dir", "contents/downloaded"))
    
    def _save(self):
        """保存配置"""
        # 更新配置
        self.config.setdefault("server", {})
        self.config["server"]["url"] = self.server_url.text().strip()
        token = self.server_token.text().strip()
        self.config["server"]["token"] = token if token else None
        self.config["server"]["offline_mode"] = self.offline_mode.isChecked()
        self.config["server"]["reconnect_interval"] = self.reconnect_interval.value()
        self.config["server"]["heartbeat_interval"] = self.heartbeat_interval.value()
        
        self.config.setdefault("device", {})
        self.config["device"]["name"] = self.device_name.text().strip() or "未命名设备"
        self.config["device"]["location"] = self.device_location.text().strip()
        
        self.config.setdefault("playlist", {})
        self.config["playlist"]["auto_play"] = self.auto_play.isChecked()
        self.config["playlist"]["shuffle"] = self.shuffle.isChecked()
        self.config["playlist"]["interval"] = self.interval.value()
        
        self.config.setdefault("ui", {})
        self.config["ui"]["background_color"] = self.bg_color
        self.config["ui"]["error_display_time"] = self.error_display_time.value()
        
        self.config.setdefault("download", {})
        self.config["download"]["enabled"] = self.download_enabled.isChecked()
        self.config["download"]["content_server"] = self.content_server.text().strip()
        self.config["download"]["check_interval"] = self.check_interval.value()
        self.config["download"]["download_dir"] = self.download_dir.text().strip() or "contents/downloaded"
        
        # 调用保存回调
        if self.save_callback:
            try:
                self.save_callback(self.config)
            except Exception as e:
                logger.error(f"保存配置失败: {e}")
                QMessageBox.warning(self, "保存失败", f"无法保存配置: {e}")
                return
        
        QMessageBox.information(self, "保存成功", "配置已保存，部分设置将在重启后生效。")
        self.accept()
    
    def _test_connection(self):
        """测试服务器连接"""
        import asyncio
        import websockets
        import json
        import threading
        
        url = self.server_url.text().strip()
        token = self.server_token.text().strip() or None
        device_name = self.device_name.text().strip() or "未命名设备"
        device_location = self.device_location.text().strip()
        
        if not url:
            self._show_result_dialog("测试失败", "请先填写服务器地址")
            return
        
        if self.offline_mode.isChecked():
            self._show_result_dialog("测试失败", "当前为离线模式，请取消勾选后再测试")
            return
        
        # 禁用按钮，显示正在测试
        self.test_conn_btn.setEnabled(False)
        self.test_conn_btn.setText("⏳ 测试中...")
        
        result = {"success": False, "message": "", "details": ""}
        
        def do_test():
            async def test_ws():
                try:
                    async with websockets.connect(url, close_timeout=5) as ws:
                        # 发送注册消息
                        register_msg = {
                            "type": "register",
                            "name": device_name,
                            "location": device_location
                        }
                        if token:
                            register_msg["token"] = token
                        
                        await ws.send(json.dumps(register_msg))
                        
                        # 等待响应
                        response = await asyncio.wait_for(ws.recv(), timeout=10)
                        data = json.loads(response)
                        
                        if data.get("type") == "register_ack":
                            result["success"] = True
                            result["message"] = "连接成功！"
                            result["details"] = f"服务器响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
                        else:
                            result["success"] = False
                            result["message"] = "注册失败"
                            result["details"] = f"服务器响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
                            
                except asyncio.TimeoutError:
                    result["success"] = False
                    result["message"] = "连接超时"
                    result["details"] = f"服务器 {url} 在 10 秒内未响应"
                except websockets.exceptions.InvalidURI:
                    result["success"] = False
                    result["message"] = "地址格式错误"
                    result["details"] = f"无效的 WebSocket 地址: {url}\n正确格式: ws://地址:端口/ws 或 wss://地址/ws"
                except websockets.exceptions.InvalidHandshake as e:
                    result["success"] = False
                    result["message"] = "握手失败"
                    result["details"] = f"无法建立 WebSocket 连接:\n{str(e)}\n\n请检查:\n1. 服务器地址是否正确\n2. 服务器是否正在运行\n3. 防火墙是否开放端口"
                except ConnectionRefusedError:
                    result["success"] = False
                    result["message"] = "连接被拒绝"
                    result["details"] = f"无法连接到 {url}\n\n可能原因:\n1. 服务器未运行\n2. 端口错误\n3. 防火墙阻止连接"
                except Exception as e:
                    result["success"] = False
                    result["message"] = "连接失败"
                    result["details"] = f"错误类型: {type(e).__name__}\n错误信息: {str(e)}"
            
            asyncio.run(test_ws())
        
        # 在线程中执行测试
        thread = threading.Thread(target=do_test, daemon=True)
        thread.start()
        
        # 等待线程完成
        def check_done():
            if thread.is_alive():
                QTimer.singleShot(100, check_done)
            else:
                self.test_conn_btn.setEnabled(True)
                self.test_conn_btn.setText("🔗 测试连接")
                title = "✅ 连接成功" if result["success"] else "❌ " + result["message"]
                self._show_result_dialog(title, result["details"])
        
        check_done()
    
    def _show_result_dialog(self, title: str, message: str):
        """显示结果对话框（内容可复制）"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(450, 300)
        dialog.setStyleSheet(self.STYLESHEET)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 可复制的文本区域
        text_edit = QTextEdit()
        text_edit.setPlainText(message)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        layout.addWidget(text_edit)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
