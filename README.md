# Discord Summariser Bot

A Discord bot that summarises chat conversations using Google's Gemini AI.

## Features

- `/summarise` slash command to summarise recent messages
- Optional parameter to specify number of messages (1-100, default: 10)
- Uses Google Gemini for intelligent summarisation
- Ignores bot messages for cleaner summaries

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Fill in your API keys in `.env`:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `GEMINI_API_KEY`: Your Google Gemini API key

4. Run the bot:
   ```bash
   python main.py
   ```

## Getting API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

## Usage

Once the bot is running and added to your server:
- Use `/summarise` to get a summary of the last 10 messages
- Use `/summarise messages:20` to summarise the last 20 messages (max 100)