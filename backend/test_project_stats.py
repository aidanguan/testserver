"""
测试项目统计数据API
"""
from app.database import SessionLocal
from sqlalchemy import func
from app.models.project import Project
from app.models.test_case import TestCase
from app.models.test_run import TestRun, LLMVerdict

db = SessionLocal()

try:
    projects = db.query(Project).all()
    
    print(f"\n共有 {len(projects)} 个项目\n")
    
    for project in projects:
        print(f"项目: {project.name}")
        print(f"  ID: {project.id}")
        
        # 测试用例数
        test_case_count = db.query(func.count(TestCase.id)).filter(
            TestCase.project_id == project.id
        ).scalar() or 0
        print(f"  测试用例数: {test_case_count}")
        
        # 执行次数（通过test_case关联）
        execution_count = db.query(func.count(TestRun.id)).join(
            TestCase, TestRun.test_case_id == TestCase.id
        ).filter(
            TestCase.project_id == project.id
        ).scalar() or 0
        print(f"  执行次数: {execution_count}")
        
        # 计算通过率
        if execution_count > 0:
            passed_count = db.query(func.count(TestRun.id)).join(
                TestCase, TestRun.test_case_id == TestCase.id
            ).filter(
                TestCase.project_id == project.id,
                TestRun.llm_verdict == LLMVerdict.PASSED
            ).scalar() or 0
            pass_rate = round((passed_count / execution_count) * 100, 2)
            print(f"  通过次数: {passed_count}")
            print(f"  通过率: {pass_rate}%")
        else:
            print(f"  通过率: 0.0%")
        
        print()
        
finally:
    db.close()
