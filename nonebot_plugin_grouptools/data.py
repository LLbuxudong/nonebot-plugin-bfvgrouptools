from email.mime import base
import json
from pathlib import Path
import re
from venv import logger

from nonebot import require

require('nonebot_plugin_localstore')
from nonebot_plugin_localstore import get_data_file
import nonebot_plugin_localstore as store
from .utils import get_persona_id

# 获取插件缓存目录
cache_dir = store.get_plugin_cache_dir()
# 获取插件缓存文件
cache_file = store.get_plugin_cache_file("grouptools.json")
# 获取插件数据目录
data_dir = store.get_plugin_data_dir()
# 获取插件数据文件
data_file = store.get_plugin_data_file("grouptools.json")
# 获取插件配置目录
config_dir = store.get_plugin_config_dir()
# 获取插件配置文件
config_file = store.get_plugin_config_file("grouptools.json")

class Data:
    def __init__(self):
        self.players = {}
        self.data_file = data_file
        if not self.data_file.exists():
            self.data_file.parent.mkdir(exist_ok=True)
            self.save()
        else:
            self.load()

    def load(self):
        data = self.data_file.read_text('Utf-8')
        self.players = json.loads(data)

    def save(self):
        data = json.dumps(self.players)
        self.data_file.write_text(data, 'Utf-8')

class Cache:
    def __init__(self):
        self.players = {}
        self.cache_file = cache_file
        # self.cache_file = get_data_file('BF5', 'Players.json')
        if not self.cache_file.exists():
            self.cache_file.parent.mkdir(exist_ok=True)
            self.save()
        else:
            self.load()

    def load(self):
        data = self.cache_file.read_text('Utf-8')
        self.players = json.loads(data)

    def save(self):
        data = json.dumps(self.players)
        self.cache_file.write_text(data, 'Utf-8')

local_cache = Cache()
async def get_personid(name: str):
    name = name.strip()
    personid = local_cache.players.get(name.lower(), None)
    if personid:                            #缓存中有
        for key in local_cache.players:
            if key.lower == name.lower:
                name = key
        userdata = {name:personid}          #返回
        logger.info(f"{name}的personaid在缓存中,为{personid}")
        return userdata
    else:                                   #缓存中没有
        userdata = await get_persona_id(name)  
        if "error" in userdata:
            return userdata
        elif userdata:
            name = userdata.get("name")
            personid = userdata.get("personaId")
            userdata = {name:personid}
            local_cache.players[name] = personid
            local_cache.save()
            logger.info(f"{name}的personaid不在在缓存中,为{personid},已添加至缓存")
            return userdata
        else:
            return {"error":"1"} #player not found