from interactions import (
    Client,
    Intents,
    listen,
    slash_command,
    SlashContext,
    OptionType,
    slash_option,
    Status,
    Activity
)
from interactions.api.events import VoiceUserJoin, VoiceUserLeave
import os
from dotenv import load_dotenv

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Hole den Token aus der Umgebungsvariablen
TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))

bot = Client(intents=Intents.DEFAULT | Intents.GUILD_VOICE_STATES)

create_channel_id = None
voice_channels = []


@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    await bot.change_presence(
        status=Status.ONLINE,
        activity=Activity(
            name="🔊 Voice Channels",
            type=2,
        )
    )


@slash_command(
    name="create_voice",
    description="Create a voice channel to create voice channels",
)
@slash_option(
    name="category_id",
    description="Die ID der Kategorie, in der der Voice-Channel erstellt werden soll",  # noqa
    opt_type=OptionType.STRING,
    required=True,
)
async def create_voice_channel(ctx: SlashContext, category_id: str):
    guild = ctx.guild

    selected_category = guild.get_channel(category_id)

    voice_channel = await guild.create_channel(
        name="➕ Create Voice 🔊",
        channel_type=2,
        category=selected_category,
    )
    await ctx.respond(f"Der Voice-Channel wurde in der Kategorie '{selected_category.name}' erstellt!", ephemeral=True)    # noqa
    global create_channel_id
    create_channel_id = str(voice_channel.id)


@listen(VoiceUserJoin)
async def voice_join(event: VoiceUserJoin):
    channel_id = str(event.channel.id)
    if channel_id != create_channel_id:
        return
    author = event.author
    guild = event.channel.guild
    voice_channel = await guild.create_channel(
        name=f"{author.display_name} Voice",
        channel_type=2,
        category=event.channel.category,
    )
    voice_channels.append(
        {
            "username": event.author.username,
            "channel_id": voice_channel.id,
        }
    )
    await author.move(voice_channel.id)


@listen(VoiceUserLeave)
async def voice_leave(event: VoiceUserLeave):
    author = event.author
    guild = event.channel.guild

    for channel in voice_channels:
        if channel["username"] == author.username:
            channel_id = channel["channel_id"]
            voice_channel = guild.get_channel(channel_id)
            if voice_channel:
                await voice_channel.delete()
            voice_channels.remove(channel)
            break


bot.start(TOKEN)
