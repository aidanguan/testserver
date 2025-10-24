""" 
认证状态管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.api.dependencies import get_current_user
from app.services.auth_state_manager import AuthStateManager
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import threading
import queue


router = APIRouter(tags=["认证状态管理"])


class AuthStateInfoResponse(BaseModel):
    """认证状态信息响应"""
    exists: bool
    file_path: str
    cookies_count: int = 0
    origins_count: int = 0
    file_size: int = 0
    modified_time: float = 0


class CreateAuthStateRequest(BaseModel):
    """创建认证状态请求"""
    login_url: str


@router.get("/projects/{project_id}/auth-state", response_model=AuthStateInfoResponse)
async def get_auth_state_info(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的认证状态信息"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 获取认证状态信息
    auth_manager = AuthStateManager()
    info = auth_manager.get_auth_state_info(project_id)
    
    return AuthStateInfoResponse(**info)


@router.delete("/projects/{project_id}/auth-state")
async def delete_auth_state(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目的认证状态"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 删除认证状态
    auth_manager = AuthStateManager()
    result = auth_manager.delete_auth_state(project_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result


# 全局变量，用于跟踪浏览器状态
auth_browser_sessions = {}


@router.post("/projects/{project_id}/auth-state/create")
async def create_auth_state(
    project_id: int,
    request: CreateAuthStateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建或更新项目的认证状态（异步打开浏览器）"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查是否已经有浏览器会话在运行
    if project_id in auth_browser_sessions:
        return {
            "success": False,
            "message": "已经有一个浏览器会话在运行，请先完成或取消"
        }
    
    # 在后台线程中启动浏览器，并添加命令队列
    def start_browser_session():
        try:
            print(f"\n🚀 为项目 {project_id} 启动浏览器会话...")
            
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # 创建命令队列和结果队列
            command_queue = queue.Queue()
            result_queue = queue.Queue()
            
            # 保存到全局字典
            auth_browser_sessions[project_id] = {
                'playwright': playwright,
                'browser': browser,
                'context': context,
                'page': page,
                'ready': False,
                'command_queue': command_queue,
                'result_queue': result_queue,
                'running': True
            }
            
            print(f"✅ 浏览器已启动，打开登录页面: {request.login_url}")
            page.goto(request.login_url)
            
            # 标记为就绪
            auth_browser_sessions[project_id]['ready'] = True
            print(f"✅ 浏览器会话就绪，等待用户登录...")
            
            # 在这个线程中监听命令
            while auth_browser_sessions.get(project_id, {}).get('running', False):
                try:
                    # 等待命令，超时1秒后检查一次
                    cmd = command_queue.get(timeout=1)
                    
                    if cmd == 'save':
                        print(f"\n💾 [线程内] 收到保存命令...")
                        try:
                            auth_manager = AuthStateManager()
                            result = auth_manager.save_auth_state(project_id, context)
                            print(f"   - 保存结果: {result}")
                            
                            # 关闭浏览器
                            print(f"\n🔒 关闭浏览器...")
                            browser.close()
                            playwright.stop()
                            print(f"   - 浏览器已关闭")
                            
                            result_queue.put({"success": True, "data": result})
                            auth_browser_sessions[project_id]['running'] = False
                            break
                            
                        except Exception as e:
                            print(f"   - 保存失败: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            result_queue.put({"success": False, "error": str(e)})
                            auth_browser_sessions[project_id]['running'] = False
                            break
                    
                    elif cmd == 'cancel':
                        print(f"\n❌ [线程内] 收到取消命令...")
                        browser.close()
                        playwright.stop()
                        result_queue.put({"success": True, "message": "已取消"})
                        auth_browser_sessions[project_id]['running'] = False
                        break
                        
                except queue.Empty:
                    # 没有命令，继续等待
                    continue
            
            print(f"\n🟢 浏览器线程退出")
            
        except Exception as e:
            print(f"❌ 启动浏览器失败: {str(e)}")
            if project_id in auth_browser_sessions:
                del auth_browser_sessions[project_id]
    
    # 启动后台线程
    thread = threading.Thread(target=start_browser_session)
    thread.daemon = True
    thread.start()
    
    return {
        "success": True,
        "message": "浏览器正在启动，请在浏览器中完成登录，然后点击'保存登录状态'按钮",
        "session_id": project_id
    }


@router.post("/projects/{project_id}/auth-state/save")
async def save_auth_state(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """保存当前浏览器会话的认证状态"""
    print(f"\n========== 开始保存认证状态 (Project ID: {project_id}) ==========")
    
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        print(f"❌ 项目不存在: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    print(f"✅ 项目存在: {project.name}")
    
    # 检查是否有浏览器会话
    if project_id not in auth_browser_sessions:
        print(f"❌ 没有活跃的浏览器会话")
        print(f"当前会话列表: {list(auth_browser_sessions.keys())}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有活跃的浏览器会话，请先创建登录会话"
        )
    
    session = auth_browser_sessions[project_id]
    print(f"✅ 找到浏览器会话")
    print(f"   - Ready: {session.get('ready')}")
    
    if not session.get('ready'):
        print(f"❌ 浏览器会话还未就绪")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="浏览器会话还未就绪，请稍后重试"
        )
    
    try:
        # 发送保存命令到浏览器线程
        command_queue = session.get('command_queue')
        result_queue = session.get('result_queue')
        
        if not command_queue or not result_queue:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="浏览器会话状态异常"
            )
        
        print(f"\n📤 发送保存命令到浏览器线程...")
        command_queue.put('save')
        
        # 等待结果，最多30秒
        print(f"⏳ 等待浏览器线程处理...")
        try:
            result_data = result_queue.get(timeout=30)
        except queue.Empty:
            print(f"❌ 保存操作超时")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="保存操作超时"
            )
        
        # 清理会话
        if project_id in auth_browser_sessions:
            del auth_browser_sessions[project_id]
            print(f"   - 会话已清理")
        
        if result_data.get("success"):
            print(f"\n✅ 保存成功!")
            print(f"========== 保存完成 ==========\n")
            return result_data["data"]
        else:
            error_msg = result_data.get('error', '未知错误')
            print(f"\n❌ 保存失败: {error_msg}")
            print(f"========== 保存失败 ==========\n")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"保存失败: {error_msg}"
            )
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"\n❌❌❌ 异常错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 清理会话
        if project_id in auth_browser_sessions:
            del auth_browser_sessions[project_id]
            print(f"   - 会话已清理")
        
        print(f"========== 保存异常 ==========\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存失败: {str(e)}"
        )


@router.post("/projects/{project_id}/auth-state/cancel")
async def cancel_auth_state(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消当前浏览器会话"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查是否有浏览器会话
    if project_id not in auth_browser_sessions:
        return {
            "success": True,
            "message": "没有活跃的浏览器会话"
        }
    
    try:
        session = auth_browser_sessions[project_id]
        command_queue = session.get('command_queue')
        result_queue = session.get('result_queue')
        
        if command_queue and result_queue:
            # 发送取消命令
            command_queue.put('cancel')
            # 等待结果
            try:
                result_queue.get(timeout=10)
            except queue.Empty:
                pass
        
        # 清理会话
        if project_id in auth_browser_sessions:
            del auth_browser_sessions[project_id]
        
        return {
            "success": True,
            "message": "浏览器会话已取消"
        }
    
    except Exception as e:
        if project_id in auth_browser_sessions:
            del auth_browser_sessions[project_id]
        
        return {
            "success": True,
            "message": f"浏览器会话已清理: {str(e)}"
        }


@router.get("/projects/{project_id}/auth-state/status")
async def get_auth_session_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取浏览器会话状态"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project_id in auth_browser_sessions:
        session = auth_browser_sessions[project_id]
        return {
            "has_session": True,
            "ready": session.get('ready', False)
        }
    else:
        return {
            "has_session": False,
            "ready": False
        }
