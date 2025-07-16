from typing import Any, Dict, Optional
from nonebot.log import logger


from .utils import get_playerdata,get_ban_data,get_community_status
from .data import Data,Cache,get_personid

# ban状态描述
status_descriptions = {
    0: "未处理", 1: "石锤", 2: "待自证", 3: "MOSS自证", 4: "无效举报",
    5: "讨论中", 6: "等待确认", 7: "空", 8: "刷枪", 9: "上诉", 'None': "无记录", 'null': "无记录",
}


#获取所有状态
async def communitystatus(name: str) -> Optional[str]:
    userdata = await get_personid(name)
    if "error"in userdata:
        return userdata
    else:
        persona_id = next(iter(userdata.values()))
        playername = next(iter(userdata.keys()))
        bandata = await get_ban_data( persona_id) #处理联ban状态
        robotdata =  await get_community_status( persona_id) #处理bfvrobot状态
        if bandata is None:
                banstat = "无记录"
                banurl = False
        else:
                status = bandata.get("data", {}).get("status")
                # 处理 None 和 'null'
                if status is None or status == 'null':
                    banstat = "无记录" 
                    banurl = False
                else:
                    banstat = status_descriptions.get(status, "未知状态😭")
                    banurl = True
        robotstat = robotdata.get("data",{}).get("operationStatusName","未知😰")                         
        robotstatreasons = robotdata.get("data",{}).get("reasonStatusName","未知😡")
        if banurl ==  True:
            communitystatus = (f"EAID:{playername}\nPID:{persona_id}\nBFBAN状态：{banstat}\n机器人服游戏状态：{robotstat}\n机器人服数据库状态：{robotstatreasons}\n————BFBAN链接————\nhttps://bfban.com/player/{persona_id}")
        else:
            communitystatus = (f"EAID:{playername}\nPID:{persona_id}\nBFBAN状态：{banstat}\n机器人服游戏状态：{robotstat}\n机器人服数据库状态：{robotstatreasons}")   
        return communitystatus

async def player_infomation(user_name: str) -> Optional[str]:
        userdata = await get_playerdata(user_name)  # 查询玩家数据
        if 'error' not in userdata:
            # 提取数据
                user_name = userdata.get('userName', '未知')
                rank = userdata.get('rank', '未知')
                accuracy = userdata.get('accuracy', '未知')
                headshots = userdata.get('headshots', '未知')
                killDeath = userdata.get('killDeath', '未知')
                infantryKillsPerMinute = userdata.get('infantryKillsPerMinute', '未知')
                extracted_data = {
                "等级": rank,
                "命中率": accuracy,
                "爆头率": headshots,
                "KD": killDeath,
                "KP": infantryKillsPerMinute,
                }
                communityatatus_data = await communitystatus(user_name)  
                extracted_data_str = "\n".join([f"{key}: {value}" for key, value in extracted_data.items()])
                return (f"欢迎来到本群组\n查询到{user_name}的基础数据如下：\n{extracted_data_str}\n{communityatatus_data}")
