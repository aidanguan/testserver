"""
测试用例管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.test_case import TestCase
from app.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    NaturalLanguageRequest, StandardCaseResponse,
    ScriptGenerationRequest, ScriptGenerationResponse
)
from app.services.llm_service import LLMService
from app.utils.encryption import decrypt_api_key
from app.api.dependencies import get_current_user, get_current_admin_user

router = APIRouter(tags=["测试用例"])


@router.get("/projects/{project_id}/cases", response_model=List[TestCaseResponse])
async def list_test_cases(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的测试用例列表"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    test_cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    return [TestCaseResponse.model_validate(tc) for tc in test_cases]


@router.post("/projects/{project_id}/cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    project_id: int,
    test_case_data: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建测试用例"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 验证project_id匹配
    if test_case_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目ID不匹配"
        )
    
    # 创建测试用例
    test_case = TestCase(
        project_id=project_id,
        name=test_case_data.name,
        description=test_case_data.description,
        natural_language=test_case_data.natural_language,
        standard_steps=test_case_data.standard_steps,
        playwright_script=test_case_data.playwright_script,
        expected_result=test_case_data.expected_result,
        created_by=current_user.id
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    
    return TestCaseResponse.model_validate(test_case)


@router.get("/cases/{case_id}", response_model=TestCaseResponse)
async def get_test_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取测试用例详情"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    return TestCaseResponse.model_validate(test_case)


@router.put("/cases/{case_id}", response_model=TestCaseResponse)
async def update_test_case(
    case_id: int,
    test_case_data: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    # 更新字段
    if test_case_data.name:
        test_case.name = test_case_data.name
    if test_case_data.description is not None:
        test_case.description = test_case_data.description
    if test_case_data.natural_language:
        test_case.natural_language = test_case_data.natural_language
    if test_case_data.standard_steps:
        test_case.standard_steps = test_case_data.standard_steps
    if test_case_data.playwright_script:
        test_case.playwright_script = test_case_data.playwright_script
    if test_case_data.expected_result:
        test_case.expected_result = test_case_data.expected_result
    
    db.commit()
    db.refresh(test_case)
    
    return TestCaseResponse.model_validate(test_case)


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    # 检查权限：Admin或创建者可以删除
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN and test_case.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己创建的测试用例"
        )
    
    db.delete(test_case)
    db.commit()
    
    return None


@router.post("/cases/generate-from-nl", response_model=StandardCaseResponse)
async def generate_case_from_natural_language(
    request: NaturalLanguageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从自然语言生成标准化测试用例"""
    # 获取项目和LLM配置
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 解密API密钥并创建LLM服务
    api_key = decrypt_api_key(project.llm_api_key)
    llm_service = LLMService(
        provider=project.llm_provider,
        model=project.llm_model,
        api_key=api_key,
        base_url=project.llm_base_url,
        config=project.llm_config
    )
    
    try:
        # 调用LLM生成用例
        result = llm_service.generate_test_case_from_nl(
            natural_language=request.natural_language,
            base_url=project.base_url
        )
        
        return StandardCaseResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成测试用例失败: {str(e)}"
        )


@router.post("/cases/generate-script", response_model=ScriptGenerationResponse)
async def generate_playwright_script(
    request: ScriptGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从标准化用例生成Playwright脚本"""
    # 获取测试用例
    test_case = db.query(TestCase).filter(TestCase.id == request.test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    # 获取项目和LLM配置
    project = db.query(Project).filter(Project.id == test_case.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 解密API密钥并创建LLM服务
    api_key = decrypt_api_key(project.llm_api_key)
    llm_service = LLMService(
        provider=project.llm_provider,
        model=project.llm_model,
        api_key=api_key,
        base_url=project.llm_base_url,
        config=project.llm_config
    )
    
    try:
        # 调用LLM生成脚本
        result = llm_service.generate_playwright_script(
            case_name=test_case.name,
            standard_steps=test_case.standard_steps,
            base_url=project.base_url
        )
        
        return ScriptGenerationResponse(playwright_script=result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Playwright脚本失败: {str(e)}"
        )
