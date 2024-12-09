import datetime
import typing as t

from datetime import timedelta

import yaml

from pydantic import BaseModel

from app import settings


class Config(BaseModel):
    cache: bool = True

    class Config:
        extra = "allow"


class ConfigLoader:
    def __init__(self, config_path, reload_interval=5):
        self.config_path = config_path
        self.reload_interval = timedelta(seconds=reload_interval)
        self.last_reload: t.Optional[datetime] = None
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.last_reload = datetime.datetime.now()
            return Config(**yaml.safe_load(f))

    def get_config(self):
        now = datetime.datetime.now()
        if now - self.last_reload > self.reload_interval:
            self.config = self.load_config()
            self.last_reload = now
        return self.config


config = ConfigLoader(settings.CONFIG_PATH)
