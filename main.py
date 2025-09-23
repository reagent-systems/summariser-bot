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

class ShareSummaryView(discord.ui.View):
    def __init__(self, summary_embed: discord.Embed, channel: discord.TextChannel):
        super().__init__(timeout=300)  # 5 minute timeout
        self.summary_embed = summary_embed
        self.channel = channel

    @discord.ui.button(label='Share to Channel', style=discord.ButtonStyle.primary, emoji='📤')
    async def share_summary(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Send the summary to the original channel
            await self.channel.send(embed=self.summary_embed)

            # Update the private message to show it was shared
            embed = discord.Embed(
                title="✅ Summary Shared!",
                description="Your summary has been posted to the channel.",
                color=0x00ff00
            )

            # Disable the button
            button.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to share summary: {str(e)}", ephemeral=True)

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
    await interaction.response.defer(ephemeral=True)

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
        embed.set_footer(text=f"Powered by Google Gemini • Summarised by {interaction.user.display_name}")

        # Create the view with the share button
        view = ShareSummaryView(embed, interaction.channel)

        # Send the summary privately (ephemeral)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred while generating the summary: {str(e)}", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not found!")
    elif not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY environment variable not found!")
    else:
        bot.run(token)