/**
 * Midscene 执行器脚本
 * 接收测试用例配置，使用 Midscene AI 能力执行测试
 */
import { chromium, firefox, webkit } from 'playwright';
import { PlaywrightAgent } from '@midscene/web/playwright';
import * as fs from 'fs';
import * as path from 'path';

interface MidsceneStep {
  index: number;
  action: string;
  description: string;
  selector?: string;
  value?: string;
  expected?: string;
  timeout?: number;
}

interface MidsceneScript {
  browser: 'chromium' | 'firefox' | 'webkit';
  viewport: { width: number; height: number };
  steps: MidsceneStep[];
}

interface ExecutionResult {
  success: boolean;
  steps: Array<{
    index: number;
    description: string;
    status: 'success' | 'failed';
    screenshot_path?: string;
    error_message?: string;
    start_time: string;
    end_time: string;
  }>;
  error_message?: string;
  artifacts_path: string;
  console_logs: string[];
}

async function executeMidsceneScript(
  scriptConfig: MidsceneScript,
  runId: number,
  artifactsBasePath: string,
  expectedResult: string,
  authStatePath?: string  // 新增：认证状态路径
): Promise<ExecutionResult> {
  const runArtifactsPath = path.join(artifactsBasePath, `runs/${runId}`);
  const screenshotsPath = path.join(runArtifactsPath, 'screenshots');
  const logsPath = path.join(runArtifactsPath, 'logs');
  const networkPath = path.join(runArtifactsPath, 'network');

  // 创建目录
  fs.mkdirSync(screenshotsPath, { recursive: true });
  fs.mkdirSync(logsPath, { recursive: true });
  fs.mkdirSync(networkPath, { recursive: true });

  const result: ExecutionResult = {
    success: false,
    steps: [],
    artifacts_path: runArtifactsPath,
    console_logs: [],
  };

  const consoleLogs: string[] = [];
  let browser = null;
  let page = null;
  let agent = null;

  try {
    // 启动浏览器
    const browserType = scriptConfig.browser || 'chromium';
    if (browserType === 'chromium') {
      browser = await chromium.launch({ headless: false });
    } else if (browserType === 'firefox') {
      browser = await firefox.launch({ headless: false });
    } else if (browserType === 'webkit') {
      browser = await webkit.launch({ headless: false });
    } else {
      browser = await chromium.launch({ headless: false });
    }

    // 创建上下文（支持加载认证状态）
    const viewport = scriptConfig.viewport || { width: 1280, height: 720 };
    const contextOptions: any = { viewport };
    
    // 如果有认证状态文件，加载它
    if (authStatePath && fs.existsSync(authStatePath)) {
      contextOptions.storageState = authStatePath;
      console.log(`✅ 加载认证状态: ${authStatePath}`);
    } else {
      console.log(`ℹ️ 未找到认证状态，使用新的浏览器会话`);
    }
    
    const context = await browser.newContext(contextOptions);
    page = await context.newPage();

    // 监听控制台日志
    page.on('console', (msg) => {
      const logEntry = `[${msg.type()}] ${msg.text()}`;
      consoleLogs.push(logEntry);
    });

    // 初始化 Midscene Agent
    // Midscene 会自动从环境变量读取配置
    console.log(`📝 Midscene 使用环境变量配置:`);
    console.log(`  - OPENAI_API_KEY: ${process.env.OPENAI_API_KEY?.substring(0, 10)}...`);
    console.log(`  - OPENAI_BASE_URL: ${process.env.OPENAI_BASE_URL || '未设置'}`);
    console.log(`  - MIDSCENE_MODEL_NAME: ${process.env.MIDSCENE_MODEL_NAME || '未设置'}`);
    console.log(`  - MIDSCENE_USE_QWEN_VL: ${process.env.MIDSCENE_USE_QWEN_VL || '未设置'}`);
    
    agent = new PlaywrightAgent(page);

    // 执行步骤
    const steps = scriptConfig.steps || [];
    const totalSteps = steps.length;

    for (let idx = 0; idx < totalSteps; idx++) {
      const step = steps[idx];
      const isLastStep = idx === totalSteps - 1;
      const stepResult = await executeStep(
        agent,
        page,
        step,
        screenshotsPath,
        isLastStep,
        artifactsBasePath  // 传递 artifacts 基础路径
      );
      result.steps.push(stepResult);

      // 如果步骤失败，停止执行
      if (stepResult.status === 'failed') {
        break;
      }
    }

    // 保存控制台日志
    fs.writeFileSync(
      path.join(logsPath, 'console.log'),
      consoleLogs.join('\n'),
      'utf-8'
    );

    result.console_logs = consoleLogs;
    result.success = result.steps.every((s) => s.status === 'success');
  } catch (error: any) {
    result.error_message = error.message || String(error);
    result.success = false;
  } finally {
    // 清理资源
    if (page) await page.close();
    if (browser) await browser.close();
  }

  return result;
}

async function executeStep(
  agent: PlaywrightAgent,
  page: any,
  step: MidsceneStep,
  screenshotsPath: string,
  isLastStep: boolean,
  artifactsBasePath: string  // 新增：artifacts 基础路径
): Promise<any> {
  const stepResult = {
    index: step.index || 0,
    description: step.description || '',
    status: 'success' as 'success' | 'failed',
    screenshot_path: undefined as string | undefined,
    error_message: undefined as string | undefined,
    start_time: new Date().toISOString(),
    end_time: '',
  };

  try {
    const action = step.action;
    const timeout = step.timeout || 30000;

    // 使用 Midscene AI 能力执行操作
    if (action === 'goto') {
      // 导航到页面
      await page.goto(step.value, { timeout, waitUntil: 'networkidle' });
    } else if (action === 'click' || action === 'aiTap') {
      // AI 点击 - 使用自然语言描述
      const target = step.description || step.selector || step.value || '';
      await agent.aiTap(target);
    } else if (action === 'fill' || action === 'aiInput') {
      // AI 输入 - 使用自然语言描述
      const targetDesc = step.description || step.selector || '';
      await agent.aiInput(step.value || '', targetDesc);
    } else if (action === 'aiAction') {
      // 通用 AI 操作
      await agent.aiAction(step.description);
    } else if (action === 'aiAssert') {
      // AI 断言
      await agent.aiAssert(step.description);
    } else if (action === 'aiWaitFor') {
      // AI 等待
      await agent.aiWaitFor(step.description, { timeoutMs: timeout });
    } else if (action === 'aiQuery') {
      // AI 查询（提取数据）
      const data = await agent.aiQuery(step.description);
      console.log('AI Query Result:', data);
    } else if (action === 'screenshot') {
      // 截图
      const screenshotName = `step_${step.index}.png`;
      const screenshotPath = path.join(screenshotsPath, screenshotName);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      // 保存相对路径
      const relativePath = screenshotPath
        .replace(artifactsBasePath, '')
        .replace(/\\/g, '/')
        .replace(/^\//, '');
      stepResult.screenshot_path = relativePath;
    } else if (action === 'waitTime') {
      // 等待固定时间
      const duration = (step as any).duration || 1000;
      await page.waitForTimeout(duration);
    } else {
      // 兜底：传统 Playwright 操作
      if (action === 'select') {
        await page.selectOption(step.selector!, step.value!);
      } else if (action === 'waitForSelector') {
        await page.waitForSelector(step.selector!, { timeout });
      } else if (action === 'assertText') {
        const element = page.locator(step.selector!);
        const text = await element.innerText({ timeout });
        if (!text.includes(step.expected || '')) {
          throw new Error(
            `文本断言失败: 期望包含'${step.expected}', 实际为'${text}'`
          );
        }
      } else if (action === 'assertVisible') {
        const element = page.locator(step.selector!);
        const visible = await element.isVisible({ timeout });
        if (!visible) {
          throw new Error(`元素不可见: ${step.selector}`);
        }
      }
    }

    // 默认截图（每步执行后）
    if ((step as any).screenshot !== false && action !== 'screenshot') {
      await page.waitForTimeout(3000); // 等待页面稳定
      const screenshotName = `step_${step.index}.png`;
      const screenshotPath = path.join(screenshotsPath, screenshotName);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      // 保存相对路径（相对于 artifacts 目录）
      const relativePath = screenshotPath
        .replace(artifactsBasePath, '')
        .replace(/\\/g, '/')
        .replace(/^\//, '');
      stepResult.screenshot_path = relativePath;
    }
  } catch (error: any) {
    stepResult.status = 'failed';
    stepResult.error_message = error.message || String(error);
  }

  stepResult.end_time = new Date().toISOString();
  return stepResult;
}

// 命令行接口
async function main() {
  try {
    // 从命令行参数获取配置
    const args = process.argv.slice(2);
    if (args.length < 4) {
      console.error(
        'Usage: node executor.js <scriptConfigJson> <runId> <artifactsPath> <expectedResult> [authStatePath]'
      );
      process.exit(1);
    }

    const scriptConfig: MidsceneScript = JSON.parse(args[0]);
    const runId = parseInt(args[1], 10);
    const artifactsPath = args[2];
    const expectedResult = args[3];
    const authStatePath = args[4] || '';  // 新增：认证状态路径（可选）

    const result = await executeMidsceneScript(
      scriptConfig,
      runId,
      artifactsPath,
      expectedResult,
      authStatePath  // 传递认证状态路径
    );

    // 输出结果（Python 端可以解析）
    console.log('===MIDSCENE_RESULT_START===');
    console.log(JSON.stringify(result, null, 2));
    console.log('===MIDSCENE_RESULT_END===');

    process.exit(result.success ? 0 : 1);
  } catch (error: any) {
    console.error('Midscene executor error:', error);
    process.exit(1);
  }
}

main();
