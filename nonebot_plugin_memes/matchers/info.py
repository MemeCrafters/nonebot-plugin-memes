from typing import Union

from meme_generator import BooleanOption, FloatOption, IntegerOption, StringOption
from nonebot.matcher import Matcher
from nonebot.utils import run_sync
from nonebot_plugin_alconna import Alconna, Args, Image, UniMessage, on_alconna

from .utils import find_meme

info_matcher = on_alconna(
    Alconna("表情详情", Args["meme_name", str]),
    aliases={"表情帮助", "表情示例"},
    block=True,
    priority=11,
    use_cmd_start=True,
)


@info_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    meme = await find_meme(matcher, meme_name)
    info = meme.info
    params = info.params
    keywords = "、".join([f'"{keyword}"' for keyword in info.keywords])
    shortcuts = "、".join(
        [f'"{shortcut.humanized or shortcut.pattern}"' for shortcut in info.shortcuts]
    )
    tags = "、".join([f'"{tag}"' for tag in info.tags])

    image_num = f"{params.min_images}"
    if params.max_images > params.min_images:
        image_num += f" ~ {params.max_images}"

    text_num = f"{params.min_texts}"
    if params.max_texts > params.min_texts:
        text_num += f" ~ {params.max_texts}"

    default_texts = ", ".join([f'"{text}"' for text in params.default_texts])

    def option_info(
        option: Union[BooleanOption, StringOption, IntegerOption, FloatOption],
    ) -> str:
        parser_flags = option.parser_flags
        short_aliases = parser_flags.short_aliases
        if parser_flags.short:
            short_aliases.insert(0, option.name[0])
        long_aliases = parser_flags.long_aliases
        if parser_flags.long:
            long_aliases.insert(0, option.name)
        text = f"{'/'.join([f'-{flag}' for flag in short_aliases])}"
        if text:
            text += "/"
        text += f"{'/'.join([f'--{flag}' for flag in long_aliases])}"

        if not isinstance(option, BooleanOption):
            text += f" <{option.name.upper()}>"

        text += f"  {option.description}"
        addition_texts = []
        if isinstance(option, (IntegerOption, FloatOption)):
            if option.minimum is not None:
                addition_texts.append(f"最小值：{option.minimum}")
            if option.maximum is not None:
                addition_texts.append(f"最大值：{option.maximum}")
        if isinstance(option, StringOption):
            if option.choices:
                choices = "、".join([f'"{c}"' for c in option.choices])
                addition_texts.append(f"可选值：{choices}")
        if option.default is not None:
            addition_texts.append(f"默认值：{option.default}")
        addition_text = "，".join(addition_texts)
        if addition_text:
            text += f"（{addition_text}）"
        return text

    options_info = "\n".join(["  " + option_info(option) for option in params.options])

    info = (
        f"表情名：{meme.key}"
        + f"\n关键词：{keywords}"
        + (f"\n快捷指令：{shortcuts}" if shortcuts else "")
        + (f"\n标签：{tags}" if tags else "")
        + f"\n需要图片数目：{image_num}"
        + f"\n需要文字数目：{text_num}"
        + (f"\n默认文字：[{default_texts}]" if default_texts else "")
        + (f"\n其他选项：\n{options_info}" if options_info else "")
    )
    msg = UniMessage.text(info)

    img = await run_sync(meme.generate_preview)()
    if isinstance(img, bytes):
        msg += "\n表情预览：\n"
        msg += Image(raw=img)
    await msg.finish()
