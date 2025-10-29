import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent 
import astrbot.api.message_components as Comp

@register("签到", "沸腾鱼", "一个简单的签到插件", "Beta1.0")
class GroupDaily(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config # 保存从框架传入的配置对象，用于后续读取用户配置
        self.data_dir = os.path.join("data", "plugins", "groupdaily") # 构建数据存储目录路径（/bot目录/data/plugins/groupdaily）
        self.records_file = os.path.join(self.data_dir, "groupdailyrecords.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self.records = self._load_records()
        logger.info("插件已加载")
    def _load_records(self) -> Dict[str, Any]:
        try: 
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"score":"","date":""}
        except Exception as e:
            logger.error(f"加载记录文件失败: {e}")
            return {"score":"","date":""}
    def _save_records(self):
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记录文件失败: {e}")
    def _is_new_day(self) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.records.get("date") != today
    @filter.command("签到")
    async def sign(self, event: AstrMessageEvent):
        async for result in self.sign_common(event, with_at=False):
            yield result
    async def sign_common(self, event, with_at=False):
        user_id = event.get_sender_id()
        if self._is_new_day():
            self.records["date"] = datetime.now().strftime("%Y-%m-%d")
            r = random.randint(10,100)
            self.records["score"] = str(int(self.records.get("score")) + r)
            yield event.plain_result(f"签到成功！获得小鱼干{r}，当前总小鱼干数量：{self.records['score']}")
            return
        else:
            yield event.plain_result("今日已签到，明日再来吧！")
            return
    async def terminate(self):
        try:
            self._save_records()
            logger.info("签到插件资源已清理完毕")
        except Exception as e:
            logger.error(f"插件终止时出现错误: {e}")