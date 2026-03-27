import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

# Токен берется ТОЛЬКО из переменной окружения
TOKEN = os.getenv('x_2SJSBreKj2TEprvEgr1G9Jy-wx7q9B')

# Проверка наличия токена
if not TOKEN:
    raise ValueError("❌ Токен не найден! Установите переменную DISCORD_TOKEN")

# Настройки
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Файл для предупреждений
WARNS_FILE = 'warns.json'

def load_warns():
    """Загружает предупреждения из файла"""
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warns(warns):
    """Сохраняет предупреждения в файл"""
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(warns, f, indent=4, ensure_ascii=False)

# ========== ЗАПУСК БОТА ==========
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📅 Серверов: {len(bot.guilds)}')
    await bot.change_presence(activity=discord.Game(name="!бан | !мут | !пред"))

# ========== КОМАНДА БАН ==========
@bot.command()
@commands.has_permissions(ban_members=True)
async def бан(ctx, member: discord.Member, *, reason="Причина не указана"):
    """Банит участника и отправляет причину в ЛС"""
    try:
        embed = discord.Embed(
            title="🔨 ВЫ ЗАБАНЕНЫ",
            description=f"Вы были забанены на сервере **{ctx.guild.name}**",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📋 Причина", value=reason, inline=False)
        embed.add_field(name="👮 Модератор", value=ctx.author.name, inline=False)
        await member.send(embed=embed)
    except:
        pass
    
    await member.ban(reason=reason)
    
    embed = discord.Embed(
        title="🔨 БАН",
        description=f"{member.mention} был забанен",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📋 Причина", value=reason, inline=False)
    embed.add_field(name="👮 Модератор", value=ctx.author.mention, inline=False)
    await ctx.send(embed=embed)

# ========== КОМАНДА МУТ ==========
@bot.command()
@commands.has_permissions(moderate_members=True)
async def мут(ctx, member: discord.Member, minutes: int = 10, *, reason="Причина не указана"):
    """Мутит участника на определенное количество минут"""
    try:
        embed = discord.Embed(
            title="🔇 ВЫ ПОЛУЧИЛИ МУТ",
            description=f"Вы были замучены на сервере **{ctx.guild.name}**",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="⏱️ Длительность", value=f"{minutes} минут", inline=False)
        embed.add_field(name="📋 Причина", value=reason, inline=False)
        embed.add_field(name="👮 Модератор", value=ctx.author.name, inline=False)
        await member.send(embed=embed)
    except:
        pass
    
    timeout_until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(timeout_until, reason=reason)
    
    embed = discord.Embed(
        title="🔇 МУТ",
        description=f"{member.mention} получил мут на {minutes} минут",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📋 Причина", value=reason, inline=False)
    embed.add_field(name="👮 Модератор", value=ctx.author.mention, inline=False)
    await ctx.send(embed=embed)

# ========== КОМАНДА ПРЕДУПРЕЖДЕНИЕ ==========
@bot.command()
@commands.has_permissions(kick_members=True)
async def пред(ctx, member: discord.Member, *, reason="Причина не указана"):
    """Выдает предупреждение участнику и отправляет в ЛС"""
    warns = load_warns()
    user_id = str(member.id)
    
    if user_id not in warns:
        warns[user_id] = []
    
    warn_data = {
        "reason": reason,
        "moderator": ctx.author.name,
        "date": str(datetime.now())
    }
    warns[user_id].append(warn_data)
    save_warns(warns)
    
    try:
        embed = discord.Embed(
            title="⚠️ ВЫ ПОЛУЧИЛИ ПРЕДУПРЕЖДЕНИЕ",
            description=f"На сервере **{ctx.guild.name}**",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📋 Причина", value=reason, inline=False)
        embed.add_field(name="👮 Модератор", value=ctx.author.name, inline=False)
        embed.add_field(name="📊 Всего предупреждений", value=str(len(warns[user_id])), inline=False)
        await member.send(embed=embed)
    except:
        pass
    
    embed = discord.Embed(
        title="⚠️ ПРЕДУПРЕЖДЕНИЕ",
        description=f"{member.mention} получил предупреждение",
        color=discord.Color.yellow(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📋 Причина", value=reason, inline=False)
    embed.add_field(name="👮 Модератор", value=ctx.author.mention, inline=False)
    embed.add_field(name="📊 Всего предупреждений", value=str(len(warns[user_id])), inline=False)
    await ctx.send(embed=embed)

# ========== КОМАНДА ПРОСМОТР ПРЕДУПРЕЖДЕНИЙ ==========
@bot.command()
@commands.has_permissions(kick_members=True)
async def преды(ctx, member: discord.Member):
    """Показывает все предупреждения участника"""
    warns = load_warns()
    user_id = str(member.id)
    
    if user_id not in warns or not warns[user_id]:
        await ctx.send(f"✅ У {member.mention} нет предупреждений")
        return
    
    embed = discord.Embed(
        title=f"⚠️ Предупреждения {member.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    for i, warn in enumerate(warns[user_id][-5:], 1):
        embed.add_field(
            name=f"#{len(warns[user_id]) - i + 1} - {warn['date'][:16]}",
            value=f"📋 Причина: {warn['reason']}\n👮 Модератор: {warn['moderator']}",
            inline=False
        )
    
    embed.set_footer(text=f"Всего: {len(warns[user_id])} предупреждений")
    await ctx.send(embed=embed)

# ========== КОМАНДА РАЗМУТ ==========
@bot.command()
@commands.has_permissions(moderate_members=True)
async def размут(ctx, member: discord.Member):
    """Снимает мут с участника"""
    await member.timeout(None)
    await ctx.send(f"✅ {member.mention} размучен")

# ========== КОМАНДА АНБАН ==========
@bot.command()
@commands.has_permissions(ban_members=True)
async def анбан(ctx, *, member_name):
    """Разбанивает участника по имени"""
    banned_users = [entry async for entry in ctx.guild.bans()]
    
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name.lower() == member_name.lower():
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} разбанен")
            return
    
    await ctx.send("❌ Пользователь не найден в банах")

# ========== КОМАНДА КИК ==========
@bot.command()
@commands.has_permissions(kick_members=True)
async def кик(ctx, member: discord.Member, *, reason="Причина не указана"):
    """Кикает участника и отправляет причину в ЛС"""
    try:
        embed = discord.Embed(
            title="👢 ВАС КИКНУЛИ",
            description=f"Вы были кикнуты с сервера **{ctx.guild.name}**",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📋 Причина", value=reason, inline=False)
        embed.add_field(name="👮 Модератор", value=ctx.author.name, inline=False)
        await member.send(embed=embed)
    except:
        pass
    
    await member.kick(reason=reason)
    
    embed = discord.Embed(
        title="👢 КИК",
        description=f"{member.mention} был кикнут",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📋 Причина", value=reason, inline=False)
    embed.add_field(name="👮 Модератор", value=ctx.author.mention, inline=False)
    await ctx.send(embed=embed)

# ========== КОМАНДА ОЧИСТИТЬ ==========
@bot.command()
@commands.has_permissions(manage_messages=True)
async def очистить(ctx, amount: int = 10):
    """Очищает указанное количество сообщений"""
    if amount > 100:
        await ctx.send("❌ Нельзя удалить больше 100 сообщений за раз!")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Удалено {len(deleted) - 1} сообщений", delete_after=3)

# ========== ОБРАБОТКА ОШИБОК ==========
@бан.error
@мут.error
@пред.error
@преды.error
@размут.error
@анбан.error
@кик.error
@очистить.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас нет прав для использования этой команды!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Участник не найден!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Не хватает аргументов! Используйте: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    else:
        await ctx.send(f"❌ Ошибка: {error}")
        print(error)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    bot.run(TOKEN)
