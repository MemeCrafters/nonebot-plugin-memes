from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")

from . import matchers as matchers
from .config import Config, memes_config

memes_prefixes = memes_config.memes_command_prefixes
memes_prefix = memes_prefixes[0] if memes_prefixes else ""

__plugin_meta__ = PluginMetadata(
    name="表情包制作",
    description="制作各种沙雕表情包",
    usage=(
        "- 表情列表\n"
        "  发送“表情包制作”查看表情列表\n\n"
        "- 表情详情\n"
        "  发送“表情详情 + 关键词”查看表情详细信息和表情预览\n\n"
        "- 表情搜索\n"
        "  发送“表情搜索 + 关键词”查找相关的表情\n\n"
        "- 表情开关\n"
        "  - “超级用户”和“管理员”可以启用或禁用某些表情\n"
        "    发送“启用表情/禁用表情 + 关键词”，如：“禁用表情 摸”\n"
        "  - “超级用户” 可以设置某个表情包的管控模式（黑名单/白名单）\n"
        "    发送“全局启用表情 + 关键词”可将表情设为黑名单模式；\n"
        "    发送“全局禁用表情 + 关键词”可将表情设为白名单模式；\n\n"
        "- 表情使用\n"
        f"  发送 “{memes_prefix}关键词 + 图片/文字” 制作表情\n"
        "  可使用“自己”、“@某人”获取指定用户的头像作为图片，如“摸 自己”\n"
        "  可使用“@ + 用户id”指定任意用户获取头像，如“摸 @114514”\n"
        "  可将回复中的消息作为文字和图片的输入\n"
        "  指定用户时将使用用户昵称作为“图片名”\n"
        "  可使用“# + 名字”指定“图片名”，如“小天使 #name 自己”\n\n"
        "- 随机表情\n"
        "  发送“随机表情 + 图片/文字”可随机制作表情\n"
        "  随机范围为 图片/文字 数量符合要求的表情\n\n"
        "- 表情调用统计\n"
        "  发送 “[我的][全局]<时间段>表情调用统计 + [表情名]” 获取表情调用次数统计图\n"
        "  “我的”、“全局”、<时间段>、“表情名” 均为可选项\n"
        "  <时间段> 可以为：日、本日、周、本周、月、本月、年、本年\n"
        "  如：“我的今日表情调用统计 petpet”"
    ),
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-memes",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
)
