"""
项目管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.test_case import TestCase
from app.models.test_run import TestRun, LLMVerdict
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithStatsResponse
from app.utils.encryption import encrypt_api_key, decrypt_api_key
from app.api.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("", response_model=List[ProjectWithStatsResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目列表（带统计数据）"""
    projects = db.query(Project).all()
    
    result = []
    for project in projects:
        # 计算每个项目的统计数据
        # 测试用例数
        test_case_count = db.query(func.count(TestCase.id)).filter(
            TestCase.project_id == project.id
        ).scalar() or 0
        
        # 执行次数（通过test_case关联）
        execution_count = db.query(func.count(TestRun.id)).join(
            TestCase, TestRun.test_case_id == TestCase.id
        ).filter(
            TestCase.project_id == project.id
        ).scalar() or 0
        
        # 计算通过率
        if execution_count > 0:
            passed_count = db.query(func.count(TestRun.id)).join(
                TestCase, TestRun.test_case_id == TestCase.id
            ).filter(
                TestCase.project_id == project.id,
                TestRun.llm_verdict == LLMVerdict.PASSED
            ).scalar() or 0
            pass_rate = round((passed_count / execution_count) * 100, 2)
        else:
            pass_rate = 0.0
        
        # 构建响应数据
        project_dict = ProjectResponse.model_validate(project).model_dump()
        project_dict['test_case_count'] = test_case_count
        project_dict['execution_count'] = execution_count
        project_dict['pass_rate'] = pass_rate
        
        result.append(ProjectWithStatsResponse(**project_dict))
    
    return result


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建项目（仅管理员）"""
    # 检查项目名是否已存在
    existing_project = db.query(Project).filter(Project.name == project_data.name).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目名已存在"
        )
    
    # 加密API密钥
    encrypted_api_key = encrypt_api_key(project_data.llm_api_key)
    
    # 创建项目
    project = Project(
        name=project_data.name,
        description=project_data.description,
        base_url=project_data.base_url,
        llm_provider=project_data.llm_provider,
        llm_model=project_data.llm_model,
        llm_api_key=encrypted_api_key,
        llm_config=project_data.llm_config,
        created_by=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新项目（仅管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查项目名是否与其他项目冲突
    if project_data.name and project_data.name != project.name:
        existing_project = db.query(Project).filter(Project.name == project_data.name).first()
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目名已存在"
            )
    
    # 更新字段
    if project_data.name:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.base_url:
        project.base_url = project_data.base_url
    if project_data.llm_provider:
        project.llm_provider = project_data.llm_provider
    if project_data.llm_model:
        project.llm_model = project_data.llm_model
    if project_data.llm_api_key:
        project.llm_api_key = encrypt_api_key(project_data.llm_api_key)
    if project_data.llm_base_url is not None:
        project.llm_base_url = project_data.llm_base_url
    if project_data.llm_config is not None:
        project.llm_config = project_data.llm_config
    
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除项目（仅管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    db.delete(project)
    db.commit()
    
    return None


@router.get("/stats/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取仪表盘统计数据"""
    # 项目总数
    projects_count = db.query(func.count(Project.id)).scalar()
    
    # 测试用例总数
    test_cases_count = db.query(func.count(TestCase.id)).scalar()
    
    # 执行总次数
    total_runs = db.query(func.count(TestRun.id)).scalar()
    
    # 计算通过率
    if total_runs > 0:
        passed_runs = db.query(func.count(TestRun.id)).filter(
            TestRun.llm_verdict == LLMVerdict.PASSED
        ).scalar()
        pass_rate = round((passed_runs / total_runs) * 100, 2)
    else:
        pass_rate = 0
    
    return {
        "projects": projects_count or 0,
        "testCases": test_cases_count or 0,
        "totalRuns": total_runs or 0,
        "passRate": pass_rate
    }
