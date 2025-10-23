"""
测试视觉API是否可用
"""
import os
import base64
from openai import OpenAI

# 从环境变量或直接输入获取API Key
api_key = os.getenv("DASHSCOPE_API_KEY") or input("请输入DashScope API Key: ")

# 测试不同的模型名称
model_names = [
    "qwen-vl-plus",
    "qwen-vl-max", 
    "qwen3-vl-plus",
    "qwen2-vl-72b-instruct",
    "qwen-vl-v1"
]

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 创建一个简单的测试图片（1x1像素的PNG）
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print("========== 测试 DashScope Vision API ==========\n")

for model_name in model_names:
    print(f"测试模型: {model_name}")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请描述这张图片"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{test_image_base64}"}}
                ]
            }],
            max_tokens=100
        )
        result = response.choices[0].message.content
        print(f"✅ 成功! 响应: {result[:100]}")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 失败: {error_msg[:150]}")
    print("-" * 60)

print("\n========== 测试完成 ==========")
