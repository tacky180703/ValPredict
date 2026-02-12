import discord
from utils.helpers import (
    get_region,
    get_region_color,
    format_vlr_url,
    get_unix_timestamp,
)


def result_card_embed(match, winner, score1, score2):
    team1 = match.get("team1")
    team2 = match.get("team2")
    event_name = match.get("match_event", "Unknown Event")

    region_label = get_region(event_name)
    color = get_region_color(region_label)

    embed = discord.Embed(
        title=f"🏁  {team1} vs {team2}",
        color=color,
        url=format_vlr_url(match.get("match_page")),
    )
    embed.add_field(name="Event", value=f"🏆 {event_name}", inline=False)
    embed.add_field(name="Winner", value=f"🙌 {winner}", inline=True)
    embed.add_field(name="Score", value=f"📈 {score1} - {score2}", inline=True)
    return embed


class PredictionView(discord.ui.View):
    def __init__(self, team1=None, team2=None, match_url=None):
        super().__init__(timeout=None)
        if team1 and team2:
            self.predict_left.label = f"{team1} WIN"
            self.predict_right.label = f"{team2} WIN"

    @discord.ui.button(style=discord.ButtonStyle.success, custom_id="predict_left")
    async def predict_left(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self._handle_prediction(interaction, side="left")

    @discord.ui.button(style=discord.ButtonStyle.danger, custom_id="predict_right")
    async def predict_right(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self._handle_prediction(interaction, side="right")

    async def _handle_prediction(self, interaction, side):
        from utils.db_manager import save_prediction

        embed = interaction.message.embeds[0]
        footer_text = embed.footer.text
        start_time_timestamp = 0
        try:
            parts = footer_text.split("|")
            id_part = parts[0].replace("ID:", "").strip()
            start_time_timestamp = int(id_part)
        except Exception as e:
            print(f"❌ Error parsing footer: {e} | Content: {footer_text}")

        teams = embed.title.replace("📢  ", "").split(" vs ")
        team1, team2 = teams[0], teams[1]
        match_url = embed.url.replace("https://www.vlr.gg", "")

        my_pick = team1 if side == "left" else team2
        other_team = team2 if side == "left" else team1

        save_prediction(
            interaction.user.id, match_url, my_pick, other_team, start_time_timestamp
        )
        await interaction.response.send_message(
            f"✅ Voted for {my_pick}", ephemeral=True
        )


def match_card_embed(match):
    team1 = match.get("team1")
    team2 = match.get("team2")
    event_name = match.get("match_event", "Unknown Event")
    url = match.get("match_page", "")
    raw_time = match.get("unix_timestamp", "")
    timestamp = get_unix_timestamp(raw_time)

    region_label = get_region(event_name)
    color = get_region_color(region_label)

    embed = discord.Embed(
        title=f"📢  {team1} vs {team2}",
        url=format_vlr_url(match.get("match_page")),
        color=color,
    )
    embed.add_field(name="Event", value=f"🏆 {event_name}", inline=False)
    embed.add_field(name="Starts in", value=f"<t:{timestamp}:R>", inline=True)
    embed.set_footer(text=f"ID: {timestamp} | Predict Now!")

    return embed
