import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp.log"),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)

def generate_request_id(data: Dict[str, Any]) -> str:
    """生成请求ID"""
    timestamp = str(int(time.time() * 1000))
    data_str = json.dumps(data, sort_keys=True)
    hash_obj = hashlib.md5(f"{timestamp}:{data_str}".encode())
    return hash_obj.hexdigest()

def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """解析SSE响应行"""
    line = line.strip()
    if not line or not line.startswith('data:'):
        return None
    
    data_str = line[5:].strip()
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        return None

def format_message_for_logging(message: Dict[str, Any]) -> str:
    """格式化消息用于日志记录"""
    message_copy = message.copy()
    
    # 避免记录长提示
    if "prompt" in message_copy:
        prompt = message_copy["prompt"]
        message_copy["prompt"] = f"{prompt[:50]}..." if len(prompt) > 50 else prompt
    
    return json.dumps(message_copy, ensure_ascii=False)

def validate_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """验证MCP请求格式"""
    required_fields = ["tool_name", "parameters"]
    
    for field in required_fields:
        if field not in request:
            return {"valid": False, "error": f"Missing required field: {field}"}
    
    return {"valid": True}

def validate_tool_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """验证工具请求格式"""
    required_fields = ["tool_name", "parameters"]
    
    for field in required_fields:
        if field not in request:
            return {"valid": False, "error": f"Missing required field: {field}"}
    
    return {"valid": True}
