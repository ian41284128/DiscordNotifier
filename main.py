import os

from dotenv import load_dotenv

from discord_listener import DiscordClient
from email_client import init_gmail_client

load_dotenv()

if __name__ == "__main__":
  init_gmail_client()
  client = DiscordClient()
  client.run(os.environ["DISCORD_TOKEN"])