"""
Woclaw Message Gateway - 消息网关
支持微信、钉钉、飞书等多平台消息接入
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Message:
    """消息"""
    id: str
    content: str
    sender: str
    channel: str
    timestamp: datetime
    metadata: dict = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class BaseGateway(ABC):
    """网关基类"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.on_message: Optional[Callable] = None
        self.running = False

    @abstractmethod
    async def start(self):
        """启动网关"""
        pass

    @abstractmethod
    async def stop(self):
        """停止网关"""
        pass

    @abstractmethod
    async def send(self, recipient: str, message: str):
        """发送消息"""
        pass

    def set_message_handler(self, handler: Callable):
        """设置消息处理器"""
        self.on_message = handler


class WechatGateway(BaseGateway):
    """
    微信网关
    通过 Wcferry 或企业微信接口接入
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name = "wechat"
        self.wx_client = None

    async def start(self):
        """启动微信网关"""
        try:
            # 尝试使用 wcferry
            from wcferry import Wcf
            
            self.wx_client = Wcf()
            self.running = True
            
            # 启动消息接收
            self.wx_client.enable_receiving_msg()
            
            # 启动消息循环
            asyncio.create_task(self._message_loop())
            
            print("✅ 微信网关已启动")
            return True
            
        except ImportError:
            print("⚠️ wcferry 未安装，微信网关不可用")
            print("   安装方式: pip install wcferry")
            return False
        except Exception as e:
            print(f"❌ 微信网关启动失败: {e}")
            return False

    async def _message_loop(self):
        """消息接收循环"""
        while self.running and self.wx_client:
            try:
                msg = self.wx_client.get_msg()
                if msg:
                    message = Message(
                        id=str(msg.id),
                        content=msg.content,
                        sender=msg.sender,
                        channel="wechat",
                        timestamp=datetime.now(),
                        metadata={"room_id": msg.roomid}
                    )
                    
                    if self.on_message:
                        await self.on_message(message)
                        
            except Exception as e:
                print(f"微信消息处理错误: {e}")
                
            await asyncio.sleep(0.1)

    async def stop(self):
        """停止微信网关"""
        self.running = False
        if self.wx_client:
            try:
                self.wx_client.disable_recv_msg()
            except:
                pass
        print("✅ 微信网关已停止")

    async def send(self, recipient: str, message: str):
        """发送微信消息"""
        if not self.wx_client:
            return {"success": False, "error": "微信未连接"}
            
        try:
            self.wx_client.send_text(message, recipient)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


class DingtalkGateway(BaseGateway):
    """
    钉钉网关
    通过钉钉机器人 Webhook 接入
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name = "dingtalk"
        self.webhook_url = config.get("webhook_url") if config else None
        self.secret = config.get("secret") if config else None

    async def start(self):
        """启动钉钉网关"""
        if not self.webhook_url:
            self.webhook_url = os.getenv("DINGTALK_WEBHOOK")
            self.secret = os.getenv("DINGTALK_SECRET")
            
        if self.webhook_url:
            self.running = True
            print("✅ 钉钉网关已启动")
            return True
        else:
            print("⚠️ 钉钉 Webhook 未配置")
            return False

    async def stop(self):
        """停止钉钉网关"""
        self.running = False
        print("✅ 钉钉网关已停止")

    async def send(self, recipient: str, message: str):
        """发送钉钉消息"""
        if not self.webhook_url:
            return {"success": False, "error": "钉钉 Webhook 未配置"}
            
        try:
            import aiohttp
            import hmac
            import hashlib
            import base64
            import time
            import urllib.parse
            
            url = self.webhook_url
            
            # 签名
            if self.secret:
                timestamp = str(round(time.time() * 1000))
                string_to_sign = f"{timestamp}\n{self.secret}"
                hmac_code = hmac.new(
                    self.secret.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    digestmod=hashlib.sha256
                ).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                url = f"{url}&timestamp={timestamp}&sign={sign}"
            
            payload = {
                "msgtype": "text",
                "text": {"content": message}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    result = await resp.json()
                    return {"success": result.get("errcode") == 0, "result": result}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


class FeishuGateway(BaseGateway):
    """
    飞书网关
    通过飞书机器人 Webhook 接入
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name = "feishu"
        self.webhook_url = config.get("webhook_url") if config else None

    async def start(self):
        """启动飞书网关"""
        if not self.webhook_url:
            self.webhook_url = os.getenv("FEISHU_WEBHOOK")
            
        if self.webhook_url:
            self.running = True
            print("✅ 飞书网关已启动")
            return True
        else:
            print("⚠️ 飞书 Webhook 未配置")
            return False

    async def stop(self):
        """停止飞书网关"""
        self.running = False
        print("✅ 飞书网关已停止")

    async def send(self, recipient: str, message: str):
        """发送飞书消息"""
        if not self.webhook_url:
            return {"success": False, "error": "飞书 Webhook 未配置"}
            
        try:
            import aiohttp
            
            payload = {
                "msg_type": "text",
                "content": {"text": message}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    result = await resp.json()
                    return {"success": result.get("code") == 0, "result": result}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


class TelegramGateway(BaseGateway):
    """
    Telegram 网关
    通过 Telegram Bot API 接入
    """

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.name = "telegram"
        self.bot_token = config.get("bot_token") if config else None
        self.api_base = "https://api.telegram.org"

    async def start(self):
        """启动 Telegram 网关"""
        if not self.bot_token:
            self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            
        if self.bot_token:
            self.running = True
            # 启动轮询
            asyncio.create_task(self._poll_loop())
            print("✅ Telegram 网关已启动")
            return True
        else:
            print("⚠️ Telegram Bot Token 未配置")
            return False

    async def _poll_loop(self):
        """消息轮询"""
        last_update_id = 0
        
        while self.running:
            try:
                import aiohttp
                
                url = f"{self.api_base}/bot{self.bot_token}/getUpdates"
                params = {"offset": last_update_id + 1, "timeout": 30}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as resp:
                        data = await resp.json()
                        
                        if data.get("ok"):
                            for update in data.get("result", []):
                                last_update_id = update["update_id"]
                                
                                if "message" in update:
                                    msg = update["message"]
                                    message = Message(
                                        id=str(update["update_id"]),
                                        content=msg.get("text", ""),
                                        sender=str(msg.get("from", {}).get("id", "")),
                                        channel="telegram",
                                        timestamp=datetime.now(),
                                        metadata=msg
                                    )
                                    
                                    if self.on_message:
                                        await self.on_message(message)
                                        
            except Exception as e:
                print(f"Telegram 轮询错误: {e}")
                
            await asyncio.sleep(1)

    async def stop(self):
        """停止 Telegram 网关"""
        self.running = False
        print("✅ Telegram 网关已停止")

    async def send(self, recipient: str, message: str):
        """发送 Telegram 消息"""
        if not self.bot_token:
            return {"success": False, "error": "Telegram Bot Token 未配置"}
            
        try:
            import aiohttp
            
            url = f"{self.api_base}/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": recipient,
                "text": message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    result = await resp.json()
                    return {"success": result.get("ok", False), "result": result}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}


class MessageHub:
    """
    消息中心
    统一管理所有网关
    """

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.gateways: dict[str, BaseGateway] = {}
        self.message_handlers: list[Callable] = []

    def register_gateway(self, name: str, gateway: BaseGateway):
        """注册网关"""
        gateway.set_message_handler(self._handle_message)
        self.gateways[name] = gateway

    async def start_all(self):
        """启动所有网关"""
        results = {}
        for name, gateway in self.gateways.items():
            results[name] = await gateway.start()
        return results

    async def stop_all(self):
        """停止所有网关"""
        for gateway in self.gateways.values():
            await gateway.stop()

    async def _handle_message(self, message: Message):
        """处理收到的消息"""
        print(f"\n📨 [{message.channel}] {message.sender}: {message.content[:50]}...")
        
        # 调用 Supervisor 处理
        result = await self.supervisor.process(message.content)
        
        # 发送回复
        if result.success and result.output:
            output_text = result.output if isinstance(result.output, str) else str(result.output)
            await self.send(message.channel, message.sender, output_text)
            
        # 调用自定义处理器
        for handler in self.message_handlers:
            try:
                await handler(message, result)
            except Exception as e:
                print(f"消息处理器错误: {e}")

    def add_handler(self, handler: Callable):
        """添加消息处理器"""
        self.message_handlers.append(handler)

    async def send(self, channel: str, recipient: str, message: str):
        """发送消息到指定渠道"""
        gateway = self.gateways.get(channel)
        if gateway:
            return await gateway.send(recipient, message)
        return {"success": False, "error": f"网关 {channel} 未注册"}

    async def broadcast(self, message: str, channels: list[str] = None):
        """广播消息到所有渠道"""
        results = {}
        for name, gateway in self.gateways.items():
            if channels is None or name in channels:
                # 广播需要知道接收者，这里简化处理
                results[name] = await gateway.send("", message)
        return results
