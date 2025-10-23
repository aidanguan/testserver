"""
Playwright录制脚本API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import subprocess
import os
import tempfile
import json
import uuid
import asyncio
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.api.dependencies import get_current_user
from app.services.llm_service import LLMService
from app.utils.encryption import decrypt_api_key

router = APIRouter(tags=["录制脚本"])

# 存储录制会话
recording_sessions = {}


class StartRecordRequest(BaseModel):
    """开始录制请求"""
    target_url: str
    project_id: int


class RecordSessionResponse(BaseModel):
    """录制会话响应"""
    session_id: str
    status: str
    message: str
    port: Optional[int] = None


class ConvertCodeRequest(BaseModel):
    """转换代码请求"""
    playwright_code: str


class ConvertCodeResponse(BaseModel):
    """转换代码响应"""
    playwright_script: Dict[str, Any]


def convert_playwright_to_json(playwright_code: str, project: Project) -> Dict[str, Any]:
    """
    使用LLM将Playwright Python代码转换为JSON格式
    
    Args:
        playwright_code: 录制生成的Playwright Python代码
        project: 项目对象（包含LLM配置）
    
    Returns:
        标准化的Playwright脚本JSON
    """
    try:
        # 如果项目配置了LLM，使用LLM转换
        # 类型注释：project 是从数据库查询的实例，属性是字符串类型
        llm_provider: str = project.llm_provider  # type: ignore
        llm_model: str = project.llm_model  # type: ignore
        llm_api_key_encrypted: str = project.llm_api_key  # type: ignore
        llm_base_url: Optional[str] = project.llm_base_url  # type: ignore
        
        if llm_provider and llm_model and llm_api_key_encrypted:
            print("使用LLM转换录制脚本...")
            
            # 解密 API key
            llm_api_key = decrypt_api_key(llm_api_key_encrypted)
            print(f"LLM配置: provider={llm_provider}, model={llm_model}")
            
            llm_service = LLMService(
                provider=llm_provider,
                model=llm_model,
                api_key=llm_api_key,
                base_url=llm_base_url,
                config={"temperature": 0.3, "max_tokens": 2000}
            )
            
            # 构建提示词
            prompt = f"""你是一个Playwright自动化测试专家。请将以下Playwright Python录制代码转换为标准化的JSON格式配置。

Playwright录制代码:
```python
{playwright_code}
```

请生成JSON格式的Playwright脚本配置，包含以下字段：
1. browser: 浏览器类型(chromium/firefox/webkit)，默认chromium
2. viewport: 视口尺寸 {{"width": 1280, "height": 720}}
3. steps: Playwright步骤数组，每个步骤包含：
   - index: 步骤序号（从1开始）
   - action: Playwright操作类型
   - selector: 元素选择器（如果有）
   - value: 输入值或URL（如果有）
   - description: 步骤的中文描述
   - screenshot: 是否截屏（布尔值），默认true
   - duration: 等待时间（仅waitTime动作需要，单位毫秒）

支持的action类型：
- goto: 导航到URL（value为URL）
- click: 点击元素（selector为选择器）
- fill: 填充输入框（selector为选择器，value为输入值）
- select: 选择下拉选项（selector为选择器，value为选项值）
- waitForSelector: 等待元素出现（selector为选择器）
- waitTime: 等待固定时间（duration为毫秒数）
- press: 按键（value为键名，如Enter）
- check: 勾选复选框（selector为选择器）
- uncheck: 取消勾选（selector为选择器）

重要提示：
- 系统会在每个步骤执行后自动等待3秒再截图，确保页面完全加载
- 你不需要在每个步骤后手动添加waitTime，除非有特殊需要

请只返回JSON，不要包含任何其他说明文字或markdown标记。确保JSON格式正确。

示例输出:
{{
  "browser": "chromium",
  "viewport": {{
    "width": 1280,
    "height": 720
  }},
  "steps": [
    {{
      "index": 1,
      "action": "goto",
      "selector": null,
      "value": "https://example.com",
      "description": "打开网站首页",
      "screenshot": true
    }},
    {{
      "index": 2,
      "action": "click",
      "selector": "#login-button",
      "value": null,
      "description": "点击登录按钮",
      "screenshot": true
    }}
  ]
}}"""
            
            response = llm_service._call_llm(prompt)
            
            # 解析响应
            response = response.strip()
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("`") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            result = json.loads(response)
            print(f"LLM转换成功，生成了 {len(result.get('steps', []))} 个步骤")
            return result
        else:
            # 回退到简单的规则转换
            print("项目未配置LLM，使用规则转换...")
            return _simple_convert(playwright_code)
    
    except Exception as e:
        print(f"LLM转换失败: {str(e)}，回退到规则转换")
        import traceback
        traceback.print_exc()
        return _simple_convert(playwright_code)


def _simple_convert(playwright_code: str) -> Dict[str, Any]:
    """
    简单的规则转换（回退方案）
    """
    steps = []
    step_index = 1
    
    lines = playwright_code.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行和注释
        if not line or line.startswith('#') or line.startswith('import') or line.startswith('from'):
            continue
        
        step = {
            "index": step_index,
            "screenshot": True
        }
        
        # page.goto("url")
        if 'page.goto(' in line:
            url = line.split('page.goto(')[1].split(')')[0].strip('"\'')
            step["action"] = "goto"
            step["value"] = url
            step["description"] = f"打开页面 {url}"
            step["selector"] = None
            steps.append(step)
            step_index += 1
        
        # page.fill("selector", "value")
        elif 'page.fill(' in line:
            parts = line.split('page.fill(')[1].split(')')[0].split(',')
            selector = parts[0].strip().strip('"\'')
            value = parts[1].strip().strip('"\'')
            step["action"] = "fill"
            step["selector"] = selector
            step["value"] = value
            step["description"] = f"输入: {value}"
            steps.append(step)
            step_index += 1
        
        # page.click("selector")
        elif 'page.click(' in line:
            selector = line.split('page.click(')[1].split(')')[0].strip('"\'')
            step["action"] = "click"
            step["selector"] = selector
            step["value"] = None
            step["description"] = f"点击元素"
            steps.append(step)
            step_index += 1
        
        # page.select_option("selector", "value")
        elif 'page.select_option(' in line:
            parts = line.split('page.select_option(')[1].split(')')[0].split(',')
            selector = parts[0].strip().strip('"\'')
            value = parts[1].strip().strip('"\'')
            step["action"] = "select"
            step["selector"] = selector
            step["value"] = value
            step["description"] = f"选择: {value}"
            steps.append(step)
            step_index += 1
        
        # page.wait_for_selector("selector")
        elif 'page.wait_for_selector(' in line:
            selector = line.split('page.wait_for_selector(')[1].split(')')[0].strip('"\'')
            step["action"] = "waitForSelector"
            step["selector"] = selector
            step["value"] = None
            step["description"] = "等待元素出现"
            steps.append(step)
            step_index += 1
        
        # page.wait_for_timeout(ms)
        elif 'page.wait_for_timeout(' in line:
            duration = line.split('page.wait_for_timeout(')[1].split(')')[0].strip()
            step["action"] = "waitTime"
            step["selector"] = None
            step["value"] = None
            step["duration"] = int(duration)
            step["description"] = f"等待 {int(duration)/1000} 秒"
            step["screenshot"] = False
            steps.append(step)
            step_index += 1
    
    return {
        "browser": "chromium",
        "viewport": {
            "width": 1280,
            "height": 720
        },
        "steps": steps
    }


@router.post("/record/start", response_model=RecordSessionResponse)
async def start_record(
    request: StartRecordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    启动Playwright Codegen录制会话
    
    在后台启动codegen进程，用户可以在本地浏览器中操作
    """
    # 验证项目存在
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 生成会话ID
    session_id = str(uuid.uuid4())
    
    # 创建临时输出文件
    output_dir = os.path.join(tempfile.gettempdir(), "playwright_recordings")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{session_id}.py")
    
    try:
        # 启动playwright codegen
        cmd = [
            "python", "-m", "playwright", "codegen",
            request.target_url,
            "-o", output_file,
            "--target", "python"
        ]
        
        print(f"尝试启动录制: {' '.join(cmd)}")
        
        # 在后台启动进程
        try:
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Unix/Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Playwright 未安装或无法找到 python 命令，请确保已安装 Playwright"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"启动进程失败: {str(e)}"
            )
        
        # 保存会话信息
        recording_sessions[session_id] = {
            "process": process,
            "output_file": output_file,
            "start_time": datetime.utcnow(),
            "target_url": request.target_url,
            "project_id": request.project_id,
            "user_id": current_user.id
        }
        
        print(f"录制会话已启动: {session_id}")
        
        return RecordSessionResponse(
            session_id=session_id,
            status="recording",
            message="录制已启动，请在弹出的浏览器窗口中操作"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"录制启动异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动录制失败: {str(e)}"
        )


@router.post("/record/{session_id}/stop")
async def stop_record(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    停止录制会话
    """
    if session_id not in recording_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="录制会话不存在"
        )
    
    session = recording_sessions[session_id]
    
    # 获取项目信息
    project = db.query(Project).filter(Project.id == session["project_id"]).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 终止进程
    try:
        session["process"].terminate()
        session["process"].wait(timeout=5)
    except:
        session["process"].kill()
    
    # 读取生成的代码
    output_file = session["output_file"]
    playwright_code = ""
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            playwright_code = f.read()
    
    # 转换为JSON（传入project对象用于LLM转换）
    playwright_script = convert_playwright_to_json(playwright_code, project)
    
    # 清理会话
    del recording_sessions[session_id]
    
    return {
        "status": "stopped",
        "playwright_code": playwright_code,
        "playwright_script": playwright_script
    }


@router.post("/convert", response_model=ConvertCodeResponse)
async def convert_code(
    request: ConvertCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    将Playwright代码转换为JSON格式
    注意：此接口需要project_id来获取LLM配置
    """
    try:
        # 这个接口目前没有project_id，使用简单转换
        # 如果需要LLM转换，前端应该使用stop_record接口
        playwright_script = _simple_convert(request.playwright_code)
        return ConvertCodeResponse(playwright_script=playwright_script)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"转换失败: {str(e)}"
        )


@router.get("/record/guide")
async def get_record_guide():
    """获取录制指南（简化版）"""
    return {
        "title": "录制脚本指南",
        "description": "点击开始录制后，系统会在服务器上打开浏览器窗口，您可以在其中进行操作。录制完成后点击停止，代码会自动转换为JSON格式。",
        "steps": [
            "1. 输入目标网站URL",
            "2. 点击'开始录制'按钮",
            "3. 在弹出的浏览器中进行操作",
            "4. 完成后点击'停止录制'",
            "5. 系统自动转换并填充脚本"
        ],
        "tips": [
            "💡 录制会在服务器上打开浏览器窗口",
            "💡 如果是远程服务器，需要有桌面环境",
            "💡 建议在本地环境使用此功能"
        ]
    }
