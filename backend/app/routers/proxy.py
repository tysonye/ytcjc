from urllib.parse import urlparse
import re
import httpx, json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from app.config import PROXY_ALLOWED_DOMAINS

router = APIRouter(prefix="/api/proxy", tags=["CORS代理"])


class ProxyRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None


@router.post("/")
async def proxy_request(req: ProxyRequest):
    parsed = urlparse(req.url)
    domain_allowed = False
    for allowed in PROXY_ALLOWED_DOMAINS:
        if parsed.hostname and (parsed.hostname == allowed or parsed.hostname.endswith("." + allowed)):
            domain_allowed = True
            break
    if not domain_allowed:
        raise HTTPException(status_code=403, detail=f"域名 {parsed.hostname} 不在白名单中")

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            headers = req.headers or {}
            headers.pop("host", None)
            headers.pop("Host", None)
            kwargs = {"method": req.method, "url": req.url, "headers": headers}
            if req.body and req.method in ("POST", "PUT", "PATCH"):
                kwargs["content"] = req.body
            resp = await client.request(**kwargs)
            content_type = resp.headers.get("content-type", "text/html")
            raw = resp.content
            charset = None
            ct_lower = content_type.lower()
            if "charset=" in ct_lower:
                charset = ct_lower.split("charset=")[-1].split(";")[0].strip()
            if not charset:
                meta_match = re.search(rb'charset=["\']?([\w-]+)', raw[:500], re.IGNORECASE)
                if meta_match:
                    charset = meta_match.group(1).decode('ascii', errors='ignore')
            if charset and charset.lower() in ('gbk', 'gb2312', 'gb18030'):
                body = raw.decode('gb18030', errors='replace')
            elif not charset:
                if raw[:3] == b'\xef\xbb\xbf':
                    body = raw.decode('utf-8-sig', errors='replace')
                else:
                    try:
                        raw.decode('utf-8')
                        body = raw.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        body = raw.decode('gb18030', errors='replace')
            else:
                body = raw.decode('utf-8', errors='replace')
            return {"status_code": resp.status_code, "content_type": content_type, "body": body}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"请求失败: {str(e)}")


# 已废弃 - 前端现在直接使用 Vercel 边缘代理
# @router.post("/fetch")
# async def proxy_fetch(req: ProxyRequest):
#     return await proxy_request(req)


@router.post("/ai-chat")
async def ai_chat_proxy(req: Dict):
    message = req.get("message", "")
    context = req.get("context", "")

    from app.config import AI_BASE_URL, AI_API_KEY
    if not AI_BASE_URL or not AI_API_KEY:
        return {
            "reply": f"AI服务尚未配置。\n\n您的问题是：{message}\n\n作为足球分析师的初步建议：\n1. 请查看比赛的赔率走势变化\n2. 关注两队近期交锋记录\n3. 分析球队主客场战绩差异\n4. 参考积分榜排名情况\n\n如需更详细的分析，请联系管理员配置AI服务。"
        }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            system_prompt = """你是一位专业的足球数据分析分析师，精通竞彩赔率分析、球队实力评估、历史交锋分析。
请根据用户提供的信息给出专业、客观的分析建议。
回答时使用中文，格式清晰，适当使用表格展示数据对比。"""
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            if context:
                messages.append({"role": "user", "content": f"[上下文信息] {context}"})
                messages.append({"role": "assistant", "content": "已了解上下文信息，请继续提问。"})
            messages.append({"role": "user", "content": message})

            resp = await client.post(
                f"{AI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 1024, "temperature": 0.7},
            )
            data = resp.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "无法获取回复")
            return {"reply": reply}
    except Exception as e:
        return {"reply": f"AI服务调用失败: {str(e)}"}
