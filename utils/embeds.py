import discord
from utils.helpers import get_region, get_region_color


def result_card_embed(match, winner, score1, score2):
    team1 = match.get("team1")
    team2 = match.get("team2")
    event_name = match.get("match_event", "Unknown Event")
    url = match.get("match_page", "")

    region_label = get_region(event_name)
    color = get_region_color(region_label)

    embed = discord.Embed(
        title=f"🏁  {team1} vs {team2}",
        color=color,
        url=f"https://www.vlr.gg{url}" if not url.startswith("http") else url,
    )
    embed.add_field(name="Event", value=f"🏆 {event_name}", inline=False)
    embed.add_field(name="Winner", value=f"🙌 {winner}", inline=True)
    embed.add_field(name="Score", value=f"📈 {score1} - {score2}", inline=True)
    return embed


def match_card_embed(match):
    team1 = match.get("team1")
    team2 = match.get("team2")
    event_name = match.get("match_event", "Unknown Event")
    url = match.get("match_page", "")
    time = match.get("time_until_match", "Upcoming")

    region_label = get_region(event_name)
    color = get_region_color(region_label)

    full_url = f"https://www.vlr.gg{url}" if not url.startswith("http") else url

    embed = discord.Embed(
        title=f"📢  {team1} vs {team2}",
        url=full_url,
        color=color,
    )
    embed.add_field(name="Event", value=f"🏆 {event_name}", inline=False)
    embed.add_field(name="Starts in", value=f"⏳ {time}", inline=True)
    embed.set_footer(
        text="Predict Now! | Click the buttons below to lock in your pick."
    )

    return embed
