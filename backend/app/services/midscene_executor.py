"""
Midscene执行引擎服务
使用 Midscene AI 能力执行测试
"""
import os
import json
import subprocess
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class MidsceneExecutor:
    """Midscene脚本执行器"""
    
    def __init__(self, artifacts_base_path: str, llm_service=None, expected_result: Optional[str] = None, auth_state_path: Optional[str] = None):
        """
        初始化执行器
        
        Args:
            artifacts_base_path: 工件存储基础路径
            llm_service: LLM服务实例（用于结果分析）
            expected_result: 预期结果描述
            auth_state_path: 认证状态文件路径（可选）
        """
        self.artifacts_base_path = artifacts_base_path
        self.llm_service = llm_service
        self.expected_result = expected_result
        self.auth_state_path = auth_state_path  # 新增：认证状态路径
        
        # Midscene 执行器脚本路径
        backend_dir = Path(__file__).parent.parent.parent
        self.midscene_dir = backend_dir / "midscene"
        self.executor_script = self.midscene_dir / "executor.ts"
        
    def execute_script(
        self, 
        script: Dict[str, Any], 
        run_id: int,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行Midscene脚本
        
        Args:
            script: Midscene脚本配置
            run_id: 运行ID
            env_vars: 环境变量（LLM API keys等）
            
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
        
        try:
            # 准备执行环境
            exec_env = os.environ.copy()
            if env_vars:
                exec_env.update(env_vars)
                print(f"🔑 Midscene 环境变量已设置: {list(env_vars.keys())}")
                # 打印 API Key 前缀以验证
                if 'OPENAI_API_KEY' in env_vars:
                    print(f"✅ OPENAI_API_KEY 已设置: {env_vars['OPENAI_API_KEY'][:10]}...")
                if 'OPENAI_BASE_URL' in env_vars:
                    print(f"✅ OPENAI_BASE_URL 已设置: {env_vars['OPENAI_BASE_URL']}")
                if 'MIDSCENE_MODEL_NAME' in env_vars:
                    print(f"✅ MIDSCENE_MODEL_NAME 已设置: {env_vars['MIDSCENE_MODEL_NAME']}")
                if 'MIDSCENE_USE_QWEN_VL' in env_vars:
                    print(f"✅ MIDSCENE_USE_QWEN_VL 已设置: {env_vars['MIDSCENE_USE_QWEN_VL']}")
            else:
                print(f"⚠️ 警告: 未提供环境变量，Midscene 可能无法使用 LLM 功能")
            
            # 检查脚本类型
            print(f"📦 脚本类型: {type(script)}")
            print(f"📦 脚本内容: {script}")
            
            # 准备命令行参数
            try:
                script_json = json.dumps(script, ensure_ascii=False)
            except Exception as json_error:
                print(f"❌ JSON 序列化错误: {json_error}")
                raise
            
            expected_result = self.expected_result or ""
            auth_state_arg = self.auth_state_path if self.auth_state_path else ""
            
            # 根据操作系统选择命令
            is_windows = platform.system() == "Windows"
            
            if is_windows:
                # Windows: 使用 npx.cmd
                cmd = [
                    "npx.cmd",
                    "tsx",
                    str(self.executor_script),
                    script_json,
                    str(run_id),
                    self.artifacts_base_path,
                    expected_result,
                    auth_state_arg  # 新增：传递认证状态路径
                ]
            else:
                # Linux/Mac: 使用 npx
                cmd = [
                    "npx",
                    "tsx",
                    str(self.executor_script),
                    script_json,
                    str(run_id),
                    self.artifacts_base_path,
                    expected_result,
                    auth_state_arg  # 新增：传递认证状态路径
                ]
            
            print(f"执行 Midscene 命令: {' '.join(cmd[:3])}...")
            
            # 执行 - 在 Windows 中文环境下需要指定编码
            process = subprocess.Popen(
                cmd,
                cwd=str(self.midscene_dir),
                env=exec_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 明确指定 UTF-8 编码
                errors='replace',  # 遇到无法解码的字符时替换而不是报错
                shell=is_windows  # Windows 需要 shell=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=300)  # 5分钟超时
            except subprocess.TimeoutExpired:
                process.kill()
                result["error_message"] = "执行超时（超过5分钟）"
                result["success"] = False
                return result
            
            # 检查是否成功获取输出
            if stdout is None:
                stdout = ""
            if stderr is None:
                stderr = ""
            
            print(f"📤 STDOUT 长度: {len(stdout)}")
            print(f"📤 STDERR 长度: {len(stderr)}")
            if stderr:
                print(f"⚠️ STDERR 内容:\n{stderr}")
            
            # 解析结果
            if stdout and "===MIDSCENE_RESULT_START===" in stdout:
                start_idx = stdout.find("===MIDSCENE_RESULT_START===") + len("===MIDSCENE_RESULT_START===")
                end_idx = stdout.find("===MIDSCENE_RESULT_END===")
                if end_idx > start_idx:
                    result_json = stdout[start_idx:end_idx].strip()
                    midscene_result = json.loads(result_json)
                    result.update(midscene_result)
            else:
                # 没有找到结果标记，说明执行失败
                error_msg = "Midscene 执行失败"
                if stdout:
                    error_msg += f"\nSTDOUT (\u524d500\u5b57\u7b26):\n{stdout[:500]}"
                if stderr:
                    error_msg += f"\nSTDERR (\u524d500\u5b57\u7b26):\n{stderr[:500]}"
                result["error_message"] = error_msg
                result["success"] = False
            
        except subprocess.TimeoutExpired:
            result["error_message"] = "执行超时（超过5分钟）"
            result["success"] = False
            
        except Exception as e:
            import traceback
            print(f"❌ 执行异常详细信息:")
            print(f"  - 错误类型: {type(e).__name__}")
            print(f"  - 错误消息: {str(e)}")
            traceback.print_exc()
            result["error_message"] = f"执行异常: {str(e)}"
            result["success"] = False
        
        return result
    
    def check_installation(self) -> Dict[str, Any]:
        """
        检查 Midscene 是否已正确安装
        
        Returns:
            检查结果 {installed, node_modules_exists, error}
        """
        try:
            node_modules = self.midscene_dir / "node_modules"
            
            return {
                "installed": node_modules.exists(),
                "node_modules_exists": node_modules.exists(),
                "midscene_dir": str(self.midscene_dir),
                "executor_script": str(self.executor_script),
                "error": None
            }
        except Exception as e:
            return {
                "installed": False,
                "node_modules_exists": False,
                "error": str(e)
            }
    
    def install_dependencies(self) -> Dict[str, Any]:
        """
        安装 Midscene 依赖
        
        Returns:
            安装结果 {success, message}
        """
        try:
            # 运行 npm install
            process = subprocess.run(
                ["npm", "install"],
                cwd=str(self.midscene_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": "Midscene 依赖安装成功"
                }
            else:
                return {
                    "success": False,
                    "message": f"安装失败: {process.stderr}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"安装异常: {str(e)}"
            }
