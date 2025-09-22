import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
from typing import Optional
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SummariserBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

bot = SummariserBot()

@bot.tree.command(name="summarise", description="Summarise recent messages in the current channel")
@app_commands.describe(
    messages="Number of messages to summarise (default: 10, max: 100)"
)
async def summarise(interaction: discord.Interaction, messages: Optional[int] = 10):
    await interaction.response.defer()

    # Validate message count
    if messages < 1:
        messages = 1
    elif messages > 100:
        messages = 100

    try:
        # Fetch messages from the channel
        channel_messages = []
        all_messages = []

        async for message in interaction.channel.history(limit=messages):
            all_messages.append(message)
            if not message.author.bot:  # Skip bot messages
                channel_messages.append(f"{message.author.display_name}: {message.content}")

        if not channel_messages:
            if len(all_messages) == 0:
                await interaction.followup.send("No messages found in this channel.")
            else:
                await interaction.followup.send(f"No user messages found to summarise. Found {len(all_messages)} bot messages.")
            return

        # Reverse to get chronological order
        channel_messages.reverse()

        # Create the prompt for Gemini
        messages_text = "\n".join(channel_messages)
        prompt = f"""Please provide a concise summary of the following Discord chat conversation. Focus on the main topics discussed, key points made, and any important decisions or conclusions reached:

{messages_text}

Summary:"""

        # Generate summary using Gemini
        response = bot.model.generate_content(prompt)
        summary = response.text

        # Create embed for the response
        embed = discord.Embed(
            title=f"📝 Chat Summary ({len(channel_messages)} messages)",
            description=summary,
            color=0x00ff00
        )
        embed.set_footer(text="Powered by Google Gemini")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred while generating the summary: {str(e)}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not found!")
    elif not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY environment variable not found!")
    else:
        bot.run(token)