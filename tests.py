import unittest
from aiounittest import AsyncTestCase
from botbuilder.testing import DialogTestClient, DialogTestLogger
from app import DIALOG, init_func
from config import DefaultConfig

config = DefaultConfig()


class TestAsync(AsyncTestCase, unittest.TestCase):

    client = DialogTestClient("test", DIALOG)

    async def test_dialogs(self):
        reply = await self.client.send_activity("hello")
        self.assertEqual(reply.text, 'What can I help you with today?')
        reply = await self.client.send_activity("i want to travel")
        self.assertEqual(reply.text, "To what city would you like to travel?")


class Test(unittest.TestCase):

    app = init_func(None)

    def test_route(self):
        tr = "<PlainResource  "
        self.assertEqual([str(x).replace(tr, "")[:-1] for x in self.app.router.resources()][0], "/api/messages")

    def test_env_vars(self):
        self.assertEqual(config.PORT, 8000)



