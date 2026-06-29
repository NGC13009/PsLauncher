# coding = utf-8
#
# @File name:       test_process_control.py
# @brief:           功能层：进程控制测试（进程树强杀、Ctrl+C 信号、无残留子进程）
# @Author:          NGC13009
# @History:         2026-06-29		Create

import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# ============================================================
# 功能层测试：进程控制
# 使用 mock 避免实际启动进程
# 注意：TerminalTab 继承 QWidget，必须通过 __init__ 创建实例
# 不能使用 __new__，否则 self.terminal 等属性未初始化
# ============================================================


class TestTerminateProcessTree:
    """_terminate_process_tree 方法测试"""

    def test_terminate_with_psutil(self, qapp, sample_scripts_dir):
        """使用 psutil 终止进程树"""
        from tabClass import TerminalTab
        # 创建 mock psutil.Process
        mock_parent = MagicMock()
        mock_child = MagicMock()
        mock_parent.children.return_value = [mock_child]
        mock_parent.pid = 1234
        mock_child.pid = 5678

        with patch('tabClass.psutil.Process', return_value=mock_parent):
            # 创建真实 TerminalTab 实例，但 mock 掉 process
            script_path = str(sample_scripts_dir / "test_script.ps1")
            tab = TerminalTab(script_path, "Consolas", True, True)
            tab.process = MagicMock()
            tab.process.processId.return_value = 1234
            tab._terminate_process_tree(1234)

            # 验证子进程被终止
            mock_child.terminate.assert_called_once()
            # 验证父进程被终止
            mock_parent.terminate.assert_called_once()

    def test_terminate_without_psutil_windows(self, qapp, sample_scripts_dir):
        """无 psutil 时使用 taskkill（Windows）"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.processId.return_value = 1234

        # 模拟 psutil 不可用：让 psutil.Process 抛出 ImportError
        # 注意：_terminate_process_tree 的 except ImportError 分支处理无 psutil 的情况
        import tabClass
        with patch.object(tabClass.psutil, 'Process', side_effect=ImportError("No psutil")):
            with patch('tabClass.os.name', 'nt'):
                with patch('tabClass.subprocess.run') as mock_run:
                    tab._terminate_process_tree(1234)
                    # 验证调用了 taskkill
                    mock_run.assert_called_once()
                    args = mock_run.call_args[0][0]
                    assert 'taskkill' in args
                    assert '/T' in args  # 树形终止
                    assert '/F' in args  # 强制
                    assert '1234' in args

    @pytest.mark.skipif(os.name != 'posix', reason="仅 Linux/macOS 支持 os.killpg")
    def test_terminate_without_psutil_linux(self, qapp, sample_scripts_dir):
        """无 psutil 时使用 os.killpg（Linux）"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.processId.return_value = 1234

        with patch.dict('sys.modules', {'psutil': None}):
            with patch('tabClass.os.name', 'posix'):
                with patch('tabClass.os.killpg') as mock_killpg:
                    with patch('tabClass.os.getpgid', return_value=1234):
                        import importlib
                        import tabClass as tc
                        importlib.reload(tc)
                        try:
                            tab._terminate_process_tree(1234)
                            assert mock_killpg.call_count >= 1
                        finally:
                            importlib.reload(tc)

    def test_terminate_already_stopped_process(self, qapp, sample_scripts_dir):
        """已停止的进程不应调用终止逻辑"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.state.return_value = 0  # QProcess.NotRunning

        with patch.object(tab, '_terminate_process_tree') as mock_terminate:
            tab.stop_process()
            mock_terminate.assert_not_called()


class TestSendCtrlC:
    """Ctrl+C 中断信号测试"""

    def test_send_ctrl_c_writes_0x03(self, qapp, sample_scripts_dir):
        """send_ctrl_c 应向进程写入 0x03 字节"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.state.return_value = 2  # QProcess.Running

        tab.send_ctrl_c()
        # 验证写入了 0x03 字节
        tab.process.write.assert_called_with(b'\x03')

    def test_send_ctrl_c_no_process(self, qapp, sample_scripts_dir):
        """无运行进程时 send_ctrl_c 不应崩溃"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = None

        # 不应抛出异常
        tab.send_ctrl_c()

    def test_send_ctrl_c_process_not_running(self, qapp, sample_scripts_dir):
        """进程未运行时 send_ctrl_c 不应写入"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.state.return_value = 0  # QProcess.NotRunning

        tab.send_ctrl_c()
        tab.process.write.assert_not_called()


class TestProcessLifecycle:
    """进程生命周期管理测试"""

    def test_stop_process_cleanup(self, qapp, sample_scripts_dir):
        """stop_process 应清理 process 对象"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab(script_path, "Consolas", True, True)
        tab.process = MagicMock()
        tab.process.state.return_value = 2  # QProcess.Running
        tab.process.processId.return_value = 1234

        with patch.object(tab, '_terminate_process_tree'):
            tab.stop_process()
            # 验证 process 被清理
            assert tab.process is None

    def test_start_process_sets_working_dir(self, qapp, sample_scripts_dir):
        """start_process 应设置工作目录为脚本所在目录"""
        from tabClass import TerminalTab
        script_path = str(sample_scripts_dir / "test_script.ps1")
        tab = TerminalTab.__new__(TerminalTab)
        tab.script_path = script_path
        tab.process = MagicMock()
        tab.terminal = MagicMock()
        tab.terminal.textCursor.return_value = MagicMock()
        tab.terminal.toPlainText.return_value = ""
        tab.append_output = MagicMock()
        tab.ansi_regex = __import__('re').compile(r'\x1b\[([\d;]*)m')

        tab.start_process()
        # 验证设置了工作目录
        expected_dir = str(sample_scripts_dir)
        tab.process.setWorkingDirectory.assert_called_with(expected_dir)