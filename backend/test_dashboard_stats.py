"""
测试Dashboard统计数据API
"""
from app.database import SessionLocal
from sqlalchemy import func
from app.models.project import Project
from app.models.test_case import TestCase
from app.models.test_run import TestRun, LLMVerdict

db = SessionLocal()

try:
    # 项目总数
    projects_count = db.query(func.count(Project.id)).scalar()
    print(f"项目总数: {projects_count}")
    
    # 测试用例总数
    test_cases_count = db.query(func.count(TestCase.id)).scalar()
    print(f"测试用例总数: {test_cases_count}")
    
    # 执行总次数
    total_runs = db.query(func.count(TestRun.id)).scalar()
    print(f"执行总次数: {total_runs}")
    
    # 计算通过率
    if total_runs > 0:
        passed_runs = db.query(func.count(TestRun.id)).filter(
            TestRun.llm_verdict == LLMVerdict.PASSED
        ).scalar()
        pass_rate = round((passed_runs / total_runs) * 100, 2)
        print(f"通过的执行次数: {passed_runs}")
        print(f"通过率: {pass_rate}%")
    else:
        print(f"通过率: 0%")
    
    # 列出所有项目
    print("\n项目列表:")
    projects = db.query(Project).all()
    for p in projects:
        print(f"  - ID: {p.id}, 名称: {p.name}, URL: {p.base_url}")
        
finally:
    db.close()
