# Discord Bots

This repository hosts multiple Discord bots and bot modules in one Python application:

- **Message Scheduler** (`/ms`): create, schedule, preview, and manage messages.
- **Ticket Bot** (`/ticket`): manage tickets, rewards, and trades.
- **Ticket Bot Admin** (`/ticketadmin`): administer user tickets and rewards.

The bots share common helpers, MongoDB access, event handling, and UI components.

> **Shared draft warning:** Message Scheduler drafts are shared across the
> entire Discord server, not separated by user. Only one person should set or
> edit a draft message at a time, or users may overwrite one another's work.

> **TODO — server-specific ticket data:** Ticket balances and the ticket rewards
> shop are currently shared across all Discord servers. They should be redesigned
> so balances and rewards are scoped to an individual server.

## Requirements

- Python 3.10 or newer
- A Discord application and bot token
- A MongoDB connection
- Discord application commands enabled for the bot

The bot uses privileged intents for message content and member events. Enable the required intents in the Discord Developer Portal before running it.

## Setup

From the repository root, create and activate a virtual environment:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

Install the dependencies:

```cmd
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```env
MONGO_ID=mongodb://your-connection-string
TOKEN=your-discord-bot-token
DBNAME=message_scheduler
REDEEM_TARGET=your-redeem-target-id
IS_DEV=True/False
TEST_DISCORD_SERVER=your-development-guild-id
```

`REDEEM_TARGET` is the Discord user ID used by the ticket reward flow. `TEST_DISCORD_SERVER` is used when `IS_DEV=True` to register application commands in one development guild.

When `IS_DEV=True`, slash commands are synchronized only to `TEST_DISCORD_SERVER` and should appear quickly. When `IS_DEV=False`, commands are synchronized globally, which can take longer to propagate through Discord.

## Database Structure

The application uses the MongoDB database named by `DBNAME`. The main collections
and their high-level relationships are:

```text
MongoDB database
└── DBNAME
    ├── messages              one shared draft/temporary document per Discord server
    │   ├── _id               Discord guild/server ID
    │   ├── message           current draft message text
    │   ├── reactions         reaction names or emoji values
    │   └── attachments       source message/channel IDs for attachments
    │
    ├── schedules             scheduled posts for each Discord server
    │   ├── _id               scheduled post ID (ObjectId)
    │   ├── server_id         Discord guild/server ID
    │   ├── channel            destination channel ID
    │   ├── message            message text
    │   ├── time              scheduled date/time
    │   ├── reactions         reactions to add after sending
    │   └── attachments       source message/channel IDs for attachments
    │
    ├── tickets               shared ticket balance and trade state per Discord user
    │   ├── _id               Discord user ID
    │   ├── tickets           current ticket balance
    │   ├── incoming_trades   pending incoming trade data
    │   └── outgoing_trades   pending outgoing trade data
    │
    └── rewards               rewards available in the ticket shop
        ├── _id               reward ID (ObjectId)
        ├── name              display name
        ├── desc              description
        ├── cost              ticket cost
        ├── stock             remaining stock; negative values represent unlimited stock
        ├── image             optional image URL
        └── page_colour       embed colour

Relationships:

```text
Discord guild/server
    ├── messages._id
    └── schedules.server_id

Discord channel
    └── schedules.channel

Discord user
    └── tickets._id

Scheduled post
    └── schedules.attachments -> source Discord message/channel
```

The application accesses these collections through
[`PymongoManager`](<src/managers/pymongo_manager.py>).

## Running

Run the bot directly from the `src` directory:

```cmd
cd src
python bot_main.py
```

For the restart wrapper, which starts the bot again after an unexpected exit:

```cmd
cd src
python main.py
```

To run the tests, navigate to the `root` directory and run:
```cmd
python -m pytest
```

### Install the pre-push test hook

The repository includes a [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
configuration that runs the full pytest suite before `git push`. Each clone
must install the local Git hook:

```cmd
python -m pip install pre-commit
pre-commit install --hook-type pre-push
```

## Project Structure

```text
src/
  bot.py                 Discord bot setup and command synchronization
  bot_main.py            Environment loading and application startup
  main.py                Restart wrapper
  commands/              Bot command groups and implementations
  data/help/             Editable Markdown help content
  helpers/               Shared helpers and bot utilities
  managers/              MongoDB and event management
  ui/                    Shared Discord UI views
```

## Development Notes

- Add or update slash commands in the appropriate command module under `src/commands/`.
- Keep shared behavior in `src/helpers/`, `src/managers/`, or `src/ui/` when it is used by more than one bot.

## Adding Commands

1. Choose the command group that owns the command:
   - Message Scheduler: `src/commands/message_scheduler/message_scheduler.py`
   - Ticket Bot: `src/commands/ticket_bot/ticket_bot.py`
   - Ticket Bot Admin: `src/commands/ticket_bot/admin/ticket_bot_admin.py`
2. Add an `app_commands.command` method to the appropriate `GroupCog`.
3. Add `@enrich_command` and any required `@app_commands.describe` or autocomplete decorators.
4. Put the command logic in a handler method and call that handler from the slash-command method.
5. Add a matching Markdown file under the bot's `src/data/help/<bot>/` directory.

Example:

```python
@app_commands.command(name="status", description="Show the current status")
@enrich_command
async def status(self, interaction: discord.Interaction):
  await self.handle_status(interaction)
```

Add the corresponding help content here:

```text
src/data/help/<bot>/status.md
```

Help files are discovered automatically when the bot starts. `description.md` supplies the help embed description. For **nested commands**, replace spaces with underscores in the filename; for example, `rewards_list.md` becomes the `rewards list` help entry.

Restart the bot after adding the command so the extension is reloaded, then allow Discord commands to synchronize. Development commands sync to `TEST_DISCORD_SERVER`; global commands may take longer to appear.
