"""
LLM编排服务 - 管理与LLM的交互
"""
from typing import Dict, Any, List, Optional
import json
from openai import OpenAI
from anthropic import Anthropic
import httpx


class LLMService:
    """LLM服务类"""
    
    def __init__(self, provider: str, model: str, api_key: str, base_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化LLM服务
        
        Args:
            provider: LLM提供商 (openai, anthropic, dashscope, openai-completion)
            model: 模型名称
            api_key: API密钥
            base_url: 自定义API基础URL
            config: 额外配置 (temperature, max_tokens等)
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = config or {}
        
        # 初始化客户端
        if self.provider == "openai":
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
        elif self.provider == "openai-completion":
            # 支持 OpenAI Completion API
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
        elif self.provider == "dashscope":
            # 阿里云百炼，使用 OpenAI 客户端但指定 DashScope 的 base_url
            dashscope_base_url = base_url if base_url else "https://dashscope.aliyuncs.com/compatible-mode/v1"
            self.client = OpenAI(
                api_key=api_key,
                base_url=dashscope_base_url
            )
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    def generate_test_case_from_nl(self, natural_language: str, base_url: str) -> Dict[str, Any]:
        """
        从自然语言生成标准化测试用例
        
        Args:
            natural_language: 自然语言描述
            base_url: 被测站点基础URL
            
        Returns:
            标准化测试用例字典
        """
        prompt = self._build_nl_to_case_prompt(natural_language, base_url)
        response = self._call_llm(prompt)
        return self._parse_case_response(response)
    
    def generate_playwright_script(
        self, 
        case_name: str,
        standard_steps: List[Dict[str, Any]], 
        base_url: str
    ) -> Dict[str, Any]:
        """
        从标准化用例生成Playwright脚本
        
        Args:
            case_name: 用例名称
            standard_steps: 标准化步骤列表
            base_url: 被测站点基础URL
            
        Returns:
            Playwright脚本字典
        """
        prompt = self._build_case_to_script_prompt(case_name, standard_steps, base_url)
        response = self._call_llm(prompt)
        return self._parse_script_response(response)
    
    def analyze_test_result(
        self, 
        expected_result: str,
        step_screenshots: List[str],
        console_logs: List[str],
        step_statuses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析测试结果并给出判定
        
        Args:
            expected_result: 预期结果描述
            step_screenshots: 步骤截图路径列表
            console_logs: 控制台日志
            step_statuses: 步骤执行状态
            
        Returns:
            判定结果字典 {verdict, confidence, reason, observations}
        """
        prompt = self._build_verdict_prompt(expected_result, step_screenshots, console_logs, step_statuses)
        response = self._call_llm(prompt)
        return self._parse_verdict_response(response)
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 2000)
        
        try:
            if self.provider in ["openai", "dashscope"]:
                # OpenAI Chat Completion API 和百炼共用相同的接口
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content or ""
            
            elif self.provider == "openai-completion":
                # OpenAI Completion API (传统接口)
                response = self.client.completions.create(
                    model=self.model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].text or ""
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.content[0].text
            
            else:
                raise ValueError(f"不支持的提供商: {self.provider}")
            
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def _build_nl_to_case_prompt(self, natural_language: str, base_url: str) -> str:
        """构建自然语言转用例的提示词"""
        return f"""你是一个专业的测试工程师。请将以下自然语言描述转换为结构化的测试用例。

被测站点: {base_url}
自然语言描述: {natural_language}

请生成一个JSON格式的测试用例,包含以下字段:
1. name: 用例名称(简短明确)
2. description: 用例描述
3. standard_steps: 标准化步骤数组,每个步骤包含:
   - index: 步骤序号(从1开始)
   - action: 操作类型(goto/click/fill/select/wait/assertText/assertVisible等)
   - description: 步骤描述
   - selector: CSS选择器(如需要)
   - value: 输入值或预期值(如需要)
   - expected: 预期结果(如需要)
4. expected_result: 整体预期结果描述

请只返回JSON,不要包含其他说明文字。确保JSON格式正确。

示例输出:
{{
  "name": "用户登录测试",
  "description": "测试用户使用正确的用户名和密码登录系统",
  "standard_steps": [
    {{
      "index": 1,
      "action": "goto",
      "description": "打开登录页面",
      "selector": null,
      "value": "/login",
      "expected": null
    }},
    {{
      "index": 2,
      "action": "fill",
      "description": "输入用户名",
      "selector": "#username",
      "value": "testuser",
      "expected": null
    }},
    {{
      "index": 3,
      "action": "fill",
      "description": "输入密码",
      "selector": "#password",
      "value": "password123",
      "expected": null
    }},
    {{
      "index": 4,
      "action": "click",
      "description": "点击登录按钮",
      "selector": "#login-button",
      "value": null,
      "expected": null
    }},
    {{
      "index": 5,
      "action": "assertVisible",
      "description": "验证进入主页",
      "selector": ".dashboard",
      "value": null,
      "expected": "显示用户仪表板"
    }}
  ],
  "expected_result": "用户成功登录并跳转到主页,显示用户仪表板"
}}"""
    
    def _build_case_to_script_prompt(self, case_name: str, standard_steps: List[Dict[str, Any]], base_url: str) -> str:
        """构建用例转Playwright脚本的提示词"""
        steps_json = json.dumps(standard_steps, ensure_ascii=False, indent=2)
        
        return f"""你是一个Playwright自动化测试专家。请将以下标准化测试步骤转换为Playwright脚本配置。

用例名称: {case_name}
被测站点: {base_url}
标准化步骤:
{steps_json}

请生成一个JSON格式的Playwright脚本配置,包含以下字段:
1. browser: 浏览器类型(chromium/firefox/webkit),默认chromium
2. viewport: 视口尺寸 {{width: 1280, height: 720}}
3. steps: Playwright步骤数组,每个步骤包含:
   - index: 步骤序号
   - action: Playwright操作(goto/click/fill/select/waitForSelector/screenshot等)
   - selector: 元素选择器
   - value: 输入值或URL
   - description: 步骤描述
   - screenshot: 是否截屏(布尔值),默认true
   - timeout: 超时时间(毫秒),可选

支持的action类型:
- goto: 导航到URL
- click: 点击元素
- fill: 填充输入框
- select: 选择下拉选项
- waitForSelector: 等待元素出现
- waitTime: 等待固定时间(需要duration参数)
- screenshot: 截屏
- assertText: 断言文本内容
- assertVisible: 断言元素可见

请只返回JSON,不要包含其他说明文字。

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
      "value": "{base_url}/login",
      "description": "打开登录页面",
      "screenshot": true
    }},
    {{
      "index": 2,
      "action": "fill",
      "selector": "#username",
      "value": "testuser",
      "description": "输入用户名",
      "screenshot": true
    }}
  ]
}}"""
    
    def _build_verdict_prompt(
        self, 
        expected_result: str,
        step_screenshots: List[str],
        console_logs: List[str],
        step_statuses: List[Dict[str, Any]]
    ) -> str:
        """构建结果判定的提示词"""
        # 简化版本，实际应该包含截图的base64编码或路径
        logs_text = "\n".join(console_logs[-20:]) if console_logs else "无控制台日志"
        statuses_json = json.dumps(step_statuses, ensure_ascii=False, indent=2)
        
        return f"""你是一个专业的测试分析专家。请分析以下测试执行结果,并给出判定。

预期结果:
{expected_result}

步骤执行状态:
{statuses_json}

控制台日志(最后20条):
{logs_text}

截图数量: {len(step_screenshots)}

请分析测试执行情况,并返回JSON格式的判定结果:
{{
  "verdict": "passed/failed/unknown",
  "confidence": 0.95,
  "reason": "判定理由的详细说明",
  "observations": [
    {{
      "step_index": 1,
      "type": "visual/log/performance",
      "description": "观察到的具体问题或成功点",
      "severity": "info/warning/error"
    }}
  ]
}}

判定规则:
1. 如果所有步骤成功且无明显错误 -> passed
2. 如果有步骤失败或有严重错误日志 -> failed
3. 如果无法确定 -> unknown

请只返回JSON,不要包含其他说明文字。"""
    
    def _parse_case_response(self, response: str) -> Dict[str, Any]:
        """解析用例生成响应"""
        try:
            # 尝试提取JSON
            response = response.strip()
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except Exception as e:
            raise ValueError(f"解析LLM响应失败: {str(e)}\n响应内容: {response}")
    
    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        """解析脚本生成响应"""
        return self._parse_case_response(response)
    
    def _parse_verdict_response(self, response: str) -> Dict[str, Any]:
        """解析判定响应"""
        return self._parse_case_response(response)
