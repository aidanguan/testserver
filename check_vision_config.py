"""
检查视觉模型配置
"""
import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models.project import Project

def check_config():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        
        print("\n========== 项目配置检查 ==========\n")
        
        if not projects:
            print("⚠️  没有找到任何项目")
            return
        
        for project in projects:
            print(f"项目 ID: {project.id}")
            print(f"项目名称: {project.name}")
            print(f"LLM Provider: {project.llm_provider}")
            print(f"LLM Model: {project.llm_model}")
            print(f"LLM Base URL: {project.llm_base_url}")
            
            # 检查是否支持视觉
            if project.llm_provider == "dashscope":
                if "vl" in project.llm_model.lower() or "vision" in project.llm_model.lower():
                    print("✅ 该项目配置了支持视觉的模型")
                else:
                    print(f"⚠️  模型 '{project.llm_model}' 可能不支持视觉功能")
                    print("   建议使用: qwen-vl-plus, qwen-vl-max 等")
            elif project.llm_provider == "openai":
                if "gpt-4" in project.llm_model.lower() and ("vision" in project.llm_model.lower() or "4o" in project.llm_model.lower()):
                    print("✅ 该项目配置了支持视觉的模型")
                else:
                    print(f"⚠️  模型 '{project.llm_model}' 可能不支持视觉功能")
                    print("   建议使用: gpt-4o, gpt-4-vision-preview 等")
            else:
                print(f"⚠️  Provider '{project.llm_provider}' 可能不支持视觉分析")
            
            print("-" * 50)
        
        print("\n========== 检查完成 ==========\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_config()
