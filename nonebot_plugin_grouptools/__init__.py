import os
from dotenv import load_dotenv
from nonebot import on_request,on_notice
from nonebot.params import CommandArg
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
GroupRequestEvent, MessageEvent, Message, Bot,GroupIncreaseNoticeEvent,MessageSegment
)
from nonebot import require

require("nonebot_plugin_localstore")

from .player_status import communitystatus,player_infomation
from .data import Cache,get_personid
from .pb import get_pblist

cache = Cache()
# 加载 .env 文件
load_dotenv()
# 从 .env 文件中获取允许的群号
ALLOWED_GROUPS = set(map(int, os.getenv('ALLOWED_GROUPS', '').split(',')))



request_matcher = on_request()
notice_matcher = on_notice()
requests: dict = {}

banstatus = on_command("player",aliases={"玩家状态"},priority=5, block=True)
playerpb = on_command("pb=", aliases={"屏蔽="}, priority=5, block=True)

#查询玩家的bfban和bfvrobot状态
@banstatus.handle()
async def handle_banstatus(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    name = str(arg).strip()
    message = await communitystatus(name)
    await banstatus.finish(message) 

#自动加群
@request_matcher.handle()
async def handle_intogroup(event: GroupRequestEvent, bot: Bot):
 if event.group_id in ALLOWED_GROUPS:
    _, user_name = event.comment.split('\n')
    user_name = user_name.lstrip('答案：')
    response = await get_personid(user_name)
    if response and "error" not in response:
        name =response.get('name',None)
        perosnid = response.get('personaId',None)
        requests[event.user_id] = response.get('name', user_name)
        cache.players[name] = perosnid
        cache.save() #添加缓存
        
        await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True)
        await request_matcher.finish()
    else:
        reason  = response.get("error","未知错误")
        if reason == "1":
            await bot.set_group_add_request(
                flag=event.flag, sub_type=event.sub_type,
                approve=False, reason=F'未找到名为 {user_name} 的玩家！请检查输入是否正确，然后再次尝试。'
            )
            await bot.send_group_msg(
            group_id=event.group_id,  # 用请求的群 ID
            message=F'收到QQ:{event.user_id}的加群申请\n提供的ID为:{user_name}\n已自动拒绝---原因:错误的ID'
            )
            await request_matcher.finish()
        elif reason  == "2":
            error_message = reason.get("error","未知错误").get("2","未知错误")
            await bot.send_group_msg(
            group_id=event.group_id,  # 用请求的群 ID
            message=F'收到QQ:{event.user_id}的加群申请\n提供的ID为:{user_name}\n由于未知错误无法判断,请管理员手动处理\n错误原因:\n'
            )
            await request_matcher.finish()
#入群通知
@notice_matcher.handle()
async def _(event: GroupIncreaseNoticeEvent, bot: Bot):
 if event.group_id in  ALLOWED_GROUPS:
    if user_name := requests.pop(event.user_id, None):
        await bot.set_group_card(group_id=event.group_id, user_id=event.user_id, card=user_name)
        player_infomation_data = await player_infomation(user_name)#获取玩家游戏内数据
        await notice_matcher.finish(F'欢迎新人加入！已自动修改您的群名片为游戏名称\n{player_infomation_data}', at_sender=True)
    await notice_matcher.finish('未找到您的申请记录，请联系管理员。', at_sender=True)

@playerpb.handle()
async def handle_playerpb(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    name = arg.extract_plain_text().strip()
    image = await get_pblist(name)
    await bot.send(event,MessageSegment.image(image),reply_message=event.message, at_sender=True)