from enum import IntEnum
from pathlib import Path
from typing import Any, Optional

import yaml
from meme_generator import Meme, get_memes, search_memes
from nonebot.compat import PYDANTIC_V2, model_dump, type_validate_python
from nonebot.log import logger
from nonebot_plugin_localstore import get_config_file
from pydantic import BaseModel

from .config import memes_config

config_path = get_config_file("nonebot_plugin_memes", "meme_manager.yml")


class MemeMode(IntEnum):
    BLACK = 0
    WHITE = 1


class MemeConfig(BaseModel):
    mode: MemeMode = MemeMode.BLACK
    white_list: list[str] = []
    black_list: list[str] = []

    if PYDANTIC_V2:
        from pydantic import field_serializer

        @field_serializer("mode")
        def get_eunm_value(self, v: MemeMode, info) -> int:
            return v.value
    else:

        class Config:
            use_enum_values = True


class MemeManager:
    def __init__(self, path: Path = config_path):
        self.__path = path
        self.__meme_config: dict[str, MemeConfig] = {}
        self.__meme_dict = {
            meme.key: meme
            for meme in filter(
                lambda meme: meme.key not in memes_config.memes_disabled_list,
                sorted(get_memes(), key=lambda meme: meme.key),
            )
        }
        self.__meme_names: dict[str, list[Meme]] = {}
        self.__load()
        self.__dump()
        self.__refresh_names()

    def get_meme(self, meme_key: str) -> Optional[Meme]:
        return self.__meme_dict.get(meme_key, None)

    def get_memes(self) -> list[Meme]:
        return list(self.__meme_dict.values())

    def block(self, user_id: str, meme_key: str):
        config = self.__meme_config[meme_key]
        if config.mode == MemeMode.BLACK and user_id not in config.black_list:
            config.black_list.append(user_id)
        if config.mode == MemeMode.WHITE and user_id in config.white_list:
            config.white_list.remove(user_id)
        self.__dump()

    def unblock(self, user_id: str, meme_key: str):
        config = self.__meme_config[meme_key]
        if config.mode == MemeMode.WHITE and user_id not in config.white_list:
            config.white_list.append(user_id)
        if config.mode == MemeMode.BLACK and user_id in config.black_list:
            config.black_list.remove(user_id)
        self.__dump()

    def change_mode(self, mode: MemeMode, meme_key: str):
        config = self.__meme_config[meme_key]
        config.mode = mode
        self.__dump()

    def find(self, meme_name: str) -> list[Meme]:
        meme_name = meme_name.lower()
        if meme_name in self.__meme_names:
            return self.__meme_names[meme_name]
        return []

    def search(self, meme_name: str, include_tags: bool = False) -> list[Meme]:
        meme_keys = search_memes(meme_name, include_tags=include_tags)
        meme_keys = [key for key in meme_keys if key in self.__meme_dict]
        return [self.__meme_dict[key] for key in meme_keys]

    def check(self, user_id: str, meme_key: str) -> bool:
        if meme_key not in self.__meme_config:
            return False
        config = self.__meme_config[meme_key]
        if config.mode == MemeMode.BLACK:
            if user_id in config.black_list:
                return False
            return True
        elif config.mode == MemeMode.WHITE:
            if user_id in config.white_list:
                return True
            return False
        return False

    def __load(self):
        raw_list: dict[str, Any] = {}
        if self.__path.exists():
            with self.__path.open("r", encoding="utf-8") as f:
                try:
                    raw_list = yaml.safe_load(f)
                except Exception:
                    logger.warning("表情列表解析失败，将重新生成")
        try:
            meme_list = {
                name: type_validate_python(MemeConfig, config)
                for name, config in raw_list.items()
            }
        except Exception:
            meme_list = {}
            logger.warning("表情列表解析失败，将重新生成")
        self.__meme_config = {
            meme_key: MemeConfig() for meme_key in self.__meme_dict.keys()
        }
        self.__meme_config.update(meme_list)

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        meme_list = {
            name: model_dump(config) for name, config in self.__meme_config.items()
        }
        with self.__path.open("w", encoding="utf-8") as f:
            yaml.dump(meme_list, f, allow_unicode=True)

    def __refresh_names(self):
        self.__meme_names = {}
        for meme in self.__meme_dict.values():
            names = set()
            names.add(meme.key.lower())
            for keyword in meme.info.keywords:
                names.add(keyword.lower())
            for shortcut in meme.info.shortcuts:
                names.add(shortcut.pattern.lower())
                if shortcut.humanized:
                    names.add(shortcut.humanized.lower())
            for name in names:
                if name not in self.__meme_names:
                    self.__meme_names[name] = []
                self.__meme_names[name].append(meme)


meme_manager = MemeManager()
