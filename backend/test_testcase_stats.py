"""
测试测试用例统计数据
"""
from app.database import SessionLocal
from sqlalchemy import func
from app.models.test_case import TestCase
from app.models.test_run import TestRun, LLMVerdict

db = SessionLocal()

try:
    test_cases = db.query(TestCase).all()
    
    print(f"\n共有 {len(test_cases)} 个测试用例\n")
    
    for test_case in test_cases:
        print(f"测试用例: {test_case.name}")
        print(f"  ID: {test_case.id}")
        
        # 执行次数
        execution_count = db.query(func.count(TestRun.id)).filter(
            TestRun.test_case_id == test_case.id
        ).scalar() or 0
        print(f"  执行次数: {execution_count}")
        
        # 计算成功率（通过率）
        if execution_count > 0:
            passed_count = db.query(func.count(TestRun.id)).filter(
                TestRun.test_case_id == test_case.id,
                TestRun.llm_verdict == LLMVerdict.PASSED
            ).scalar() or 0
            pass_rate = round((passed_count / execution_count) * 100, 2)
            print(f"  通过次数: {passed_count}")
            print(f"  成功率: {pass_rate}%")
        else:
            print(f"  成功率: 0.0%")
        
        print()
        
finally:
    db.close()
