from csv import Error
from os import error
import httpx
from typing import Any, Dict, Optional
from aiocache import cached

# 异步请求 JSON 数据
async def fetch_json(url: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}"}
    except httpx.RequestError as e:
        return {"error": f"请求发生错误: {e}"}
    
# 获取玩家数据
@cached(ttl=600)
async def get_playerdata( playername: str) -> Optional[Dict[str, Any]]:
    server_url = f"https://api.gametools.network/bfv/stats/?format_values=true&name={playername}&platform=pc&skip_battlelog=false&lang=zh-cn"
    data = await fetch_json(server_url)
    return data

# 获取玩家ID
@cached(ttl=600)
async def get_persona_id(username: str) -> Optional[str]:
    url_uid = f"https://api.bfvrobot.net/api/v2/bfv/checkPlayer?name={username}"
    try:
        user_data = await fetch_json(url_uid)
    except Exception as e:
        error_message = {"error":"{e}"} 
        return error_message
    else:
        if user_data and user_data.get("status") == 1 and user_data.get("message") == "successful":
            persona_id=user_data.get("data", {}).get("personaId")
            name=user_data.get("data", {}).get("name")
            user_data={"personaId":persona_id,"name":name}
            return user_data 
        else:
            return "error:player not found"

# 获取ban状态
@cached(ttl=600)
async def get_ban_data(person_id: str) -> Optional[Dict[str, Any]]:
    url_ban = f"https://api.bfban.com/api/player?personaId={person_id}"
    return await fetch_json(url_ban)

# 获取社区状态
@cached(ttl=600) #缓存装饰器
async def get_community_status(persona_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.bfvrobot.net/api/player/getCommunityStatus?personaId={persona_id}"
    return await fetch_json(url)

#获取pb记录
async def getpblist(personid: str):
    url = f'https://api.bfvrobot.net/api/player/getBannedLogsByPersonaId?personaId={personid}'
    data = await fetch_json(url)
    return data