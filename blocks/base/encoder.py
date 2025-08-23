#!/usr/bin/env python3
import os
import sys
import typing
import json
import uuid
import copy


class BaseJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        if isinstance(obj, (set,)):
            return list(obj)
        return super().default(obj)


