import os

import discord
from dotenv import load_dotenv
from email_client import gmail_create_draft

class DiscordClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        print("initial status {}, status {}, afk {}".format(self.initial_status, self.status, self.is_afk()))

    async def on_message(self, message):
        if message.author == self.user or message.is_acked():
            return
        if not await self.mentions_me(message):
            return
        print("{} in #{}: {}".format(message.author, message.channel, message.content), end=" ==> ")
        print("Sending email")
        gmail_create_draft(message)

    async def mentions_me(self, message):
        if type(message.channel) == discord.channel.DMChannel or type(message.channel) == discord.channel.GroupChannel:
            return True
        for role in message.role_mentions:
            if self.user in await role.fetch_members():
                return True
        return self.user.mentioned_in(message)

if __name__ == '__main__':
    load_dotenv()
    client = DiscordClient(status=discord.Status.offline)
    client.run(os.environ["DISCORD_TOKEN"])
