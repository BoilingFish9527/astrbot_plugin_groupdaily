from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent 
import astrbot.api.message_components as Comp
import os
import json
import time
import random
from typing import List, Dict, Any


@register("groupdaily","BoilingFish","一个简单的群聊签到插件","Beta1.0","https://github.com/BoilingFish9527/astrbot_plugin_groupdaily")
class GroupDaily(Star):
    def __init__(self,context:Context):
        super().__init__(context)
        self.data_dir = os.path.join("data", "plugins", "group_daily")
        self_records_file = os.path.join(self.data_dir, "daily_records.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self.records = self._load_records()
        logger.info("群聊签到插件已加载")
    def _load_records(self):
        try:
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"date": "", "score": "", "wife": ""}
        except Exception as e:
            logger.error(f"加载记录文件失败: {e}")
            return {"date": "", "score": "", "wife": ""}
    def _save_records(self):
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记录文件失败: {e}")
    def _use_score_(self,score:int,n:int,user_id:str,event:AstrMessageEvent):
        if score - n < 0:
            yield event.plain_result("小鱼干数量不足，无法使用！")
            return False
        self.records[user_id]["score"] -= n
        return True
    @filter.command("签到")
    async def handle_sign_in(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.records:
            self.records[user_id] = {"date": "", "score": 0,"wife": ""}
        if self.records[user_id]["date"] == time.strftime("%Y-%m-%d", time.localtime()):
            yield event.plain_result("您今天已经签到过了，明天再来吧！")
            return
        self.records[user_id]["date"] = time.strftime("%Y-%m-%d", time.localtime())
        r = random.randint(10, 200)
        self.records[user_id]["score"] += r
        self._save_records()
        yield event.plain_result(f"签到成功！今天获得{r}个小鱼干，当前小鱼干数量：{self.records[user_id]['score']}")
        return
    @filter.command("查询数量")
    async def handle_query_score(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in self.records:
            score = self.records[user_id]["score"]
            yield event.plain_result(f"您的当前小鱼干数量为：{score}")
            return
        else:
            yield event.plain_result("您还没有签到记录，快去签到吧！")
            return
    @filter.command("今日老婆")
    async def _get_group_members(self, event: AstrMessageEvent) -> List[Dict[str, Any]]:
        try:
            group_id = event.get_group_id()
            if not group_id:
                logger.warning("无法获取群组ID")
                return []
            
            if event.get_platform_name() == "aiocqhttp":
                assert isinstance(event, AiocqhttpMessageEvent)
                client = event.bot
                payloads = {"group_id": group_id, "no_cache": True}
                return await client.api.call_action('get_group_member_list', **payloads)
            else:
                logger.warning(f"不支持的平台: {event.get_platform_name()}")
                return []
        except Exception as e: # 捕获所有可能的异常（不会分开分析）
            logger.error(f"获取群成员失败: {e}")
            return []
    async def handle_today_wife(self, event: AstrMessageEvent):
        if event.is_private_chat():
            yield event.plain_result("此命令仅限群聊使用！")
            return
        group_id = event.get_group_id()
        user_id = event.get_sender_id()
        if user_id not in self.records:
            self.records[user_id] = {"date": "", "score": 0,"wife": ""}
        if self.records[user_id]["wife"] != "":
            yield event.plain_result(f"您今天的老婆是：{self.records[user_id]['wife']}")
            return
        members = await self._get_group_members(event)
        if not members:
            yield event.plain_result("无法获取群成员列表，请稍后再试！")
            return
        available_members = [m for m in members if m["user_id"] != user_id]
        if not available_members:
            yield event.plain_result("群里没有单身成员，无法抽取老婆！")
            return
        excluded = [user_id] + [m["user_id"] for m in members if m["user_id"] != user_id]
        self.records[user_id]["wife"] = random.choice(available_members)["user_id"]
        if self._use_score_(self.records[user_id]["score"],10,user_id,event):
            avatar_url = f"https://q4.qlogo.cn/headimg_dl?dst_uin={self.records[user_id]['wife']}&spec=640"
            chain =[
                Comp.Image.fromURL(avatar_url),
                Comp.Text(f"恭喜你抽到了今天的老婆：{self.records[user_id]['wife']}！\n（使用了10小鱼干）")
            ]
            yield event.chain_result(chain)
        return




    async def terminate(self):
        try:
            self._save_records()
            logger.info("群聊签到插件资源已清理完毕")
        except Exception as e:
            logger.error(f"插件终止时出现错误: {e}")