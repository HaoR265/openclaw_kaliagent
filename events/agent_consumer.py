#!/usr/bin/env python3
"""
专业化攻击者代理的消费者脚本
每个代理运行此脚本，只处理自己类别的任务。
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, date
from pathlib import Path
import fcntl
import time

from db import update_task_state_from_legacy

EVENTS_DIR = Path(__file__).parent

def get_tasks_file(target_date=None):
    """返回指定日期的任务文件路径（默认今天）"""
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)
    filename = f"tasks-{target_date.isoformat()}.jsonl"
    return EVENTS_DIR / filename

def load_events():
    """读取当天事件文件中的所有事件"""
    tasks_file = get_tasks_file()
    if not tasks_file.exists():
        return []
    with open(tasks_file, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def save_events(events):
    """保存所有事件到当天文件（覆盖）"""
    tasks_file = get_tasks_file()
    with open(tasks_file, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

def update_event_status(event_id, new_status, events):
    """更新事件状态并记录历史"""
    for event in events:
        if event["id"] == event_id:
            event["status"] = new_status
            event["statusHistory"].append({
                "status": new_status,
                "at": datetime.now(timezone.utc).isoformat()
            })
            if new_status == "processing":
                event["processedAt"] = datetime.now(timezone.utc).isoformat()
            elif new_status in ("completed", "failed"):
                event["completedAt"] = datetime.now(timezone.utc).isoformat()
            return True
    return False

def write_result(event_id, status, raw_data, metadata):
    """写入结果文件"""
    results_file = EVENTS_DIR / "results.jsonl"
    result = {
        "eventId": event_id,
        "status": status,
        "rawData": raw_data,
        "metadata": metadata,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    with open(results_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(f"结果已写入: {event_id}")

def load_apis_config():
    """加载 API 配置"""
    apis_file = EVENTS_DIR / "apis.json"
    if not apis_file.exists():
        return {}
    try:
        with open(apis_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"API 配置文件解析失败: {apis_file}")
        return {}


def resolve_api_key(value):
    """支持 ${ENV_VAR} 占位符，避免在仓库中保存明文密钥。"""
    if not value:
        return None
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.environ.get(env_name)
    return value

def call_category_api(category, event, max_retries=2):
    """调用类别对应的 DeepSeek Beta API（从 consume.py 复制并修改）"""
    # 尝试导入 requests
    try:
        import requests
        REQUESTS_AVAILABLE = True
    except ImportError:
        print("requests 库不可用，无法调用 API")
        return None
    
    apis = load_apis_config()
    if category not in apis:
        print(f"类别 '{category}' 未在 API 配置中定义")
        return None
    
    config = apis[category]
    api_key = resolve_api_key(config.get("api_key"))
    base_url = config.get("base_url", "https://api.deepseek.com/beta")
    endpoint = config.get("endpoint", "/chat/completions")
    model = config.get("model", "deepseek-chat")

    if not api_key:
        print(f"类别 '{category}' 缺少可用 API 密钥，请检查环境变量或 apis.json 占位符配置")
        return None
    
    # 构建请求 URL
    url = base_url.rstrip("/") + endpoint
    
    # 构建请求体 - 要求 JSON 响应格式
    task = event["task"]
    params = event.get("params", {})
    
    messages = [
        {"role": "system", "content": f"你是 {category} 攻击者代理，执行渗透测试任务。请始终以 JSON 格式返回结果，包含 'success' (布尔值) 和 'data' (对象) 字段。"},
        {"role": "user", "content": f"任务: {task}\n参数: {json.dumps(params, indent=2)}\n\n请返回 JSON 格式的结果，包含以下字段：\n- success: true/false\n- data: 执行结果的具体数据\n- message: 可选的人类可读消息"}
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}  # 要求 JSON 响应
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 重试逻辑
    for attempt in range(max_retries + 1):
        try:
            timeout = 30 * (attempt + 1)  # 逐渐增加超时
            print(f"调用 {category} API (尝试 {attempt+1}/{max_retries+1})")
            
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                # 由于设置了 response_format，内容应该是 JSON
                try:
                    api_result = json.loads(content)
                    # 验证基本结构
                    if isinstance(api_result, dict) and "success" in api_result:
                        print(f"API 调用成功 (尝试 {attempt+1})")
                        return api_result
                    else:
                        print(f"API 响应缺少 'success' 字段: {api_result}")
                        # 仍然接受，但包装一下
                        return {"success": True, "data": api_result, "message": "API returned non-standard format"}
                except json.JSONDecodeError as e:
                    print(f"API 响应不是有效的 JSON (尝试 {attempt+1}): {e}")
                    # 回退到文本处理
                    return {"success": True, "data": {"output": content}, "message": "API returned text instead of JSON"}
            else:
                # 非标准响应格式
                print(f"API 返回非标准格式: {result.keys()}")
                return {"success": True, "data": result, "message": "API returned non-standard response"}
                
        except requests.exceptions.Timeout as e:
            print(f"API 调用超时 (尝试 {attempt+1}): {e}")
            if attempt == max_retries:
                print(f"达到最大重试次数 ({max_retries+1})")
                return None
            print(f"等待 2 秒后重试...")
            time.sleep(2)
            
        except requests.exceptions.ConnectionError as e:
            print(f"API 连接错误 (尝试 {attempt+1}): {e}")
            if attempt == max_retries:
                print(f"达到最大重试次数 ({max_retries+1})")
                return None
            print(f"等待 3 秒后重试...")
            time.sleep(3)
            
        except requests.exceptions.HTTPError as e:
            print(f"API HTTP 错误 (尝试 {attempt+1}): {e}")
            if e.response.status_code == 401:
                print("API 密钥无效，停止重试")
                return None
            elif e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                print(f"速率限制，等待 {retry_after} 秒")
                time.sleep(retry_after)
                continue
            elif 500 <= e.response.status_code < 600:
                print("服务器错误，重试...")
                if attempt == max_retries:
                    return None
                time.sleep(5)
                continue
            else:
                print(f"HTTP {e.response.status_code} 错误，停止重试")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API 请求异常 (尝试 {attempt+1}): {e}")
            if attempt == max_retries:
                return None
            time.sleep(2)
            
        except json.JSONDecodeError as e:
            print(f"响应 JSON 解析失败 (尝试 {attempt+1}): {e}")
            if attempt == max_retries:
                return None
            time.sleep(1)
    
    print("所有重试尝试均失败")
    return None

def execute_task_for_agent(category, event):
    """执行任务（调用类别对应的 API）"""
    print(f"代理 {category} 执行任务: {event['task']}")
    
    # 调用 API
    api_result = call_category_api(category, event)
    
    if api_result is not None:
        # 确保有正确的字段
        result = {
            "success": api_result.get("success", True),
            "data": api_result.get("data", api_result),
            "message": api_result.get("message", f"代理 {category} 完成任务"),
            "executionSource": "agent-api"
        }
        return result
    else:
        # API 调用失败，返回模拟结果
        print(f"API 调用失败，返回模拟结果")
        return {
            "success": False,
            "data": {
                "task": event["task"],
                "category": category,
                "error": "API 调用失败",
                "executedAt": datetime.now(timezone.utc).isoformat()
            },
            "message": f"代理 {category} API 调用失败",
            "executionSource": "agent-fallback"
        }

def main():
    parser = argparse.ArgumentParser(description="专业化攻击者代理消费者")
    parser.add_argument("--category", required=True, 
                       help="代理类别 (wireless, recon, web, internal, exploit, social)")
    parser.add_argument("--once", action="store_true",
                       help="只处理一次然后退出")
    
    args = parser.parse_args()
    category = args.category
    
    print(f"启动 {category} 代理消费者")
    
    while True:
        # 文件锁，避免并发消费
        tasks_file = get_tasks_file()
        lock_file = tasks_file.with_suffix(".lock")
        
        try:
            with open(lock_file, "w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                events = load_events()
                # 只查找当前代理类别的 pending 事件
                pending_events = [
                    e for e in events 
                    if e["status"] == "pending" and e.get("category") == category
                ]
                
                if not pending_events:
                    print(f"无 {category} 类别的待处理事件")
                    if args.once:
                        return
                    # 等待一段时间再检查
                    fcntl.flock(lock, fcntl.LOCK_UN)
                    time.sleep(30)
                    continue
                
                # 每次只处理一个事件
                event = pending_events[0]
                event_id = event["id"]
                
                # 更新状态为 processing
                if not update_event_status(event_id, "processing", events):
                    print(f"无法更新事件状态: {event_id}")
                    continue
                save_events(events)
                update_task_state_from_legacy(event_id, "processing")
                
                # 释放锁，允许其他代理处理其他事件
                fcntl.flock(lock, fcntl.LOCK_UN)
                
                # 处理事件（可能耗时）
                try:
                    result = execute_task_for_agent(category, event)
                    final_status = "completed" if result.get("success") else "failed"
                except Exception as e:
                    print(f"处理事件时出错: {e}")
                    final_status = "failed"
                    result = {"success": False, "data": {"error": str(e)}}
                
                # 重新加锁以更新最终状态
                with open(lock_file, "w") as lock2:
                    fcntl.flock(lock2, fcntl.LOCK_EX)
                    events = load_events()
                    update_event_status(event_id, final_status, events)
                    save_events(events)
                update_task_state_from_legacy(
                    event_id,
                    final_status,
                    error_message=result.get("message") if isinstance(result, dict) else None,
                )
                
                # 写入结果
                raw_data = {
                    "task": event["task"],
                    "params": event.get("params", {}),
                    "executionResult": result,
                    "category": category,
                    "apiUsed": False,
                    "executionSource": "agent"
                }
                
                metadata = {
                    "duration": 1,
                    "toolsUsed": [],
                    "apiUsed": False,
                    "executionSource": "agent",
                    "agentCategory": category
                }
                
                write_result(event_id, final_status, raw_data, metadata)
                
                if args.once:
                    print(f"处理完成一个事件，退出")
                    return
                    
        except BlockingIOError:
            print("另一个消费者正在运行，等待...")
            time.sleep(10)
        except Exception as e:
            print(f"消费者出错: {e}")
            if args.once:
                return
            time.sleep(30)

if __name__ == "__main__":
    main()
