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
        if not await self.should_notify(message):
            return
        self.send_notification(message)

    async def should_notify(self, message):
        level, muted = self.read_channel_notification_settings(message.channel)
        if level == discord.NotificationLevel.nothing:
            return False
        if level == discord.NotificationLevel.all_messages and not muted:
            return True
        # only_mentions or muted (still deliver mentions in muted channels)
        return await self.mentions_me(message)

    def read_channel_notification_settings(self, channel):
        """Resolve (NotificationLevel, muted) for a channel,
        falling back from channel -> category -> guild like the Discord client."""
        # Thread defaults to parent channel setting
        if isinstance(channel, discord.Thread):
            channel = channel.parent

        # DMs and group DMs default to notifying on all messages
        if getattr(channel, 'guild', None) is None:
            settings = channel.notification_settings
            level = settings.level
            if level == discord.NotificationLevel.default:
                level = discord.NotificationLevel.all_messages
            return level, bool(settings.muted)

        guild_settings = channel.guild.notification_settings
        channel_settings = channel.notification_settings
        muted = bool(channel_settings.muted) or bool(guild_settings.muted)
        level = channel_settings.level

        category = channel.category
        if category is not None:
            category_settings = category.notification_settings
            muted = muted or bool(category_settings.muted)
            if level == discord.NotificationLevel.default:
                level = category_settings.level

        if level == discord.NotificationLevel.default:
            level = guild_settings.level
        if level == discord.NotificationLevel.default:
            level = channel.guild.default_notifications

        return level, muted


    def send_notification(self, message):
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
