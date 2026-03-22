#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Callable, Optional


class AbstractProto(ABC):
    on_ready: Optional[Callable[[], None]] = None

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def force_reset(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    def __getattr__(
        self, item
    ):  # for handling some methods that are just specific to one protocol
        return lambda *args, **kwargs: None
