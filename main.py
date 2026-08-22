import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = False

    @discord.ui.button(label="نعم، امسح كل شي", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.edit_message(content="🔥 جاري المسح... لا تطلع من السيرفر", view=None)

    @discord.ui.button(label="إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="تم الإلغاء.", view=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"البوت شغال باسم: {bot.user}")

@bot.tree.command(name="مسح_السيرفر", description="يحذف كل الرومات والرتب مرة وحدة")
async def مسح_السيرفر(interaction: discord.Interaction):
    # حماية: فقط مالك السيرفر
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ هذا الأمر فقط لمالك السيرفر.", ephemeral=True)
        return
    
    if not interaction.guild.me.guild_permissions.administrator:
        await interaction.response.send_message("❌ لازم تعطيني صلاحية Administrator أول.", ephemeral=True)
        return

    view = ConfirmView()
    await interaction.response.send_message("⚠️ **تحذير أخير:** رح يتم حذف كل الرومات والرتب ولن تقدر ترجعها.\nمتأكد؟", view=view, ephemeral=True)
    await view.wait()

    if not view.value:
        return

    guild = interaction.guild
    current_channel = interaction.channel

    # 1. حذف الرتب أولاً
    for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
        try:
            if role.is_default(): # @everyone ما ينحذف
                continue
            if role.managed: # رتب البوتات
                continue
            if role >= guild.me.top_role: # أعلى مني ما اقدر احذفه
                continue
            await role.delete(reason=f"مسح شامل بواسطة {interaction.user}")
            await asyncio.sleep(0.4) # عشان ما يبلّعنا ريت ليميت
        except:
            pass

    # 2. حذف الرومات - نخلي روم الأمر للآخر
    other_channels = [c for c in guild.channels if c.id != current_channel.id]
    for channel in other_channels:
        try:
            await channel.delete(reason="تغيير ستايل السيرفر")
            await asyncio.sleep(0.4)
        except:
            pass
    
    # أخيرا نحذف نفس الروم اللي انكتب فيه الأمر
    try:
        await current_channel.delete(reason="تغيير ستايل السيرفر")
    except:
        pass

# التشغيل عبر التوكن المسجل في Environment Variables على Render
bot.run(os.getenv("DISCORD_TOKEN"))
