"""
Playwright执行引擎服务
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from pathlib import Path


class PlaywrightExecutor:
    """Playwright脚本执行器"""
    
    def __init__(self, artifacts_base_path: str, llm_service=None, expected_result: Optional[str] = None, auth_state_path: Optional[str] = None):
        """
        初始化执行器
        
        Args:
            artifacts_base_path: 工件存储基础路径
            llm_service: LLM服务实例（用于视觉分析）
            expected_result: 预期结果描述
            auth_state_path: 认证状态文件路径（可选）
        """
        self.artifacts_base_path = artifacts_base_path
        self.llm_service = llm_service
        self.expected_result = expected_result
        self.auth_state_path = auth_state_path  # 新增：认证状态路径
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    def execute_script(
        self, 
        script: Dict[str, Any], 
        run_id: int
    ) -> Dict[str, Any]:
        """
        执行Playwright脚本
        
        Args:
            script: Playwright脚本配置
            run_id: 运行ID
            
        Returns:
            执行结果 {success, steps, error_message, artifacts_path}
        """
        # 创建工件目录
        run_artifacts_path = os.path.join(self.artifacts_base_path, f"runs/{run_id}")
        screenshots_path = os.path.join(run_artifacts_path, "screenshots")
        logs_path = os.path.join(run_artifacts_path, "logs")
        network_path = os.path.join(run_artifacts_path, "network")
        
        os.makedirs(screenshots_path, exist_ok=True)
        os.makedirs(logs_path, exist_ok=True)
        os.makedirs(network_path, exist_ok=True)
        
        # 执行结果
        result = {
            "success": False,
            "steps": [],
            "error_message": None,
            "artifacts_path": run_artifacts_path,
            "console_logs": []
        }
        
        console_logs = []
        
        try:
            # 启动Playwright
            self.playwright = sync_playwright().start()
            
            # 获取浏览器类型
            browser_type = script.get("browser", "chromium")
            if browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(headless=False)  # 改为有头模式，可以看到浏览器
            elif browser_type == "firefox":
                self.browser = self.playwright.firefox.launch(headless=False)  # 改为有头模式
            elif browser_type == "webkit":
                self.browser = self.playwright.webkit.launch(headless=False)  # 改为有头模式
            else:
                self.browser = self.playwright.chromium.launch(headless=False)  # 改为有头模式
            
            # 创建上下文（支持加载认证状态）
            viewport = script.get("viewport", {"width": 1280, "height": 720})
            context_options = {
                "viewport": viewport,
                "record_har_path": os.path.join(network_path, "traffic.har")
            }
            
            # 如果有认证状态文件，加载它
            if self.auth_state_path and os.path.exists(self.auth_state_path):
                context_options["storage_state"] = self.auth_state_path
                print(f"✅ 加载认证状态: {self.auth_state_path}")
            
            self.context = self.browser.new_context(**context_options)
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 监听控制台日志
            def handle_console(msg):
                log_entry = f"[{msg.type}] {msg.text}"
                console_logs.append(log_entry)
            
            self.page.on("console", handle_console)
            
            # 执行步骤
            steps = script.get("steps", [])
            total_steps = len(steps)
            for idx, step in enumerate(steps):
                is_last_step = (idx == total_steps - 1)  # 判断是否是最后一步
                step_result = self._execute_step(step, screenshots_path, is_last_step)
                result["steps"].append(step_result)
                
                # 如果步骤失败,停止执行
                if step_result["status"] == "failed":
                    break
            
            # 保存控制台日志
            with open(os.path.join(logs_path, "console.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(console_logs))
            
            result["console_logs"] = console_logs
            result["success"] = all(s["status"] == "success" for s in result["steps"])
            
        except Exception as e:
            result["error_message"] = str(e)
            result["success"] = False
            
        finally:
            # 清理资源
            self._cleanup()
        
        return result
    
    def _execute_step(self, step: Dict[str, Any], screenshots_path: str, is_last_step: bool = False) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            step: 步骤配置
            screenshots_path: 截图保存路径
            is_last_step: 是否是最后一步（不再使用，保留参数兼容性）
            
        Returns:
            步骤执行结果
        """
        step_result = {
            "index": step.get("index", 0),
            "description": step.get("description", ""),
            "status": "success",
            "screenshot_path": None,
            "error_message": None,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        
        try:
            action = step.get("action")
            selector = step.get("selector")
            value = step.get("value")
            timeout = step.get("timeout", 30000)
            
            # 执行对应的操作
            if action == "goto":
                self.page.goto(value, timeout=timeout, wait_until="networkidle")
            
            elif action == "click":
                self.page.click(selector, timeout=timeout)
            
            elif action == "fill":
                self.page.fill(selector, value, timeout=timeout)
            
            elif action == "select":
                self.page.select_option(selector, value, timeout=timeout)
            
            elif action == "waitForSelector":
                self.page.wait_for_selector(selector, timeout=timeout)
            
            elif action == "waitTime":
                duration = step.get("duration", 1000)
                self.page.wait_for_timeout(duration)
            
            elif action == "screenshot":
                screenshot_name = f"step_{step['index']}.png"
                screenshot_path = os.path.join(screenshots_path, screenshot_name)
                self.page.screenshot(path=screenshot_path, full_page=True)
                # 保存相对路径
                relative_path = screenshot_path.replace(self.artifacts_base_path, "").replace("\\", "/").lstrip("/")
                step_result["screenshot_path"] = relative_path
            
            elif action == "assertText":
                element = self.page.locator(selector)
                text = element.inner_text(timeout=timeout)
                expected = step.get("expected", "")
                if expected not in text:
                    raise Exception(f"文本断言失败: 期望包含'{expected}', 实际为'{text}'")
            
            elif action == "assertVisible":
                element = self.page.locator(selector)
                if not element.is_visible(timeout=timeout):
                    raise Exception(f"元素不可见: {selector}")
            
            # 默认截屏（不再进行单步视觉分析，只保存截图供后续整体分析）
            if step.get("screenshot", True) and action != "screenshot":
                # 等待3秒让页面完全加载后再截图
                self.page.wait_for_timeout(3000)
                screenshot_name = f"step_{step['index']}.png"
                screenshot_path = os.path.join(screenshots_path, screenshot_name)
                self.page.screenshot(path=screenshot_path, full_page=True)
                # 保存相对路径（相对于 artifacts 目录），以便前端可以访问
                relative_path = screenshot_path.replace(self.artifacts_base_path, "").replace("\\", "/").lstrip("/")
                step_result["screenshot_path"] = relative_path
            
        except Exception as e:
            step_result["status"] = "failed"
            step_result["error_message"] = str(e)
        
        step_result["end_time"] = datetime.utcnow().isoformat()
        return step_result
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"清理资源时出错: {e}")
    
    def save_auth_state(self, output_path: str) -> Dict[str, Any]:
        """
        保存当前浏览器上下文的认证状态
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            保存结果
        """
        try:
            if not self.context:
                return {
                    "success": False,
                    "message": "浏览器上下文未初始化"
                }
            
            # 保存认证状态
            self.context.storage_state(path=output_path)
            
            # 读取并验证
            with open(output_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            return {
                "success": True,
                "message": f"认证状态已保存（包含 {len(state_data.get('cookies', []))} 个 cookies）",
                "file_path": output_path,
                "cookies_count": len(state_data.get('cookies', [])),
                "origins_count": len(state_data.get('origins', []))
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"保存认证状态失败: {str(e)}"
            }
