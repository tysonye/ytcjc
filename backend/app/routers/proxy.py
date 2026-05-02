from urllib.parse import urlparse
import re
import httpx, json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from app.config import PROXY_ALLOWED_DOMAINS, AI_BASE_URL, AI_API_KEY
from app.database import get_db
from app.models import User, AIConfig, TokenUsage
from app.services.auth_service import get_current_user

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


@router.post("/ai-chat")
async def ai_chat_proxy(req: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = req.get("message", "")
    context = req.get("context", "")
    settings = req.get("settings", {})

    ai_config = db.query(AIConfig).order_by(AIConfig.id.desc()).first()
    base_url = ai_config.base_url if (ai_config and ai_config.base_url) else AI_BASE_URL
    api_key = ai_config.api_key if (ai_config and ai_config.api_key) else AI_API_KEY
    model_name = ai_config.model_name if (ai_config and ai_config.model_name) else "auto"

    if not base_url or not api_key:
        return {
            "reply": f"AI服务尚未配置。\n\n您的问题是：{message}\n\n作为足球分析师的初步建议：\n1. 请查看比赛的赔率走势变化\n2. 关注两队近期交锋记录\n3. 分析球队主客场战绩差异\n4. 参考积分榜排名情况\n\n如需更详细的分析，请联系管理员配置AI服务。"
        }

    try:
        preference_labels = {
            'odds_trend': '赔率走势分析',
            'head_to_head': '历史交锋记录',
            'recent_form': '球队近期状态',
            'home_away': '主客场战绩差异',
            'injury': '伤停/阵容信息',
            'standings': '联赛积分排名',
            'fund_flow': '盘口资金流向',
            'weather': '天气/场地影响',
        }

        preset = settings.get('preset', 'balanced')
        preferences = settings.get('preferences', ['odds_trend', 'head_to_head'])
        reply_format = settings.get('replyFormat', 'detailed')
        reply_language = settings.get('replyLanguage', 'zh')
        custom_prompt = settings.get('customPrompt', '')
        temperature = settings.get('temperature', 0.7)

        base_prompt = "你是一位专业的足球数据分析分析师，精通竞彩赔率分析、球队实力评估、历史交锋分析。"

        if ai_config and ai_config.system_prompt:
            base_prompt = ai_config.system_prompt

        if preset == 'conservative':
            base_prompt += "你的分析风格偏稳健，基于数据给出保守建议，强调风险提示，不轻易下结论。"
        elif preset == 'aggressive':
            base_prompt += "你的分析风格偏激进，大胆预测，关注冷门和爆冷机会，善于发现盘口异动和资金流向异常。"
        else:
            base_prompt += "你的分析风格均衡，兼顾数据与直觉判断，给出平衡建议。"

        focus_items = [preference_labels.get(p, p) for p in preferences if p in preference_labels]
        if focus_items:
            base_prompt += f"\n请在分析时重点关注以下维度：{'、'.join(focus_items)}。"

        if reply_format == 'concise':
            base_prompt += "\n请简洁回复，仅给出结论和关键数据，不要冗长的分析过程。"
        else:
            base_prompt += "\n请详细分析，包含完整的分析过程、数据支撑、结论和建议。"

        if reply_language == 'bilingual':
            base_prompt += "\n请使用中英双语回复。"
        else:
            base_prompt += "\n请使用中文回复。"

        if custom_prompt:
            base_prompt += f"\n\n用户追加指令：{custom_prompt}"

        base_prompt += "\n回答时格式清晰，适当使用表格展示数据对比。"

        max_tokens = 512 if reply_format == 'concise' else 1024

        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            messages = [
                {"role": "system", "content": base_prompt},
            ]
            if context:
                messages.append({"role": "user", "content": f"[上下文信息] {context}"})
                messages.append({"role": "assistant", "content": "已了解上下文信息，请继续提问。"})
            messages.append({"role": "user", "content": message})

            full_content = ""
            total_input_tokens = 0
            total_output_tokens = 0

            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_name, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "stream": True},
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_content += content
                            usage = data.get("usage")
                            if usage:
                                total_input_tokens = usage.get("prompt_tokens", 0)
                                total_output_tokens = usage.get("completion_tokens", 0)
                        except Exception:
                            pass

            if total_input_tokens == 0 and total_output_tokens == 0:
                approx_input = sum(len(m["content"]) for m in messages) // 4
                approx_output = len(full_content) // 4
                total_input_tokens = approx_input
                total_output_tokens = approx_output

            usage_record = TokenUsage(
                user_id=current_user.id,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                model_name=model_name,
                request_text_preview=message[:200],
            )
            db.add(usage_record)
            current_user.token_used += total_input_tokens + total_output_tokens
            db.commit()

            return {
                "reply": full_content or "无法获取回复",
                "token_usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                },
            }
    except Exception as e:
        return {"reply": f"AI服务调用失败: {str(e)}"}
