import discord


def result_card_embed(team1, team2, winner, score1, score2, url, event_name):
    embed = discord.Embed(
        title=f"**{team1}** vs **{team2}**",
        description=f"**{event_name}**",
        color=discord.Color.gold(),
        url=f"https://www.vlr.gg{url}",
    )
    embed.add_field(name="🏆勝者", value=f" **{winner}**", inline=True)
    embed.add_field(name="スコア", value=f"**{score1} - {score2}**", inline=True)
    return embed
