import aiohttp
import discord
import requests
import asyncio 

# Bot initialization
intents = discord.Intents.default()
intents.messages = True
bot = discord.Client(intents=intents)

# Function to check for new scores
async def check_new_scores():
    last_score_id = None
    url = f"https://osu.ppy.sh/api/get_user_recent?k={OSU_API_KEY}&u={OSU_USER_ID}"

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        scores = await response.json()
                        if scores:
                            latest_score = scores[0]

                            # Check if this is a new score
                            if latest_score["score_id"] != last_score_id:
                                last_score_id = latest_score["score_id"]
                                map_name = latest_score["beatmap_id"]
                                score = latest_score["score"]

                                total_hits = (
                                    int(latest_score["count300"])
                                    + int(latest_score["count100"])
                                    + int(latest_score["count50"])
                                    + int(latest_score["countmiss"])
                                )

                                # Calculate accuracy
                                accuracy = (
                                    (
                                        int(latest_score["count300"]) * 300
                                        + int(latest_score["count100"]) * 100
                                        + int(latest_score["count50"]) * 50
                                    )
                                    / (total_hits * 300)
                                    if total_hits > 0
                                    else 0
                                )

                                combo = latest_score["maxcombo"]

                                # Format the message
                                message = (
                                    f"New score submitted by user:\n"
                                    f"**Map ID**: {map_name}\n"
                                    f"**Score**: {score}\n"
                                    f"**Accuracy**: {accuracy*100:.2f}%\n"
                                    f"**Max Combo**: {combo}x"
                                )

                                # Send the message to the Discord channel
                                channel = bot.get_channel(CHANNEL_ID)
                                if channel:
                                    await channel.send(message)
                                else:
                                    print(f"Failed to find channel with ID: {CHANNEL_ID}")
                    else:
                        print(f"Failed to fetch scores: {response.status} {await response.text()}")

            except Exception as e:
                print(f"Error in check_new_scores: {e}")

            await asyncio.sleep(60)  # Check every 60 seconds


# Bot event for when it's ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(check_new_scores())


# Run the bot
bot.run(DISCORD_TOKEN)