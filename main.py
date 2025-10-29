from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
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
            if path.exists(self.records_file):
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
    
