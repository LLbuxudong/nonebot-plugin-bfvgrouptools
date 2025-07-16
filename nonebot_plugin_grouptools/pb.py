from datetime import datetime
from email import message
from email.mime import image
from logging import debug
from re import DEBUG
from traceback import print_list
from venv import logger
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Any, Dict, Optional

from .data import get_personid
from .utils import getpblist

BanType = {
    '0':  '',
    '1':  'BFBAN实锤或即将实锤',
    '2':  'ROBOT全局黑名单',
    '3':  '自定义原因',
    '4':  '',
    '5':  '',
    '6':  '',
    '7':  '',
    '8':  '',
    '9':  '数据异常',
    '10': '',
    '11': '小电视屏蔽/踢人',
    '12': '',
    '13': '',
}

async def create_text_image_bytes(text: str, font_path: str, font_size: int) -> BytesIO:
    """
    通过pIL创建文本图片并返回 BytesIO 字节流
    """
    # 估算图像大小（可动态计算）
    img = Image.new('RGBA', (800, 100 + (len(text.split('\n')) + 1) * (font_size + 10)), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

    line_spacing = 10
    lines = text.split('\n')
    y = 100

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (img.width - text_width) / 2
        draw.text((x, y), line, fill=(255, 255, 255), font=font)
        y += text_height + line_spacing

    # 将图像写入 BytesIO
    byte_io = BytesIO()
    img.save(byte_io, format="PNG")
    img_bytes = byte_io.getvalue()

    return img_bytes

async def format_iso_time(time_str: str, fmt: str = "%Y年%m月%d日 %H:%M:%S") -> str:
    """
    将 ISO 时间字符串转为指定格式
    
    Args:
        time_str (str): ISO 格式时间字符串
        fmt (str): 输出格式，默认是 "YYYY年MM月DD日 HH:MM:SS"
    
    Returns:
        str: 格式化后的时间字符串
    """
    # 去掉 Z 并加上时区信息以便正确解析
    dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    return dt.strftime(fmt)

async def get_pblist(name: str) -> Optional[Dict[str, Any]]:
    """获取玩家pb列表

    Args:
        personid (str): 玩家ID

    Returns:
        Optional[Dict[str, Any]]: 玩家pb列表
    """
    userdata = await get_personid(name)
    if "error" in userdata:
        return userdata
    else:
        personid = next(iter(userdata.values()))
        name = next(iter(userdata.keys()))
        pblist = await getpblist(personid)
        pblist = pblist.get('data', [])
        if pblist == None:
            message = f"玩家{name}({personid}没有封禁记录)"
            image = await create_text_image_bytes(text=message, font_path="STXINWEI.TTF", font_size=24)
        else:
            text = ""#pb记录初始值
            for key,value in enumerate(pblist):
                text += f"\n--- 第 {key + 1} 条封禁记录 ---\n"
                ban_type_code = str(value.get('banType'))  # 获取 banType 并转为字符串
                ban_type_desc = BanType.get(ban_type_code, '未知类型')  # 查找对应的描述
                server_name = value.get('serverName')
                reason = value.get('reason')
                expire_time = await format_iso_time(value.get('createTime'))
                text +=f'服务器：{server_name}\n封禁类型: {ban_type_desc} ({ban_type_code})\n原因: {reason},\n时间: {expire_time}\n'
                image = await create_text_image_bytes(text=text, font_path="STXINWEI.TTF", font_size=24)
        return image