import imghdr
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Annotated
from zipfile import ZIP_BZIP2, ZipFile

from meme_generator import Meme
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot_plugin_alconna import CustomNode, Image, UniMessage
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import waiter

from ..config import memes_config
from ..manager import meme_manager


def get_user_id(uninfo: Uninfo) -> str:
    return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"


UserId = Annotated[str, Depends(get_user_id)]


async def find_meme(matcher: Matcher, meme_name: str) -> Meme:
    found_memes = meme_manager.find(meme_name)
    found_num = len(found_memes)

    if found_num == 0:
        searched_memes = meme_manager.search(meme_name)[:5]
        if searched_memes:
            await matcher.finish(
                f"表情 {meme_name} 不存在，你可能在找：\n"
                + "\n".join(
                    f"* {meme.key} ({'/'.join(meme.info.keywords)})"
                    for meme in searched_memes
                )
            )
        else:
            await matcher.finish(f"表情 {meme_name} 不存在！")

    if found_num == 1:
        return found_memes[0]

    await matcher.send(
        f"找到 {found_num} 个表情，请发送编号选择：\n"
        + "\n".join(
            f"{i + 1}. {meme.key} ({'/'.join(meme.info.keywords)})"
            for i, meme in enumerate(found_memes)
        )
    )

    @waiter(waits=["message"], keep_session=True)
    async def get_response(event: Event):
        return event.get_plaintext()

    for _ in range(3):
        resp = await get_response.wait(timeout=15)
        if resp is None:
            await matcher.finish()
        elif not resp.isdigit():
            await matcher.send("输入错误，请输入数字")
            continue
        elif not (1 <= (index := int(resp)) <= found_num):
            await matcher.send("输入错误，请输入正确的数字")
            continue
        else:
            return found_memes[index - 1]

    await matcher.finish()


async def send_multiple_images(bot: Bot, event: Event, images: list[bytes]):
    config = memes_config.memes_multiple_image_config

    if len(images) <= config.direct_send_threshold:
        await UniMessage(Image(raw=img) for img in images).send()

    else:
        if config.send_zip_file:
            zip_file = zip_images(images)
            time_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"memes_{time_str}.zip"
            await send_file(bot, event, filename, zip_file.getvalue())

        if config.send_forward_msg:
            await send_forward_msg(bot, event, images)


def zip_images(files: list[bytes]):
    output = BytesIO()
    with ZipFile(output, "w", ZIP_BZIP2) as zip_file:
        for i, file in enumerate(files):
            ext = imghdr.what(None, h=file)
            zip_file.writestr(f"{i}.{ext}", file)
    return output


async def send_file(bot: Bot, event: Event, filename: str, content: bytes):
    try:
        from nonebot.adapters.onebot.v11 import Bot as V11Bot
        from nonebot.adapters.onebot.v11 import Event as V11Event
        from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent

        async def upload_file_v11(
            bot: V11Bot, event: V11Event, filename: str, content: bytes
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                with open(Path(temp_dir) / filename, "wb") as f:
                    f.write(content)
                if isinstance(event, V11GMEvent):
                    await bot.call_api(
                        "upload_group_file",
                        group_id=event.group_id,
                        file=f.name,
                        name=filename,
                    )
                else:
                    await bot.call_api(
                        "upload_private_file",
                        user_id=event.get_user_id(),
                        file=f.name,
                        name=filename,
                    )

        if isinstance(bot, V11Bot) and isinstance(event, V11Event):
            await upload_file_v11(bot, event, filename, content)
            return

    except ImportError:
        pass

    await UniMessage.file(raw=content, name=filename, mimetype="application/zip").send()


async def send_forward_msg(
    bot: Bot,
    event: Event,
    images: list[bytes],
):
    try:
        from nonebot.adapters.onebot.v11 import Bot as V11Bot
        from nonebot.adapters.onebot.v11 import Event as V11Event
        from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
        from nonebot.adapters.onebot.v11 import Message as V11Msg
        from nonebot.adapters.onebot.v11 import MessageSegment as V11MsgSeg

        async def send_forward_msg_v11(
            bot: V11Bot,
            event: V11Event,
            name: str,
            uin: str,
            msgs: list[V11Msg],
        ):
            messages = [
                {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}
                for msg in msgs
            ]
            if isinstance(event, V11GMEvent):
                await bot.call_api(
                    "send_group_forward_msg", group_id=event.group_id, messages=messages
                )
            else:
                await bot.call_api(
                    "send_private_forward_msg",
                    user_id=event.get_user_id(),
                    messages=messages,
                )

        if isinstance(bot, V11Bot) and isinstance(event, V11Event):
            await send_forward_msg_v11(
                bot,
                event,
                "memes",
                bot.self_id,
                [V11Msg(V11MsgSeg.image(img)) for img in images],
            )
            return

    except ImportError:
        pass

    uid = bot.self_id
    name = "memes"
    time = datetime.now()
    await UniMessage.reference(
        *[CustomNode(uid, name, UniMessage.image(raw=img), time) for img in images]
    ).send()
