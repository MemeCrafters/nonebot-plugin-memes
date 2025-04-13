import re
import traceback
from dataclasses import dataclass
from typing import Callable, Optional

from meme_generator import ImageDecodeError, ImageEncodeError
from meme_generator.tools import image_operations
from nonebot.adapters import Bot, Event
from nonebot.exception import AdapterException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.utils import run_sync
from nonebot_plugin_alconna import (
    AlcMatches,
    Alconna,
    Args,
    Image,
    MultiVar,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension
from nonebot_plugin_alconna.uniseg.tools import image_fetch

from .utils import send_multiple_images


def flip_horizontal(img: bytes):
    return image_operations.flip_horizontal(img)


def flip_vertical(img: bytes):
    return image_operations.flip_vertical(img)


def rotate(num: Optional[float], img: bytes):
    return image_operations.rotate(img, num)


def resize(text: str, img: bytes):
    width = None
    height = None
    match1 = re.fullmatch(r"(\d{1,4})?[*xX, ](\d{1,4})?", text)
    match2 = re.fullmatch(r"(\d{1,3})%", text)
    if match1:
        w = match1.group(1)
        h = match1.group(2)
        if not w and h:
            height = int(h)
        elif w and not h:
            width = int(w)
        elif w and h:
            width = int(w)
            height = int(h)
    elif match2:
        image_info = image_operations.inspect(img)
        if not isinstance(image_info, image_operations.ImageInfo):
            return image_info
        ratio = int(match2.group(1)) / 100
        width = int(image_info.width * ratio)
        height = int(image_info.height * ratio)
    else:
        return "请使用正确的尺寸格式，如：100x100、100x、50%"
    return image_operations.resize(img, width, height)


def crop(text: str, img: bytes):
    image_info = image_operations.inspect(img)
    if not isinstance(image_info, image_operations.ImageInfo):
        return image_info

    match1 = re.fullmatch(r"(\d{1,4})[, ](\d{1,4})[, ](\d{1,4})[, ](\d{1,4})", text)
    match2 = re.fullmatch(r"(\d{1,4})[*xX, ](\d{1,4})", text)
    match3 = re.fullmatch(r"(\d{1,2})[:：比](\d{1,2})", text)
    if match1:
        left = int(match1.group(1))
        top = int(match1.group(2))
        right = int(match1.group(3))
        bottom = int(match1.group(4))
    else:
        if match2:
            width = int(match2.group(1))
            height = int(match2.group(2))
        elif match3:
            wp = int(match3.group(1))
            hp = int(match3.group(2))
            size = min(image_info.width / wp, image_info.height / hp)
            width = int(wp * size)
            height = int(hp * size)
        else:
            return "请使用正确的裁剪格式，如：0,0,100,100、100x100、2:1"
        left = (image_info.width - width) // 2
        top = (image_info.height - height) // 2
        right = left + width
        bottom = top + height
    return image_operations.crop(img, left, top, right, bottom)


def grayscale(img: bytes):
    return image_operations.grayscale(img)


def invert(img: bytes):
    return image_operations.invert(img)


def merge_horizontal(imgs: list[bytes]):
    return image_operations.merge_horizontal(imgs)


def merge_vertical(imgs: list[bytes]):
    return image_operations.merge_vertical(imgs)


def gif_split(img: bytes):
    return image_operations.gif_split(img)


def gif_merge(num: Optional[float], imgs: list[bytes]):
    return image_operations.gif_merge(imgs, num)


def gif_reverse(img: bytes):
    return image_operations.gif_reverse(img)


def gif_change_duration(text: str, img: bytes):
    p_float = r"\d{0,3}\.?\d{1,3}"
    if match := re.fullmatch(rf"({p_float})fps", text, re.I):
        duration = 1 / float(match.group(1))
    elif match := re.fullmatch(rf"({p_float})(m?)s", text, re.I):
        duration = (
            float(match.group(1)) / 1000 if match.group(2) else float(match.group(1))
        )
    else:
        image_info = image_operations.inspect(img)
        if not isinstance(image_info, image_operations.ImageInfo):
            return image_info
        duration = image_info.average_duration or 0.1
        if match := re.fullmatch(rf"({p_float})(?:x|X|倍速?)", text):
            duration /= float(match.group(1))
        elif match := re.fullmatch(rf"({p_float})%", text):
            duration /= float(match.group(1)) / 100
        else:
            return "请使用正确的倍率格式，如：0.5x、50%、20FPS、0.05s"
    if duration < 0.02:
        return (
            f"帧间隔必须大于 0.02 s（小于等于 50 FPS），\n"
            f"超过该限制可能会导致 GIF 显示速度不正常。\n"
            f"当前帧间隔为 {duration:.3f} s ({1 / duration:.1f} FPS)"
        )
    return image_operations.gif_change_duration(img, duration)


arg_image = Args["img", Image]
arg_images = Args["imgs", MultiVar(Image, "+")]
arg_num_image = Args["num?", float, None]["img", Image]
arg_num_images = Args["num?", float, None]["imgs", MultiVar(Image, "+")]
arg_text_image = Args["text", str]["img", Image]


@dataclass
class Command:
    keywords: tuple[str, ...]
    args: Args
    func: Callable


commands = [
    Command(("水平翻转", "左翻", "右翻"), arg_image, flip_horizontal),
    Command(("竖直翻转", "上翻", "下翻"), arg_image, flip_vertical),
    Command(("旋转",), arg_num_image, rotate),
    Command(("缩放",), arg_text_image, resize),
    Command(("裁剪",), arg_text_image, crop),
    Command(("灰度图", "黑白"), arg_image, grayscale),
    Command(("反相", "反色"), arg_image, invert),
    Command(("横向拼接",), arg_images, merge_horizontal),
    Command(("纵向拼接",), arg_images, merge_vertical),
    Command(("gif分解",), arg_image, gif_split),
    Command(("gif合成",), arg_num_images, gif_merge),
    Command(("gif倒放", "倒放"), arg_image, gif_reverse),
    Command(("gif变速",), arg_text_image, gif_change_duration),
]


image_operations_matcher = on_alconna(
    "图片操作", aliases={"图片工具"}, block=True, priority=11, use_cmd_start=True
)


@image_operations_matcher.handle()
async def _(matcher: Matcher):
    await matcher.finish(
        "简单图片操作，支持的操作：\n"
        + "\n".join(
            f"{i+1}、{'/'.join(command.keywords)}" for i, command in enumerate(commands)
        )
    )


def create_matcher(command: Command):
    command_matcher = on_alconna(
        Alconna(command.keywords[0], command.args),
        aliases=set(command.keywords[1:]),
        block=True,
        priority=11,
        use_cmd_start=True,
        extensions=[ReplyMergeExtension()],
    )

    @command_matcher.handle()
    async def _(
        bot: Bot,
        event: Event,
        state: T_State,
        matcher: Matcher,
        alc_matches: AlcMatches,
    ):
        async def fetch_image(image: Image):
            try:
                result = await image_fetch(event, bot, state, image)
                if not isinstance(result, bytes):
                    raise NotImplementedError
                return result
            except NotImplementedError:
                await matcher.finish("当前平台可能不支持下载图片")
            except AdapterException:
                logger.warning(traceback.format_exc())
                await matcher.finish("图片下载出错")

        args = alc_matches.all_matched_args
        if image := args.get("img"):
            args["img"] = await fetch_image(image)
        if images := args.get("imgs"):
            args["imgs"] = [await fetch_image(image) for image in images]

        result = await run_sync(command.func)(**args)

        if isinstance(result, str):
            await matcher.finish(result)
        elif isinstance(result, bytes):
            await UniMessage.image(raw=result).send()
        elif isinstance(result, list):
            await send_multiple_images(bot, event, result)
        elif isinstance(result, ImageDecodeError):
            await matcher.finish(f"图片解码出错：{result.error}")
        elif isinstance(result, ImageEncodeError):
            await matcher.finish(f"图片编码出错：{result.error}")


def create_matchers():
    for command in commands:
        create_matcher(command)


create_matchers()
