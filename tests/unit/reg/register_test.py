import pytest

from telethon import events

from iahr.reg import Register
from iahr.config import IahrConfig


class TestRegister:
    def test_to_type(self):
        for etype in IahrConfig.PREFIXES.keys():
            event = etype()
            assert Register.to_type(event) == etype
            assert Register.to_type(etype) == etype
