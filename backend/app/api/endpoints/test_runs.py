"""
测试执行API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.test_case import TestCase
from app.models.test_run import TestRun, TestRunStatus, LLMVerdict
from app.models.step_execution import StepExecution, StepStatus
from app.models.project import Project
from app.schemas.test_run import TestRunResponse, TestRunDetailResponse, StepExecutionResponse
from app.services.playwright_executor import PlaywrightExecutor
from app.services.llm_service import LLMService
from app.utils.encryption import decrypt_api_key
from app.api.dependencies import get_current_user
from app.config import settings

router = APIRouter(tags=["测试执行"])


def execute_test_background(
    test_run_id: int,
    test_case_id: int,
    db_url: str
):
    """后台执行测试任务"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建新的数据库会话
    # SQLite 需要 check_same_thread=False
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 获取测试运行记录
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            return
        
        # 获取测试用例
        test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
        if not test_case:
            test_run.status = TestRunStatus.ERROR
            test_run.error_message = "测试用例不存在"
            test_run.end_time = datetime.utcnow()
            db.commit()
            return
        
        # 获取项目
        project = db.query(Project).filter(Project.id == test_case.project_id).first()
        if not project:
            test_run.status = TestRunStatus.ERROR
            test_run.error_message = "项目不存在"
            test_run.end_time = datetime.utcnow()
            db.commit()
            return
        
        # 执行Playwright脚本
        # 初始化LLM服务用于实时视觉分析
        llm_service = None
        try:
            api_key = decrypt_api_key(project.llm_api_key)
            llm_service = LLMService(
                provider=project.llm_provider,
                model=project.llm_model,
                api_key=api_key,
                base_url=project.llm_base_url,
                config=project.llm_config
            )
            print(f"\ud83e\udd16 LLM服务初始化成功，将进行实时视觉分析")
        except Exception as e:
            print(f"\u26a0\ufe0f LLM服务初始化失败: {e}，将跳过视觉分析")
        
        executor = PlaywrightExecutor(
            artifacts_base_path=settings.ARTIFACTS_PATH,
            llm_service=llm_service,
            expected_result=test_case.expected_result
        )
        exec_result = executor.execute_script(
            script=test_case.playwright_script,
            run_id=test_run_id
        )
        
        # 保存步骤执行记录
        for step_data in exec_result.get("steps", []):
            step = StepExecution(
                test_run_id=test_run_id,
                step_index=step_data["index"],
                step_description=step_data["description"],
                status=StepStatus.SUCCESS if step_data["status"] == "success" else StepStatus.FAILED,
                screenshot_path=step_data.get("screenshot_path"),
                vision_observation=step_data.get("vision_observation"),  # 保存视觉观察结果
                start_time=datetime.fromisoformat(step_data["start_time"]),
                end_time=datetime.fromisoformat(step_data["end_time"]) if step_data.get("end_time") else None,
                error_message=step_data.get("error_message")
            )
            db.add(step)
        
        db.commit()
        
        # 更新运行记录
        test_run.artifacts_path = exec_result.get("artifacts_path")
        
        if exec_result.get("success"):
            test_run.status = TestRunStatus.SUCCESS
            
            # 使用LLM判定结果
            try:
                api_key = decrypt_api_key(project.llm_api_key)
                llm_service = LLMService(
                    provider=project.llm_provider,
                    model=project.llm_model,
                    api_key=api_key,
                    base_url=project.llm_base_url,
                    config=project.llm_config
                )
                
                # 收集截图路径
                screenshots = [s.get("screenshot_path") for s in exec_result.get("steps", []) if s.get("screenshot_path")]
                
                # LLM判定
                verdict_result = llm_service.analyze_test_result(
                    expected_result=test_case.expected_result,
                    step_screenshots=screenshots,
                    console_logs=exec_result.get("console_logs", []),
                    step_statuses=exec_result.get("steps", [])
                )
                
                # 保存判定结果
                verdict_map = {"passed": LLMVerdict.PASSED, "failed": LLMVerdict.FAILED, "unknown": LLMVerdict.UNKNOWN}
                test_run.llm_verdict = verdict_map.get(verdict_result.get("verdict"), LLMVerdict.UNKNOWN)
                
                # 将完整的判定结果（包括 observations）序列化为 JSON 存储
                import json
                test_run.llm_reason = json.dumps(verdict_result, ensure_ascii=False)
                
            except Exception as e:
                print(f"LLM判定失败: {e}")
                test_run.llm_verdict = LLMVerdict.UNKNOWN
                test_run.llm_reason = f"LLM判定失败: {str(e)}"
        
        else:
            test_run.status = TestRunStatus.FAILED
            test_run.error_message = exec_result.get("error_message")
        
        test_run.end_time = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # 更新为错误状态
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if test_run:
            test_run.status = TestRunStatus.ERROR
            test_run.error_message = str(e)
            test_run.end_time = datetime.utcnow()
            db.commit()
    
    finally:
        db.close()


@router.post("/cases/{case_id}/execute", response_model=TestRunResponse)
async def execute_test_case(
    case_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """执行测试用例"""
    # 获取测试用例
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    # 创建运行记录
    test_run = TestRun(
        test_case_id=case_id,
        status=TestRunStatus.RUNNING,
        trigger_by=current_user.id
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    # 构建数据库URL用于后台任务
    # 使用 SQLite - 需要从 app/api/endpoints/ 往上4层到 backend/
    import os
    # __file__ -> app/api/endpoints/test_runs.py
    # 需要4个 dirname 到达 backend/
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
        "ui_test_platform.db"
    )
    db_url = f"sqlite:///{db_path}"
    print(f"后台任务使用数据库路径: {db_path}")
    
    # 如果需要使用 MySQL，取消下面的注释并注释掉上面的 SQLite 配置
    # from app.config import settings as config_settings
    # db_url = f"mysql+pymysql://{config_settings.DB_USER}:{config_settings.DB_PASSWORD}@{config_settings.DB_HOST}:{config_settings.DB_PORT}/{config_settings.DB_NAME}?charset=utf8mb4"
    
    # 添加后台任务
    background_tasks.add_task(
        execute_test_background,
        test_run.id,
        case_id,
        db_url
    )
    
    return TestRunResponse.model_validate(test_run)


@router.get("/runs/{run_id}", response_model=TestRunDetailResponse)
async def get_test_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取测试运行详情"""
    test_run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运行记录不存在"
        )
    
    # 获取步骤执行记录
    steps = db.query(StepExecution).filter(
        StepExecution.test_run_id == run_id
    ).order_by(StepExecution.step_index).all()
    
    # 获取测试用例信息
    test_case = db.query(TestCase).filter(TestCase.id == test_run.test_case_id).first()
    
    # 构建响应数据
    response_data = {
        "id": test_run.id,
        "test_case_id": test_run.test_case_id,
        "status": test_run.status,
        "trigger_by": test_run.trigger_by,
        "start_time": test_run.start_time,
        "end_time": test_run.end_time,
        "llm_verdict": test_run.llm_verdict,
        "llm_reason": test_run.llm_reason,
        "error_message": test_run.error_message,
        "artifacts_path": test_run.artifacts_path,
        "created_at": test_run.created_at,
        "steps": [StepExecutionResponse.model_validate(s) for s in steps],
        "test_case": None
    }
    
    if test_case:
        response_data["test_case"] = {
            "id": test_case.id,
            "name": test_case.name,
            "description": test_case.description,
            "project_id": test_case.project_id
        }
    
    return TestRunDetailResponse(**response_data)


@router.get("/runs", response_model=List[TestRunResponse])
async def list_test_runs(
    project_id: int = None,
    case_id: int = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取运行记录列表"""
    query = db.query(TestRun)
    
    if case_id:
        query = query.filter(TestRun.test_case_id == case_id)
    elif project_id:
        # 通过测试用例关联项目
        query = query.join(TestCase).filter(TestCase.project_id == project_id)
    
    runs = query.order_by(TestRun.start_time.desc()).limit(limit).all()
    return [TestRunResponse.model_validate(run) for run in runs]


@router.get("/runs/{run_id}/steps", response_model=List[StepExecutionResponse])
async def get_test_run_steps(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取运行的步骤执行记录"""
    test_run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运行记录不存在"
        )
    
    steps = db.query(StepExecution).filter(
        StepExecution.test_run_id == run_id
    ).order_by(StepExecution.step_index).all()
    
    return [StepExecutionResponse.model_validate(s) for s in steps]
