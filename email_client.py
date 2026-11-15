import os.path

import discord.channel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDS = None


def init_gmail_client():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  global CREDS

  if os.path.exists("token.json"):
    CREDS = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not CREDS or not CREDS.valid:
    if CREDS and CREDS.expired and CREDS.refresh_token:
      CREDS.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      CREDS = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(CREDS.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=CREDS)

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")

def gmail_create_draft(discord_message):
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  global CREDS

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=CREDS)

    message = EmailMessage()

    message.set_content(discord_message.clean_content)

    user, domain = os.environ["GMAIL_ADDRESS"].split("@", 1)
    message["To"] = "{}+discordnotification@{}".format(user, domain)
    message["From"] = "{} <{}+{}@{}>".format(discord_message.author, user, discord_message.channel, domain)
    location = discord_message.channel
    if type(location) == discord.channel.DMChannel or type(location) == discord.channel.GroupChannel:
      location = "DMs"
    message["Subject"] = "{} in {}".format(discord_message.author, location)

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
      service.users()
      .messages()
      .send(userId="me", body=create_message)
      .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message

if __name__ == "__main__":
  init_gmail_client()