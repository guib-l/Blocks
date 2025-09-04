#!/usr/bin/env python3
import os
import sys
import typing
import json
import uuid
import copy

from typing import Dict, Any, TypeVar, Type

class BaseJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        if isinstance(obj, (set,)):
            return list(obj)
        return super().default(obj)

class BaseBlockJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any):
        if isinstance(obj, obj.__class__):
            return obj.__str__()
        return super().default(obj)
