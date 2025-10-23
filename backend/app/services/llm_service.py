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
    
    def analyze_final_result(
        self, 
        expected_result: str,
        final_screenshot: str,
        console_logs: List[str],
        all_steps_success: bool
    ) -> Dict[str, Any]:
        """
        分析最终结果并给出判定（只看最后一张截图，整体判定）
        
        Args:
            expected_result: 预期结果描述
            final_screenshot: 最后一张截图路径
            console_logs: 控制台日志
            all_steps_success: 所有步骤是否执行成功
            
        Returns:
            判定结果字典 {verdict, confidence, reason, observations}
        """
        print(f"\n########## analyze_final_result 被调用 ##########")
        print(f"预期结果: {expected_result}")
        print(f"最终截图: {final_screenshot}")
        print(f"所有步骤成功: {all_steps_success}")
        
        if not final_screenshot:
            print("没有截图，使用基础判定")
            return self._analyze_without_vision(expected_result, console_logs, [])
        
        try:
            # 使用视觉大模型分析最后一张截图
            print(f"使用视觉大模型分析最终截图...")
            vision_analysis = self._analyze_screenshot_with_vision(
                screenshot_path=final_screenshot,
                expected_result=expected_result,
                step_status=None
            )
            
            print(f"视觉分析结果: {vision_analysis}")
            
            # 基于视觉分析和步骤执行状态给出最终判定
            matches_expectation = vision_analysis.get("matches_expectation")
            
            if matches_expectation and all_steps_success:
                verdict = "passed"
                confidence = 0.9
                reason = f"最终截图符合预期结果：{vision_analysis.get('observation', '')}"
            elif not all_steps_success:
                verdict = "failed"
                confidence = 0.85
                reason = f"有步骤执行失败"
            elif matches_expectation is False:
                verdict = "failed"
                confidence = 0.85
                reason = f"最终截图不符合预期：{vision_analysis.get('observation', '')}"
            else:
                verdict = "unknown"
                confidence = 0.6
                reason = f"无法确定是否符合预期"
            
            result = {
                "verdict": verdict,
                "confidence": confidence,
                "reason": reason,
                "observations": [{
                    "step_index": "final",
                    "type": "visual",
                    "description": vision_analysis.get("observation", ""),
                    "severity": "error" if not matches_expectation else "info"
                }]
            }
            
            print(f"最终判定结果: {result}")
            print("########## analyze_final_result 结束 ##########\n")
            return result
            
        except Exception as e:
            print(f"视觉分析失败: {str(e)}")
            print("########## analyze_final_result 失败 ##########\n")
            return self._analyze_without_vision(expected_result, console_logs, [])
    
    def analyze_test_result(
        self, 
        expected_result: str,
        step_screenshots: List[str],
        console_logs: List[str],
        step_statuses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析测试结果并给出判定（使用视觉大模型分析截图）
        
        Args:
            expected_result: 预期结果描述
            step_screenshots: 步骤截图路径列表
            console_logs: 控制台日志
            step_statuses: 步骤执行状态
            
        Returns:
            判定结果字典 {verdict, confidence, reason, observations}
        """
        print(f"\n########## analyze_test_result 被调用 ##########")
        print(f"预期结果: {expected_result}")
        print(f"截图数量: {len(step_screenshots)}")
        print(f"截图列表: {step_screenshots}")
        print(f"步骤状态数量: {len(step_statuses)}")
        
        # 如果没有截图，使用基础判定
        if not step_screenshots:
            print("没有截图，使用基础判定")
            print("########## analyze_test_result 结束 ##########\n")
            return self._analyze_without_vision(expected_result, console_logs, step_statuses)
        
        print(f"有截图，将使用视觉大模型分析")
        
        # 使用视觉大模型分析每个截图
        screenshot_analyses = []
        for idx, screenshot_path in enumerate(step_screenshots):
            try:
                analysis = self._analyze_screenshot_with_vision(
                    screenshot_path,
                    expected_result,
                    step_statuses[idx] if idx < len(step_statuses) else None
                )
                screenshot_analyses.append({
                    "step_index": idx + 1,
                    "screenshot_path": screenshot_path,
                    "analysis": analysis
                })
            except Exception as e:
                print(f"分析截图 {screenshot_path} 失败: {e}")
                screenshot_analyses.append({
                    "step_index": idx + 1,
                    "screenshot_path": screenshot_path,
                    "analysis": {"error": str(e)}
                })
        
        # 综合所有截图分析结果和步骤状态，给出最终判定
        result = self._综合判定(expected_result, screenshot_analyses, console_logs, step_statuses)
        print(f"最终判定结果: {result}")
        print("########## analyze_test_result 结束 ##########\n")
        return result
    
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

重要提示：
- 系统会在每个步骤执行后自动等待3秒再截图，确保页面完全加载
- 你不需要在每个步骤后手动添加waitTime，除非有特殊需要

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
    
    def _analyze_screenshot_with_vision(self, screenshot_path: str, expected_result: str, step_status: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """使用视觉大模型分析截图"""
        import base64
        import os
        
        print(f"\n========== 开始视觉分析 ==========")
        print(f"Provider: {self.provider}")
        print(f"Model: {self.model}")
        print(f"截图路径: {screenshot_path}")
        
        # 读取截图文件并转为base64
        try:
            with open(screenshot_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            print(f"截图文件读取成功，大小: {len(image_data)} bytes (base64)")
        except Exception as e:
            print(f"读取截图失败: {str(e)}")
            return {"error": f"读取截图失败: {str(e)}"}
        
        step_desc = step_status.get("description", "") if step_status else ""
        
        prompt = f"""你是一个专业的UI测试分析专家。请分析这张截图。

步骤描述: {step_desc}
预期结果: {expected_result}

请描述你在截图中看到的内容，并判断是否符合预期。返回JSON格式：
{{
  "observation": "具体观察到的内容",
  "matches_expectation": true/false,
  "issues": ["发现的问题列表"]
}}"""
        
        # 调用视觉大模型
        if self.provider in ["openai", "dashscope"]:
            try:
                print(f"调用 {self.provider} Vision API，模型: {self.model}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }],
                    max_tokens=500
                )
                result_text = response.choices[0].message.content or "{}"
                print(f"Vision API响应: {result_text[:200]}...")
                parsed_result = json.loads(result_text.strip().replace("```json", "").replace("```", ""))
                print(f"解析结果: {parsed_result}")
                print(f"========== 视觉分析完成 ==========\n")
                return parsed_result
            except Exception as e:
                print(f"Vision API调用失败: {str(e)}")
                print(f"========== 视觉分析失败 ==========\n")
                return {"error": f"Vision API调用失败: {str(e)}"}
        else:
            print(f"Provider {self.provider} 不支持视觉分析")
            print(f"========== 视觉分析跳过 ==========\n")
            return {"observation": "当前模型不支持视觉分析", "matches_expectation": None, "issues": []}
    
    def _analyze_without_vision(self, expected_result: str, console_logs: List[str], step_statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """不使用视觉分析的基本判定"""
        all_success = all(s.get("status") == "success" for s in step_statuses)
        return {
            "verdict": "passed" if all_success else "failed",
            "confidence": 0.7,
            "reason": "根据步骤执行状态判定（未使用视觉分析）",
            "observations": []
        }
    
    def _综合判定(self, expected_result: str, screenshot_analyses: List[Dict], console_logs: List[str], step_statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """综合所有分析结果给出最终判定"""
        # 统计符合预期的截图数量
        matching_count = sum(1 for a in screenshot_analyses if a.get("analysis", {}).get("matches_expectation") == True)
        total_count = len(screenshot_analyses)
        
        # 收集所有观察
        observations = []
        for analysis in screenshot_analyses:
            if "analysis" in analysis and "observation" in analysis["analysis"]:
                observations.append({
                    "step_index": analysis["step_index"],
                    "type": "visual",
                    "description": analysis["analysis"]["observation"],
                    "severity": "error" if not analysis["analysis"].get("matches_expectation") else "info"
                })
        
        # 判定逻辑
        if matching_count == total_count:
            verdict = "passed"
            confidence = 0.9
            reason = f"所有{total_count}个步骤的截图分析都符合预期结果"
        elif matching_count >= total_count * 0.7:
            verdict = "unknown"
            confidence = 0.6
            reason = f"{matching_count}/{total_count}个步骤符合预期，部分步骤存在问题"
        else:
            verdict = "failed"
            confidence = 0.85
            reason = f"只有{matching_count}/{total_count}个步骤符合预期，测试失败"
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reason": reason,
            "observations": observations
        }
