from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent 
import astrbot.api.message_components as Comp
import os
import json
import time
import random


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
            return {"date": "", "score": ""}
        except Exception as e:
            logger.error(f"加载记录文件失败: {e}")
            return {"date": "", "score": ""}
    def _save_records(self):
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记录文件失败: {e}")
    @filter.command("签到")
    async def handle_sign_in(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.records:
            self.records[user_id] = {"date": "", "score": 0}
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
    async def terminate(self):
        try:
            self._save_records()
            logger.info("群聊签到插件资源已清理完毕")
        except Exception as e:
            logger.error(f"插件终止时出现错误: {e}")