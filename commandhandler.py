class CommandHandler:

    def __init__(self):
        self._functions = {
            'ping': self.ping
        }

    async def resolve(self, cmd, args, msgctx, client):
        res = await self._functions[cmd](args, msgctx, client)
        await msgctx.channel.send(res)

    @staticmethod
    async def ping(*args):
        return 'Pong!'
