<div align="center">

  <a href="https://nonebot.dev/">
    <img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
  </a>

# nonebot-plugin-memes

_✨ [Nonebot2](https://github.com/nonebot/nonebot2) 表情包制作插件 ✨_

<p align="center">
  <img src="https://img.shields.io/github/license/noneplugin/nonebot-plugin-memes" alt="license">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.3.0+-red.svg" alt="NoneBot">
  <a href="https://pypi.org/project/nonebot-plugin-memes">
    <img src="https://badgen.net/pypi/v/nonebot-plugin-memes" alt="pypi">
  </a>
  <a href="https://jq.qq.com/?_wv=1027&k=wDVNrMdr">
    <img src="https://img.shields.io/badge/QQ%E7%BE%A4-682145034-orange" alt="qq group">
  </a>
</p>

</div>

本插件是 [表情包生成器 meme-generator](https://github.com/MemeCrafters/meme-generator-rs) 的 [Nonebot2](https://github.com/nonebot/nonebot2) 对接插件，方便通过聊天机器人制作表情包

另有 [nonebot-plugin-memes-api](https://github.com/noneplugin/nonebot-plugin-memes-api)（表情包制作 调用 api 版本），可以将 NoneBot 插件与 `meme-generator` 分开部署

`nonebot-plugin-memes-api` 与 `nonebot-plugin-memes` 功能上基本一致

### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_memes
```

- 使用 pip

```
pip install nonebot_plugin_memes
```

并按照 [NoneBot 加载插件](https://nonebot.dev/docs/tutorial/create-plugin#加载插件) 加载插件

#### 配置驱动器 ​

插件需要“客户端型驱动器”（如 httpx）来下载图片等，驱动器安装和配置参考 [NoneBot 选择驱动器](https://nonebot.dev/docs/advanced/driver)

同时需要在 `.env.*` 配置文件中启用对应的驱动器，例如：

```
DRIVER=~fastapi+~httpx+~websockets
```

### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `memes_command_prefixes`

- 类型：`List[str] | None`
- 默认：`None`
- 说明：命令前缀（仅作用于制作表情的命令）；如果不设置默认使用 [NoneBot 命令前缀](https://nonebot.dev/docs/appendices/config#command-start-和-command-separator)

#### `memes_disabled_list`

- 类型：`List[str]`
- 默认：`[]`
- 说明：禁用的表情包列表，需填写表情的`key`，可在 [meme-generator 表情列表](https://github.com/MemeCrafters/meme-generator-rs/wiki/表情列表) 中查看。若只是临时关闭，可以用下文中的“表情包开关”

#### `memes_check_resources_on_startup`

- 类型：`bool`
- 默认：`True`
- 说明：是否在启动时检查 `meme-generator` 资源

#### `memes_params_mismatch_policy`

- 类型：`MemeParamsMismatchPolicy`
- 说明：图片/文字数量不符时的处理方式，其中具体设置项如下：
  - `too_much_text`
    - 类型：`str`
    - 默认：`"ignore"`
    - 可选项：`"ignore"`（忽略本次命令）、 `"prompt"`（发送提示）, `"drop"`（去掉多余的文字）
  - `too_few_text`
    - 类型：`str`
    - 默认：`"ignore"`
    - 可选项：`"ignore"`（忽略本次命令）、 `"prompt"`（发送提示）, `"get"`（交互式获取所需的文字）
  - `too_much_image`
    - 类型：`str`
    - 默认：`"ignore"`
    - 可选项：`"ignore"`（忽略本次命令）、 `"prompt"`（发送提示）, `"drop"`（去掉多余的图片）
  - `too_few_image`
    - 类型：`str`
    - 默认：`"ignore"`
    - 可选项：`"ignore"`（忽略本次命令）、 `"prompt"`（发送提示）, `"get"`（交互式获取所需的图片）
- `memes_params_mismatch_policy` 在 `.env` 文件中的设置示例如下：

```
memes_params_mismatch_policy='
{
  "too_much_text": "drop",
  "too_few_text": "get",
  "too_much_image": "drop",
  "too_few_image": "get"
}
'
```

#### `memes_use_sender_when_no_image`

- 类型：`bool`
- 默认：`False`
- 说明：在表情需要至少 1 张图且没有输入图片时，是否使用发送者的头像

#### `memes_use_default_when_no_text`

- 类型：`bool`
- 默认：`False`
- 说明：在表情需要至少 1 段文字且没有输入文字时，是否使用默认文字

#### `memes_random_meme_show_info`

- 类型：`bool`
- 默认：`True`
- 说明：使用“随机表情”时是否同时发出表情关键词

#### `memes_list_image_config`

- 类型：`MemeListImageConfig`
- 说明：表情列表图相关设置，其中具体设置项如下：
  - `sort_by`
    - 类型：`str`
    - 默认：`"keywords_pinyin"`
    - 说明：表情排序方式，可用值：`"key"`（按表情 `key` 排序）、`"keywords"`（按表情关键词排序）、`keywords_pinyin`（按表情关键词拼音排序）、`"date_created"`（按表情添加时间排序）、`"date_modified"`（按表情修改时间排序）
  - `sort_reverse`
    - 类型：`bool`
    - 默认：`False`
    - 说明：是否倒序排序
  - `text_template`
    - 类型：`str`
    - 默认：`"{index}. {keywords}"`
    - 说明：表情显示文字模板，可用变量：`"{index}"`（序号）、`"{key}"`（表情名）、`"{keywords}"`（关键词）、`"{shortcuts}"`（快捷指令）、`"{tags}"`（标签）
  - `add_category_icon`
    - 类型：`bool`
    - 默认：`True`
    - 说明：是否添加图标以表示类型，即“图片表情包”和“文字表情包”
  - `label_new_timedelta`
    - 类型：`timedelta`
    - 默认：`timedelta(days=30)`
    - 说明：表情添加时间在该时间间隔以内时，添加 `new` 图标
  - `label_hot_threshold`
    - 类型：`int`
    - 默认：`21`
    - 说明：单位：次；表情在 `label_hot_days` 内的调用次数超过该阈值时，添加 `hot` 图标
  - `label_hot_days`
    - 类型：`int`
    - 默认：`7`
    - 说明：单位：天；表情调用次数统计周期
- `memes_list_image_config` 在 `.env` 文件中的设置示例如下：

```
memes_list_image_config='
{
  "sort_by": "keywords",
  "sort_reverse": false,
  "text_template": "{index}. {keywords}",
  "add_category_icon": true,
  "label_new_timedelta": "P30D",
  "label_hot_threshold": 21,
  "label_hot_days": 7
}
'
```

#### `memes_multiple_image_config`

- 类型：`MultipleImageConfig`
- 说明：发送多张图片时的相关设置，其中具体设置项如下：
  - `direct_send_threshold`
    - 类型：`int`
    - 默认：`10`
    - 说明：发送图片数量大于该数目时，不再直接发送，而是以文件或合并转发消息的形式发送
  - `send_zip_file`
    - 类型：`bool`
    - 默认：`True`
    - 说明：发送图片数量大于 `direct_send_threshold` 时，是否打包为zip以文件形式发送
  - `send_forward_msg`
    - 类型：`bool`
    - 默认：`False`
    - 说明：发送图片数量大于 `direct_send_threshold` 时，是否发送合并转发消息
- `memes_multiple_image_config` 在 `.env` 文件中的设置示例如下：

```
memes_multiple_image_config='
{
  "direct_send_threshold": 10,
  "send_zip_file": true,
  "send_forward_msg": true
}
'
```

### 使用

**以下命令需要加 [NoneBot 命令前缀](https://nonebot.dev/docs/appendices/config#command-start-和-command-separator) (默认为`/`)，可自行添加空字符**

#### 表情列表

- 发送 “表情包制作” 查看表情列表

#### 表情详情

- 发送 “表情详情 + 关键词” 查看表情详细信息和表情预览

#### 表情搜索

- 发送 “表情搜索 + 关键词” 查找相关的表情

#### 表情包开关

“超级用户” 和 “管理员” 可以启用或禁用某些表情

- 发送 “启用表情/禁用表情 + 关键词”，如：`禁用表情 摸`

“超级用户” 可以设置某个表情包的管控模式（黑名单/白名单）

- 发送 “全局启用表情 + 关键词” 可将表情设为黑名单模式；

- 发送 “全局禁用表情 + 关键词” 可将表情设为白名单模式；

> [!NOTE]
>
> “超级用户” 可通过 [NoneBot SuperUsers](https://nonebot.dev/docs/appendices/config#superusers) 设置

#### 表情使用

- 发送 “关键词 + 图片/文字” 制作表情

可使用 “自己”、“@某人” 获取指定用户的头像作为图片

可使用 “@ + 用户 id” 指定任意用户获取头像，如 `摸 @114514`

可将回复中的消息作为文字和图片的输入

指定用户时将使用用户昵称作为“图片名”

可使用“# + 名字”指定“图片名”，如 `小天使 #name 自己`

示例：

<div align="left">
  <img src="https://s2.loli.net/2023/03/10/UDTOuPnwk3emxv4.png" width="250" />
</div>

> [!NOTE]
>
> - 为避免误触发，当输入的 图片/文字 数量不符时，默认不会进行提示，可通过 `memes_params_mismatch_policy` 配置项进行设置
> - 本插件通过 [nonebot-plugin-uninfo](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo) 插件获取用户名和用户头像，具体平台支持范围可前往该插件查看
> - 本插件通过 [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 来实现多适配器消息接收、获取图片输入、获取回复内容等，相关问题可前往该插件查看

#### 随机表情

- 发送 “随机表情 + 图片/文字” 可随机制作表情

随机范围为 图片/文字 数量符合要求的表情

#### 表情调用统计

- 发送 “[我的][全局]<时间段>表情调用统计 [表情名]” 获取表情调用次数统计图

“我的”、“全局”、<时间段>、“表情名” 均为可选项

<时间段> 可以为：日、本日、周、本周、月、本月、年、本年

如：`我的今日表情调用统计 petpet`

### 相关插件

- [nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna) 强大的 Nonebot2 命令匹配拓展，支持富文本/多媒体解析，跨平台消息收发
- [nonebot-plugin-uninfo](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo) Nonebot2 多平台的会话信息(用户、群组、频道)获取插件
- [nonebot-plugin-orm](https://github.com/nonebot/plugin-orm) SQLAlchemy support for NoneBot2
