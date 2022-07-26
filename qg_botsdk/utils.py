# !/usr/bin/env python3
# encoding: utf-8
from typing import Dict, Any
try:
    from yaml import safe_load
except (ImportError, ModuleNotFoundError):
    safe_load = None


def read_yaml(yaml_path) -> Dict[str, Any]:
    assert safe_load, '如需使用read_yaml函数，必须先pip install pyyaml'
    with open(yaml_path, "r", encoding="utf-8") as f:
        return safe_load(f)
