from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_waiter import waiter

from ..manager import meme_manager

search_matcher = on_alconna(
    Alconna("表情搜索", Args["meme_name", str]),
    aliases={"表情查找", "表情查询"},
    block=True,
    priority=11,
    use_cmd_start=True,
)


@search_matcher.handle()
async def _(matcher: Matcher, meme_name: str):
    searched_memes = meme_manager.search(meme_name, include_tags=True)
    if not searched_memes:
        await matcher.finish("没有找到相关表情！")

    num_per_page = 5
    total_page = (len(searched_memes) - 1) // num_per_page + 1
    page_num = 0

    async def show_page(add_footer: bool = False):
        start = page_num * num_per_page
        end = min(start + num_per_page, len(searched_memes))
        msg = "\n".join(
            f"{start + i + 1}. {meme.key} ({'/'.join(meme.info.keywords)})"
            + (f"\n    tags: {'、'.join(meme.info.tags)}" if meme.info.tags else "")
            for i, meme in enumerate(searched_memes[start:end])
        )
        if add_footer:
            msg += f"\n\npage {page_num + 1}/{total_page}，发送 '<' '>' 翻页"
        await matcher.send(msg)

    if total_page == 1:
        await show_page()
        await matcher.finish()

    LAST_PAGE = ["上一页", "上页", "上", "←", "<", "<-"]
    NEXT_PAGE = ["下一页", "下页", "下", "→", ">", "->"]

    @waiter(waits=["message"], keep_session=True, block=False)
    async def get_response(event: Event):
        return event.get_plaintext()

    while True:
        await show_page(add_footer=True)
        resp = await get_response.wait(timeout=30)
        if resp is None:
            await matcher.finish()

        elif resp.isdigit() and 1 <= (page := int(resp)) <= total_page:
            page_num = page - 1

        elif resp in LAST_PAGE:
            page_num = (page_num - 1) % total_page

        elif resp in NEXT_PAGE:
            page_num = (page_num + 1) % total_page

        else:
            await matcher.finish()
