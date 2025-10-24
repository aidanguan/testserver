"""
Playwright 认证状态管理服务
用于保存和加载浏览器的登录状态
"""
import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from playwright.sync_api import BrowserContext


class AuthStateManager:
    """认证状态管理器"""
    
    def __init__(self, storage_base_path: Optional[str] = None):
        """
        初始化管理器
        
        Args:
            storage_base_path: 认证状态存储基础路径
        """
        if storage_base_path is None:
            # 默认存储在 backend/auth_states 目录
            storage_base_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "auth_states"
            )
        
        self.storage_base_path = storage_base_path
        os.makedirs(self.storage_base_path, exist_ok=True)
    
    def get_state_file_path(self, project_id: int) -> str:
        """
        获取项目的认证状态文件路径
        
        Args:
            project_id: 项目ID
            
        Returns:
            认证状态文件路径
        """
        return os.path.join(self.storage_base_path, f"project_{project_id}_auth.json")
    
    def has_auth_state(self, project_id: int) -> bool:
        """
        检查项目是否有保存的认证状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否存在认证状态
        """
        state_file = self.get_state_file_path(project_id)
        return os.path.exists(state_file)
    
    def save_auth_state(self, project_id: int, context: BrowserContext) -> Dict[str, Any]:
        """
        保存浏览器上下文的认证状态
        
        Args:
            project_id: 项目ID
            context: Playwright BrowserContext
            
        Returns:
            保存结果 {success, message, file_path}
        """
        try:
            state_file = self.get_state_file_path(project_id)
            print(f"   - 目标文件: {state_file}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(state_file), exist_ok=True)
            print(f"   - 目录已准备")
            
            # 保存认证状态到文件
            print(f"   - 开始调用 context.storage_state()...")
            context.storage_state(path=state_file)
            print(f"   - storage_state() 调用成功")
            
            # 读取并验证
            print(f"   - 读取并验证文件...")
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            cookies_count = len(state_data.get('cookies', []))
            origins_count = len(state_data.get('origins', []))
            
            print(f"   - 验证成功: {cookies_count} 个 cookies, {origins_count} 个 origins")
            
            return {
                "success": True,
                "message": f"认证状态已保存（包含 {cookies_count} 个 cookies）",
                "file_path": state_file,
                "cookies_count": cookies_count,
                "origins_count": origins_count
            }
        
        except Exception as e:
            print(f"   - 保存失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"保存认证状态失败: {str(e)}",
                "file_path": None
            }
    
    def load_auth_state(self, project_id: int) -> Optional[str]:
        """
        加载项目的认证状态文件路径
        
        Args:
            project_id: 项目ID
            
        Returns:
            认证状态文件路径，如果不存在返回 None
        """
        state_file = self.get_state_file_path(project_id)
        
        if os.path.exists(state_file):
            return state_file
        
        return None
    
    def delete_auth_state(self, project_id: int) -> Dict[str, Any]:
        """
        删除项目的认证状态
        
        Args:
            project_id: 项目ID
            
        Returns:
            删除结果 {success, message}
        """
        try:
            state_file = self.get_state_file_path(project_id)
            
            if os.path.exists(state_file):
                os.remove(state_file)
                return {
                    "success": True,
                    "message": "认证状态已删除"
                }
            else:
                return {
                    "success": False,
                    "message": "认证状态不存在"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"删除认证状态失败: {str(e)}"
            }
    
    def get_auth_state_info(self, project_id: int) -> Dict[str, Any]:
        """
        获取认证状态信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            认证状态信息
        """
        state_file = self.get_state_file_path(project_id)
        
        if not os.path.exists(state_file):
            return {
                "exists": False,
                "file_path": state_file
            }
        
        try:
            # 读取状态文件
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 获取文件修改时间
            stat_info = os.stat(state_file)
            
            return {
                "exists": True,
                "file_path": state_file,
                "cookies_count": len(state_data.get('cookies', [])),
                "origins_count": len(state_data.get('origins', [])),
                "file_size": stat_info.st_size,
                "modified_time": stat_info.st_mtime
            }
        
        except Exception as e:
            return {
                "exists": True,
                "file_path": state_file,
                "error": str(e)
            }
