"""
SANTACHO FC V6 — RAILWAY 24/7
===================================

Esta versión:
- RENOMBRA la estructura vieja de Santacho FC al nuevo estilo.
- NO duplica categorías/canales/roles si ya existen.
- Mantiene reclutamiento, tickets, selector de posiciones y slash commands.
- Usa tipografía Unicode decorativa en categorías, canales y roles.

Requiere:
    discord.py>=2.6,<3.0
"""

import os
import re
import asyncio
import json
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# ESTILO / BRANDING
# =========================================================

SERVER_NAME = "🟡⚫ 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂"
GOLD = 0xD4AF37

# ----- Categorías bonitas -----
CAT_INFO = "━━ 📌・𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐂𝐈Ó𝐍 ━━"
CAT_CLUB = "━━ 🏟️・𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂 ━━"
CAT_COMP = "━━ ⚽・𝐂𝐎𝐌𝐏𝐄𝐓𝐈𝐂𝐈Ó𝐍 ━━"
CAT_LOCKER = "━━ 🧠・𝐕𝐄𝐒𝐓𝐔𝐀𝐑𝐈𝐎 ━━"
CAT_SCOUT = "━━ 🔍・𝐒𝐂𝐎𝐔𝐓𝐈𝐍𝐆 ━━"
CAT_TRYOUT = "━━ 🧪・𝐏𝐑𝐔𝐄𝐁𝐀𝐒 𝐏𝐑𝐈𝐕𝐀𝐃𝐀𝐒 ━━"
CAT_TV = "━━ 🎥・𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐓𝐕 ━━"
CAT_VOICE = "━━ 🎙️・𝐂𝐀𝐍𝐀𝐋𝐄𝐒 𝐃𝐄 𝐕𝐎𝐙 ━━"
CAT_BOTS = "━━ 🤖・𝐁𝐎𝐓𝐒 ━━"
CAT_ROSTER = "━━ 👥・𝐏𝐋𝐀𝐍𝐓𝐈𝐋𝐋𝐀 ━━"
CAT_STAFF = "━━ 👑・𝐃𝐈𝐑𝐄𝐂𝐓𝐈𝐕𝐀 ━━"

# ----- Roles bonitos -----
ROLE_PRESIDENT = "👑・𝐏𝐑𝐄𝐒𝐈𝐃𝐄𝐍𝐓𝐄"
ROLE_BOARD = "🛡️・𝐃𝐈𝐑𝐄𝐂𝐓𝐈𝐕𝐀"
ROLE_DT = "🎩・𝐃𝐓"
ROLE_CAPTAIN = "🧠・𝐂𝐀𝐏𝐈𝐓Á𝐍"
ROLE_STARTER = "⭐・𝐓𝐈𝐓𝐔𝐋𝐀𝐑"
ROLE_ROSTER = "🔄・𝐏𝐋𝐀𝐍𝐓𝐈𝐋𝐋𝐀"
ROLE_TRIAL = "🧪・𝐀 𝐏𝐑𝐔𝐄𝐁𝐀"
ROLE_CREATOR = "🎥・𝐂𝐑𝐄𝐀𝐃𝐎𝐑"
ROLE_BOTS = "🤖・𝐁𝐎𝐓𝐒"
ROLE_GUEST = "🤝・𝐈𝐍𝐕𝐈𝐓𝐀𝐃𝐎"
ROLE_COMMUNITY = "👥・𝐂𝐎𝐌𝐔𝐍𝐈𝐃𝐀𝐃"

LEADERSHIP_ROLES = {ROLE_PRESIDENT, ROLE_BOARD, ROLE_DT, ROLE_CAPTAIN}
STAFF_ROLES = {ROLE_PRESIDENT, ROLE_BOARD, ROLE_DT}

POSITION_ROLES = {
    "PO": "🧤・𝐏𝐎",
    "DFC": "🛡️・𝐃𝐅𝐂",
    "LD": "🏃・𝐋𝐃",
    "LI": "🏃・𝐋𝐈",
    "MCD": "⚙️・𝐌𝐂𝐃",
    "MC": "🎛️・𝐌𝐂",
    "MCO": "🎨・𝐌𝐂𝐎",
    "MD": "⚡・𝐌𝐃",
    "MI": "⚡・𝐌𝐈",
    "DC": "🎯・𝐃𝐂",
}

BASE_ROLES = [
    (ROLE_PRESIDENT, 0xFFD700, True),
    (ROLE_BOARD, 0xC99A00, True),
    (ROLE_DT, 0xE5B80B, True),
    (ROLE_CAPTAIN, 0xF2F2F2, True),
    (ROLE_STARTER, 0xE8C547, True),
    (ROLE_ROSTER, 0xB8B8B8, True),
    (ROLE_TRIAL, 0x777777, False),
    (ROLE_CREATOR, 0xA970FF, False),
    (ROLE_BOTS, 0x949BA4, True),
    (ROLE_GUEST, 0x8A8A8A, False),
    (ROLE_COMMUNITY, 0xD0D0D0, False),
]

# =========================================================
# NOMBRES DE CANALES
# =========================================================

CH_WELCOME = "👋・𝒃𝒊𝒆𝒏𝒗𝒆𝒏𝒊𝒅𝒂"
CH_RULES = "📜・𝒓𝒆𝒈𝒍𝒂𝒔"
CH_ANNOUNCE = "📢・𝒂𝒏𝒖𝒏𝒄𝒊𝒐𝒔"
CH_TROPHIES = "🏆・𝒑𝒂𝒍𝒎𝒂𝒓𝒆́𝒔"
CH_JOIN = "🎮・𝒄𝒐́𝒎𝒐-𝒖𝒏𝒊𝒓𝒔𝒆"
CH_SOCIALS = "🌐・𝒓𝒆𝒅𝒆𝒔-𝒔𝒐𝒄𝒊𝒂𝒍𝒆𝒔"

CH_GENERAL = "💬・𝒍𝒂-𝒄𝒂𝒏𝒄𝒉𝒂"
CH_MEDIA = "📸・𝒔𝒂𝒏𝒕𝒂𝒄𝒉𝒐-𝒎𝒆𝒅𝒊𝒂"
CH_MEMES = "😂・𝒎𝒆𝒎𝒆𝒔"
CH_FOOTBALL = "⚽・𝒇𝒖́𝒕𝒃𝒐𝒍"
CH_FC = "🎮・𝒇𝒄𝟐𝟕"
CH_POSITIONS = "🎯・𝒆𝒍𝒊𝒈𝒆-𝒕𝒖-𝒑𝒐𝒔𝒊𝒄𝒊𝒐́𝒏"
CH_SUGGEST = "💡・𝒔𝒖𝒈𝒆𝒓𝒆𝒏𝒄𝒊𝒂𝒔"

CH_CALENDAR = "📅・𝒄𝒂𝒍𝒆𝒏𝒅𝒂𝒓𝒊𝒐"
CH_CALLED = "✅・𝒄𝒐𝒏𝒗𝒐𝒄𝒂𝒅𝒐𝒔"
CH_LINEUPS = "📋・𝒂𝒍𝒊𝒏𝒆𝒂𝒄𝒊𝒐𝒏𝒆𝒔"
CH_RESULTS = "🎯・𝒓𝒆𝒔𝒖𝒍𝒕𝒂𝒅𝒐𝒔"
CH_STATS = "📊・𝒆𝒔𝒕𝒂𝒅𝒊́𝒔𝒕𝒊𝒄𝒂𝒔"
CH_HIGHLIGHTS = "🎥・𝒉𝒊𝒈𝒉𝒍𝒊𝒈𝒉𝒕𝒔"
CH_TABLE = "🏆・𝒕𝒂𝒃𝒍𝒂-𝒅𝒆-𝒑𝒐𝒔𝒊𝒄𝒊𝒐𝒏𝒆𝒔"

CH_LOCKER = "🚪・𝒗𝒆𝒔𝒕𝒖𝒂𝒓𝒊𝒐"
CH_TACTICS = "🧠・𝒑𝒊𝒛𝒂𝒓𝒓𝒂-𝒅𝒆𝒍-𝒅𝒕"
CH_AVAIL = "📋・𝒅𝒊𝒔𝒑𝒐𝒏𝒊𝒃𝒊𝒍𝒊𝒅𝒂𝒅"
CH_ABSENCE = "⚠️・𝒂𝒖𝒔𝒆𝒏𝒄𝒊𝒂𝒔"
CH_OBJECTIVES = "🎯・𝒐𝒃𝒋𝒆𝒕𝒊𝒗𝒐𝒔"
CH_ANALYSIS = "🎬・𝒂𝒏𝒂́𝒍𝒊𝒔𝒊𝒔-𝒅𝒆-𝒑𝒂𝒓𝒕𝒊𝒅𝒐𝒔"

CH_TRY = "📝・𝒒𝒖𝒊𝒆𝒓𝒐-𝒑𝒓𝒐𝒃𝒂𝒓"
CH_RECRUIT = "🔎・𝒃𝒖𝒔𝒄𝒂𝒎𝒐𝒔-𝒋𝒖𝒈𝒂𝒅𝒐𝒓𝒆𝒔"
CH_ACCEPTED = "✅・𝒑𝒓𝒖𝒆𝒃𝒂𝒔-𝒂𝒄𝒆𝒑𝒕𝒂𝒅𝒂𝒔"

CH_SCREEN = "📸・𝒔𝒄𝒓𝒆𝒆𝒏𝒔𝒉𝒐𝒕𝒔"
CH_CLIPS = "🎬・𝒄𝒍𝒊𝒑𝒔"
CH_TIKTOK = "📱・𝒕𝒊𝒌𝒕𝒐𝒌"
CH_STREAMS = "🔴・𝒔𝒕𝒓𝒆𝒂𝒎𝒔"
CH_DESIGNS = "🎨・𝒅𝒊𝒔𝒆𝒏̃𝒐𝒔"
CH_POTW = "🔥・𝒋𝒖𝒈𝒂𝒅𝒂-𝒅𝒆-𝒍𝒂-𝒔𝒆𝒎𝒂𝒏𝒂"

CH_BOARD = "👑・𝒅𝒊𝒓𝒆𝒄𝒕𝒊𝒗𝒂"
CH_STAFF = "📝・𝒔𝒕𝒂𝒇𝒇-𝒄𝒉𝒂𝒕"
CH_DECISIONS = "📋・𝒅𝒆𝒄𝒊𝒔𝒊𝒐𝒏𝒆𝒔"
CH_REPORTS = "🚨・𝒓𝒆𝒑𝒐𝒓𝒕𝒆𝒔"
CH_SCOUT_STAFF = "🔍・𝒔𝒄𝒐𝒖𝒕𝒊𝒏𝒈-𝒔𝒕𝒂𝒇𝒇"
CH_ADMIN = "⚙️・𝒂𝒅𝒎𝒊𝒏𝒊𝒔𝒕𝒓𝒂𝒄𝒊𝒐́𝒏"

CH_BOT_COMMANDS = "🤖・𝒄𝒐𝒎𝒂𝒏𝒅𝒐𝒔-𝒃𝒐𝒕"
CH_BOT_EVENTS = "📅・𝒆𝒗𝒆𝒏𝒕𝒐𝒔-𝒃𝒐𝒕"
CH_BOT_STATS = "📊・𝒔𝒕𝒂𝒕𝒔-𝒃𝒐𝒕"

CH_ROSTER = "👥・𝒑𝒍𝒂𝒏𝒕𝒊𝒍𝒍𝒂-𝒐𝒇𝒊𝒄𝒊𝒂𝒍"
CH_PLAYER_STATS = "📊・𝒆𝒔𝒕𝒂𝒅𝒊́𝒔𝒕𝒊𝒄𝒂𝒔-𝒋𝒖𝒈𝒂𝒅𝒐𝒓𝒆𝒔"
CH_MVP = "⭐・𝒎𝒗𝒑"
CH_BOT_DATA = "🗄️・𝒅𝒂𝒕𝒐𝒔-𝒅𝒆𝒍-𝒃𝒐𝒕"

VOICE_LOBBY = "🏟️・𝐋𝐨𝐛𝐛𝐲 𝐒𝐚𝐧𝐭𝐚𝐜𝐡𝐨"
VOICE_LOCKER = "⚽・𝐕𝐞𝐬𝐭𝐮𝐚𝐫𝐢𝐨"
VOICE_MATCH = "🎮・𝐏𝐚𝐫𝐭𝐢𝐝𝐨 𝐎𝐟𝐢𝐜𝐢𝐚𝐥"
VOICE_FRIENDLY = "🔥・𝐀𝐦𝐢𝐬𝐭𝐨𝐬𝐨𝐬"
VOICE_TRAIN = "🏋️・𝐄𝐧𝐭𝐫𝐞𝐧𝐚𝐦𝐢𝐞𝐧𝐭𝐨"
VOICE_DT = "🧠・𝐒𝐚𝐥𝐚 𝐝𝐞𝐥 𝐃𝐓"
VOICE_CHILL = "🎵・𝐂𝐡𝐢𝐥𝐥"

CATEGORY_BLUEPRINT = [
    (CAT_INFO, [
        ("text", CH_WELCOME), ("text", CH_RULES), ("text", CH_ANNOUNCE),
        ("text", CH_TROPHIES), ("text", CH_JOIN), ("text", CH_SOCIALS),
    ]),
    (CAT_CLUB, [
        ("text", CH_GENERAL), ("text", CH_MEDIA), ("text", CH_MEMES),
        ("text", CH_FOOTBALL), ("text", CH_FC), ("text", CH_POSITIONS),
        ("text", CH_SUGGEST),
    ]),
    (CAT_COMP, [
        ("text", CH_CALENDAR), ("text", CH_CALLED), ("text", CH_LINEUPS),
        ("text", CH_RESULTS), ("text", CH_STATS), ("text", CH_HIGHLIGHTS),
        ("text", CH_TABLE),
    ]),
    (CAT_LOCKER, [
        ("text", CH_LOCKER), ("text", CH_TACTICS), ("text", CH_AVAIL),
        ("text", CH_ABSENCE), ("text", CH_OBJECTIVES), ("text", CH_ANALYSIS),
    ]),
    (CAT_SCOUT, [
        ("text", CH_TRY), ("text", CH_RECRUIT), ("text", CH_ACCEPTED),
    ]),
    (CAT_TRYOUT, []),
    (CAT_TV, [
        ("text", CH_SCREEN), ("text", CH_CLIPS), ("text", CH_TIKTOK),
        ("text", CH_STREAMS), ("text", CH_DESIGNS), ("text", CH_POTW),
    ]),
    (CAT_VOICE, [
        ("voice", VOICE_LOBBY), ("voice", VOICE_LOCKER), ("voice", VOICE_MATCH),
        ("voice", VOICE_FRIENDLY), ("voice", VOICE_TRAIN), ("voice", VOICE_DT),
        ("voice", VOICE_CHILL),
    ]),
    (CAT_BOTS, [
        ("text", CH_BOT_COMMANDS),
        ("text", CH_BOT_EVENTS),
        ("text", CH_BOT_STATS),
    ]),
    (CAT_ROSTER, [
        ("text", CH_ROSTER),
        ("text", CH_PLAYER_STATS),
        ("text", CH_MVP),
    ]),
    (CAT_STAFF, [
        ("text", CH_BOT_DATA),
        ("text", CH_BOARD), ("text", CH_STAFF), ("text", CH_DECISIONS),
        ("text", CH_REPORTS), ("text", CH_SCOUT_STAFF), ("text", CH_ADMIN),
    ]),
]


# =========================================================
# MIGRACIÓN DE LOS NOMBRES V2 -> V3
# =========================================================

CATEGORY_RENAMES = {
    "📌・INFORMACIÓN": CAT_INFO,
    "🏟️・SANTACHO FC": CAT_CLUB,
    "⚽・COMPETICIÓN": CAT_COMP,
    "🧠・VESTUARIO": CAT_LOCKER,
    "🔍・SCOUTING": CAT_SCOUT,
    "🧪・PRUEBAS PRIVADAS": CAT_TRYOUT,
    "🎥・SANTACHO TV": CAT_TV,
    "🎙️・VOZ": CAT_VOICE,
    "👑・DIRECTIVA": CAT_STAFF,
}

CHANNEL_RENAMES = {
    "👋・bienvenida": CH_WELCOME,
    "📜・reglas": CH_RULES,
    "📢・anuncios": CH_ANNOUNCE,
    "🏆・palmares": CH_TROPHIES,
    "🎮・como-unirse": CH_JOIN,
    "🌐・redes-sociales": CH_SOCIALS,

    "💬・la-cancha": CH_GENERAL,
    "📸・santacho-media": CH_MEDIA,
    "😂・memes": CH_MEMES,
    "⚽・futbol": CH_FOOTBALL,
    "🎮・fc27": CH_FC,
    "🎯・elige-tu-posicion": CH_POSITIONS,
    "💡・sugerencias": CH_SUGGEST,

    "📅・calendario": CH_CALENDAR,
    "✅・convocados": CH_CALLED,
    "📋・alineaciones": CH_LINEUPS,
    "🎯・resultados": CH_RESULTS,
    "📊・estadisticas": CH_STATS,
    "🎥・highlights": CH_HIGHLIGHTS,
    "🏆・tabla-de-posiciones": CH_TABLE,

    "🚪・vestuario": CH_LOCKER,
    "🧠・pizarra-del-dt": CH_TACTICS,
    "📋・disponibilidad": CH_AVAIL,
    "⚠️・ausencias": CH_ABSENCE,
    "🎯・objetivos": CH_OBJECTIVES,
    "🎬・analisis-de-partidos": CH_ANALYSIS,

    "📝・quiero-probar": CH_TRY,
    "🔎・buscamos-jugadores": CH_RECRUIT,
    "✅・pruebas-aceptadas": CH_ACCEPTED,

    "📸・screenshots": CH_SCREEN,
    "🎬・clips": CH_CLIPS,
    "📱・tiktok": CH_TIKTOK,
    "🔴・streams": CH_STREAMS,
    "🎨・diseños": CH_DESIGNS,
    "🔥・jugada-de-la-semana": CH_POTW,

    "👑・directiva": CH_BOARD,
    "📝・staff-chat": CH_STAFF,
    "📋・decisiones": CH_DECISIONS,
    "🚨・reportes": CH_REPORTS,
    "🔍・scouting-staff": CH_SCOUT_STAFF,
    "⚙️・administracion": CH_ADMIN,

    "🏟️・Lobby Santacho": VOICE_LOBBY,
    "⚽・Vestuario": VOICE_LOCKER,
    "🎮・Partido Oficial": VOICE_MATCH,
    "🔥・Amistosos": VOICE_FRIENDLY,
    "🏋️・Entrenamiento": VOICE_TRAIN,
    "🧠・Sala del DT": VOICE_DT,
    "🎵・Chill": VOICE_CHILL,
}

ROLE_RENAMES = {
    "👑 PRESIDENTE": ROLE_PRESIDENT,
    "🛡️ DIRECTIVA": ROLE_BOARD,
    "🎩 DT": ROLE_DT,
    "🧠 CAPITÁN": ROLE_CAPTAIN,
    "⭐ TITULAR": ROLE_STARTER,
    "🔄 PLANTILLA": ROLE_ROSTER,
    "🧪 A PRUEBA": ROLE_TRIAL,
    "🎥 CREADOR": ROLE_CREATOR,
    "🤝 INVITADO": ROLE_GUEST,
    "👥 COMUNIDAD": ROLE_COMMUNITY,
    "🤖 BOTS": ROLE_BOTS,

    "🧤 PO": POSITION_ROLES["PO"],
    "🛡️ DFC": POSITION_ROLES["DFC"],
    "🏃 LD": POSITION_ROLES["LD"],
    "🏃 LI": POSITION_ROLES["LI"],
    "⚙️ MCD": POSITION_ROLES["MCD"],
    "🎛️ MC": POSITION_ROLES["MC"],
    "🎨 MCO": POSITION_ROLES["MCO"],
    "⚡ MD": POSITION_ROLES["MD"],
    "⚡ MI": POSITION_ROLES["MI"],
    "🎯 DC": POSITION_ROLES["DC"],
}


# =========================================================
# HELPERS
# =========================================================

def role_by_name(guild, name):
    return discord.utils.get(guild.roles, name=name)

def category_by_name(guild, name):
    return discord.utils.get(guild.categories, name=name)

def text_by_name(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

def channel_by_name(guild, name):
    return discord.utils.get(guild.channels, name=name)

def is_staff(member):
    return member.guild_permissions.administrator or any(r.name in STAFF_ROLES for r in member.roles)

def is_leadership(member):
    return member.guild_permissions.administrator or any(r.name in LEADERSHIP_ROLES for r in member.roles)

def safe_channel_name(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9áéíóúñ_-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:45] or "jugador"

def public_overwrites(guild):
    return {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True, read_message_history=True,
            send_messages=True, connect=True, speak=True
        )
    }

def staff_only_overwrites(guild):
    ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    for name in STAFF_ROLES:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=True, manage_messages=True,
                connect=True, speak=True
            )
    return ow

def leadership_overwrites(guild):
    ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    for name in LEADERSHIP_ROLES:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=True, manage_messages=True,
                connect=True, speak=True
            )
    return ow

def locker_overwrites(guild):
    allowed = [
        ROLE_PRESIDENT, ROLE_BOARD, ROLE_DT, ROLE_CAPTAIN,
        ROLE_STARTER, ROLE_ROSTER
    ]
    ow = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    for name in allowed:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=True, connect=True, speak=True
            )
    return ow

def staff_write_overwrites(guild):
    ow = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True, read_message_history=True, send_messages=False
        )
    }
    for name in LEADERSHIP_ROLES:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=True, manage_messages=True
            )
    return ow


# =========================================================
# MIGRACIÓN
# =========================================================

async def migrate_names(guild):
    print("\n[1/5] Aplicando el nuevo estilo...")

    # Roles
    for old, new in ROLE_RENAMES.items():
        old_role = role_by_name(guild, old)
        new_role = role_by_name(guild, new)
        if old_role and not new_role:
            try:
                await old_role.edit(name=new, reason="Santacho FC V3 visual upgrade")
                print(f"  ✓ Rol: {old} -> {new}")
                await asyncio.sleep(0.15)
            except discord.HTTPException as e:
                print(f"  ! No pude renombrar rol {old}: {e}")

    # Categorías
    for old, new in CATEGORY_RENAMES.items():
        old_cat = category_by_name(guild, old)
        new_cat = category_by_name(guild, new)
        if old_cat and not new_cat:
            try:
                await old_cat.edit(name=new, reason="Santacho FC V3 visual upgrade")
                print(f"  ✓ Categoría: {old}")
                await asyncio.sleep(0.15)
            except discord.HTTPException as e:
                print(f"  ! No pude renombrar categoría {old}: {e}")

    # Canales
    for old, new in CHANNEL_RENAMES.items():
        old_ch = channel_by_name(guild, old)
        new_ch = channel_by_name(guild, new)
        if old_ch and not new_ch:
            try:
                await old_ch.edit(name=new, reason="Santacho FC V3 visual upgrade")
                print(f"  ✓ Canal: {old}")
                await asyncio.sleep(0.15)
            except discord.HTTPException as e:
                print(f"  ! No pude renombrar canal {old}: {e}")


# =========================================================
# SETUP
# =========================================================

async def ensure_role(guild, name, colour, hoist):
    role = role_by_name(guild, name)
    if role:
        try:
            await role.edit(colour=discord.Colour(colour), hoist=hoist)
        except discord.HTTPException:
            pass
        return role
    return await guild.create_role(
        name=name,
        colour=discord.Colour(colour),
        hoist=hoist,
        reason="Santacho FC V3 setup"
    )

async def ensure_roles(guild):
    print("\n[2/5] Verificando roles...")
    for name, colour, hoist in BASE_ROLES:
        await ensure_role(guild, name, colour, hoist)
    for name in POSITION_ROLES.values():
        await ensure_role(guild, name, 0xAFAFAF, False)

async def ensure_category(guild, name):
    existing = category_by_name(guild, name)
    if existing:
        return existing

    if name == CAT_TRYOUT:
        overwrites = staff_only_overwrites(guild)
    elif name == CAT_LOCKER:
        overwrites = locker_overwrites(guild)
    elif name == CAT_STAFF:
        overwrites = leadership_overwrites(guild)
    else:
        overwrites = public_overwrites(guild)

    return await guild.create_category(
        name, overwrites=overwrites, reason="Santacho FC V3 setup"
    )

async def ensure_channel(guild, category, kind, name):
    if kind == "text":
        existing = discord.utils.get(category.text_channels, name=name)
        if existing:
            return existing

        kwargs = dict(name=name, category=category, reason="Santacho FC V3 setup")

        readonly = {
            CH_RULES, CH_ANNOUNCE, CH_TROPHIES, CH_JOIN,
            CH_CALENDAR, CH_CALLED, CH_LINEUPS, CH_RESULTS,
            CH_STATS, CH_TABLE, CH_RECRUIT, CH_ACCEPTED, CH_ROSTER, CH_PLAYER_STATS, CH_MVP
        }
        if name in readonly:
            kwargs["overwrites"] = staff_write_overwrites(guild)

        if name == CH_BOT_DATA:
            kwargs["overwrites"] = data_channel_overwrites(guild)

        return await guild.create_text_channel(**kwargs)

    existing = discord.utils.get(category.voice_channels, name=name)
    if existing:
        return existing

    kwargs = dict(name=name, category=category, reason="Santacho FC V3 setup")

    if name == VOICE_DT:
        kwargs["overwrites"] = leadership_overwrites(guild)
    elif name in {VOICE_MATCH, VOICE_TRAIN}:
        kwargs["overwrites"] = locker_overwrites(guild)

    return await guild.create_voice_channel(**kwargs)

async def ensure_structure(guild):
    print("\n[3/6] Verificando categorías y canales...")
    for category_name, channels in CATEGORY_BLUEPRINT:
        cat = await ensure_category(guild, category_name)
        for kind, channel_name in channels:
            await ensure_channel(guild, cat, kind, channel_name)
            await asyncio.sleep(0.08)


async def cleanup_default_channels(guild):
    """Borra únicamente los dos canales iniciales sin categoría llamados general/General."""
    target_system = text_by_name(guild, CH_GENERAL) or text_by_name(guild, CH_WELCOME)

    for channel in list(guild.channels):
        if channel.category is not None:
            continue

        is_default_text = isinstance(channel, discord.TextChannel) and channel.name.lower() == "general"
        is_default_voice = isinstance(channel, discord.VoiceChannel) and channel.name.lower() == "general"
        if not (is_default_text or is_default_voice):
            continue

        try:
            if isinstance(channel, discord.TextChannel) and guild.system_channel and guild.system_channel.id == channel.id:
                try:
                    await guild.edit(system_channel=target_system, reason="Santacho FC V4 cleanup")
                except discord.HTTPException:
                    pass
            await channel.delete(reason="Santacho FC V4: quitar canales predeterminados")
            print(f"  ✓ Eliminado canal predeterminado: {channel.name}")
            await asyncio.sleep(0.2)
        except discord.HTTPException as exc:
            print(f"  ! No pude borrar {channel.name}: {exc}")


async def organize_categories(guild):
    """Ordena las categorías principales de Santacho FC."""
    desired = [
        CAT_INFO, CAT_CLUB, CAT_COMP, CAT_LOCKER, CAT_SCOUT,
        CAT_TRYOUT, CAT_TV, CAT_VOICE, CAT_BOTS, CAT_ROSTER, CAT_STAFF,
    ]
    for position, name in enumerate(desired):
        category = category_by_name(guild, name)
        if not category:
            continue
        try:
            await category.edit(position=position, reason="Santacho FC V4 organization")
            await asyncio.sleep(0.12)
        except discord.HTTPException:
            pass

    # Mantiene el orden de canales dentro de cada categoría según el blueprint.
    for category_name, channels in CATEGORY_BLUEPRINT:
        category = category_by_name(guild, category_name)
        if not category:
            continue
        for position, (_, channel_name) in enumerate(channels):
            channel = discord.utils.get(category.channels, name=channel_name)
            if channel:
                try:
                    await channel.edit(position=position, reason="Santacho FC V4 channel order")
                    await asyncio.sleep(0.05)
                except discord.HTTPException:
                    pass


async def group_external_bots(guild):
    """Agrupa bots externos visibles bajo el rol 🤖・BOTS cuando Discord los tiene en caché."""
    bot_role = role_by_name(guild, ROLE_BOTS)
    community_role = role_by_name(guild, ROLE_COMMUNITY)
    if not bot_role:
        return

    # Intenta dejar BOTS encima de Comunidad sin tocar roles administrados por Discord.
    if community_role:
        try:
            desired_position = max(community_role.position + 1, 1)
            if bot_role.position != desired_position and bot_role < guild.me.top_role:
                await bot_role.edit(position=desired_position, reason="Santacho FC V4 role order")
        except discord.HTTPException:
            pass

    assigned = 0
    for member in list(guild.members):
        if not member.bot or (guild.me and member.id == guild.me.id):
            continue
        if bot_role in member.roles:
            continue
        try:
            await member.add_roles(bot_role, reason="Santacho FC V4 bot grouping")
            assigned += 1
            await asyncio.sleep(0.08)
        except discord.HTTPException:
            pass

    if assigned:
        print(f"  ✓ Bots externos agrupados: {assigned}")




def readonly_public_overwrites(guild):
    """Todos pueden ver; solo liderazgo puede publicar."""
    ow = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=False,
            add_reactions=True,
        )
    }
    for name in LEADERSHIP_ROLES:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
            )
    return ow


def community_overwrites(guild):
    return {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=True,
            add_reactions=True,
            attach_files=True,
            embed_links=True,
            connect=True,
            speak=True,
        )
    }


def data_channel_overwrites(guild):
    ow = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False,
            send_messages=False,
            read_message_history=False,
        )
    }
    if guild.me:
        ow[guild.me] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_messages=True,
        )
    for name in STAFF_ROLES:
        role = role_by_name(guild, name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
            )
    return ow


async def enforce_permissions(guild):
    # INFORMACIÓN: solo lectura.
    for name in [CH_WELCOME, CH_RULES, CH_ANNOUNCE, CH_TROPHIES, CH_JOIN, CH_SOCIALS]:
        ch = text_by_name(guild, name)
        if ch:
            try:
                await ch.edit(overwrites=readonly_public_overwrites(guild), reason="Santacho FC V5 permisos")
            except discord.HTTPException:
                pass

    # SANTACHO FC: comunidad abierta.
    for name in [CH_GENERAL, CH_MEDIA, CH_MEMES, CH_FOOTBALL, CH_FC, CH_POSITIONS, CH_SUGGEST]:
        ch = text_by_name(guild, name)
        if ch:
            try:
                await ch.edit(overwrites=community_overwrites(guild), reason="Santacho FC V5 permisos")
            except discord.HTTPException:
                pass

    # COMPETICIÓN y PLANTILLA: solo lectura para miembros.
    for name in [CH_CALENDAR, CH_CALLED, CH_LINEUPS, CH_RESULTS, CH_STATS, CH_TABLE,
                 CH_ROSTER, CH_PLAYER_STATS, CH_MVP]:
        ch = text_by_name(guild, name)
        if ch:
            try:
                await ch.edit(overwrites=readonly_public_overwrites(guild), reason="Santacho FC V5 permisos")
            except discord.HTTPException:
                pass

    # VESTUARIO: privado para plantilla oficial + liderazgo.
    locker = category_by_name(guild, CAT_LOCKER)
    if locker:
        try:
            await locker.edit(overwrites=locker_overwrites(guild), reason="Santacho FC V5 permisos")
        except discord.HTTPException:
            pass
        for ch in locker.channels:
            try:
                await ch.edit(sync_permissions=True, reason="Santacho FC V5 permisos")
            except discord.HTTPException:
                pass

    # DIRECTIVA: privada.
    staff_cat = category_by_name(guild, CAT_STAFF)
    if staff_cat:
        try:
            await staff_cat.edit(overwrites=leadership_overwrites(guild), reason="Santacho FC V5 permisos")
        except discord.HTTPException:
            pass

    # Datos internos del bot: ocultos.
    data_ch = text_by_name(guild, CH_BOT_DATA)
    if data_ch:
        try:
            await data_ch.edit(overwrites=data_channel_overwrites(guild), reason="Santacho FC V5 datos")
        except discord.HTTPException:
            pass


def find_cached_bot(guild, keywords):
    """
    Busca bots externos ya visibles en caché.
    Si Discord no los incluyó en guild.members, /configurarbots permite seleccionarlos manualmente.
    """
    words = [w.lower() for w in keywords]
    for member in guild.members:
        if not member.bot:
            continue
        haystack = f"{member.name} {member.display_name}".lower()
        if any(word in haystack for word in words):
            return member
    return None


def bot_base_channel_overwrites(guild):
    """
    Canal visible para todos. Usuarios pueden usar slash commands,
    pero no escribir mensajes normales salvo en comandos-bot.
    """
    ow = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=False,
            add_reactions=True,
            use_application_commands=True,
        )
    }

    if guild.me:
        ow[guild.me] = discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            add_reactions=True,
            use_application_commands=True,
        )

    for role_name in LEADERSHIP_ROLES:
        role = role_by_name(guild, role_name)
        if role:
            ow[role] = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True,
                use_application_commands=True,
            )

    return ow


def bot_member_overwrite():
    return discord.PermissionOverwrite(
        view_channel=True,
        read_message_history=True,
        send_messages=True,
        embed_links=True,
        attach_files=True,
        add_reactions=True,
        use_application_commands=True,
    )


async def assign_bot_role(guild, member):
    if not member or not member.bot:
        return False

    role = role_by_name(guild, ROLE_BOTS)
    if not role or role in member.roles:
        return True

    try:
        await member.add_roles(role, reason="Santacho FC V6: agrupar aplicaciones")
        return True
    except discord.HTTPException:
        return False


async def configure_external_bots(guild, sesh=None, statbot=None):
    """
    Configura la zona de bots.
    No cambia ajustes internos privados de SeshBot/Statbot;
    sí configura canales, permisos y organización dentro de Santacho FC.
    """
    sesh = sesh or find_cached_bot(guild, ["seshbot", "sesh"])
    statbot = statbot or find_cached_bot(guild, ["statbot"])

    commands_ch = text_by_name(guild, CH_BOT_COMMANDS)
    events_ch = text_by_name(guild, CH_BOT_EVENTS)
    stats_ch = text_by_name(guild, CH_BOT_STATS)

    # COMANDOS-BOT: chat normal permitido.
    if commands_ch:
        ow = bot_base_channel_overwrites(guild)
        ow[guild.default_role] = discord.PermissionOverwrite(
            view_channel=True,
            read_message_history=True,
            send_messages=True,
            add_reactions=True,
            embed_links=True,
            attach_files=True,
            use_application_commands=True,
        )
        if sesh:
            ow[sesh] = bot_member_overwrite()
        if statbot:
            ow[statbot] = bot_member_overwrite()

        try:
            await commands_ch.edit(
                topic="Comandos generales de aplicaciones y bots de Santacho FC.",
                overwrites=ow,
                reason="Santacho FC V6: configurar bots",
            )
        except discord.HTTPException:
            pass

    # EVENTOS-BOT: limpio; usuarios usan slash commands, Sesh publica.
    if events_ch:
        ow = bot_base_channel_overwrites(guild)
        if sesh:
            ow[sesh] = bot_member_overwrite()
        if statbot:
            # Puede ver, pero no ensucia el canal con respuestas propias.
            ow[statbot] = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=False,
                use_application_commands=True,
            )

        try:
            await events_ch.edit(
                topic="Eventos, partidos, entrenamientos y RSVP gestionados con SeshBot.",
                overwrites=ow,
                reason="Santacho FC V6: configurar SeshBot",
            )
        except discord.HTTPException:
            pass

    # STATS-BOT: limpio; usuarios usan slash commands, Statbot publica.
    if stats_ch:
        ow = bot_base_channel_overwrites(guild)
        if statbot:
            ow[statbot] = bot_member_overwrite()
        if sesh:
            ow[sesh] = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=False,
                use_application_commands=True,
            )

        try:
            await stats_ch.edit(
                topic="Analítica de actividad del servidor y comandos de Statbot.",
                overwrites=ow,
                reason="Santacho FC V6: configurar Statbot",
            )
        except discord.HTTPException:
            pass

    await assign_bot_role(guild, sesh)
    await assign_bot_role(guild, statbot)

    return sesh, statbot


async def ensure_external_bot_panels(guild):
    commands_ch = text_by_name(guild, CH_BOT_COMMANDS)
    events_ch = text_by_name(guild, CH_BOT_EVENTS)
    stats_ch = text_by_name(guild, CH_BOT_STATS)

    if commands_ch:
        embed = discord.Embed(
            title="🤖 𝐂𝐄𝐍𝐓𝐑𝐎 𝐃𝐄 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒",
            description=(
                "Canal para comandos generales de aplicaciones.\n\n"
                "📅 **SeshBot** → eventos y asistencia\n"
                "📊 **Statbot** → analítica del servidor\n"
                "🟡⚫ **Santacho FC** → plantilla, pruebas, tickets y competición"
            ),
            color=GOLD,
        )
        await upsert_clean_embed(commands_ch, embed.title, embed)

    if events_ch:
        embed = discord.Embed(
            title="📅 𝐄𝐕𝐄𝐍𝐓𝐎𝐒 — 𝐒𝐄𝐒𝐇𝐁𝐎𝐓",
            description=(
                "Usa aquí los comandos de **SeshBot** para crear y gestionar:\n\n"
                "⚽ Partidos\n"
                "🏋️ Entrenamientos\n"
                "🧪 Pruebas\n"
                "👥 Reuniones de plantilla\n\n"
                "Este canal está bloqueado para conversación normal para mantenerlo limpio."
            ),
            color=GOLD,
        )
        await upsert_clean_embed(events_ch, embed.title, embed)

    if stats_ch:
        embed = discord.Embed(
            title="📊 𝐀𝐍𝐀𝐋Í𝐓𝐈𝐂𝐀 — 𝐒𝐓𝐀𝐓𝐁𝐎𝐓",
            description=(
                "Usa aquí los comandos de **Statbot** para revisar actividad y participación.\n\n"
                "Este canal está separado de las **estadísticas deportivas** de Santacho FC."
            ),
            color=GOLD,
        )
        await upsert_clean_embed(stats_ch, embed.title, embed)


async def apply_v6_layout(guild):
    print("\n[4/6] Limpiando y ordenando Santacho FC...")
    await cleanup_default_channels(guild)
    await organize_categories(guild)
    await group_external_bots(guild)
    await enforce_permissions(guild)
    await configure_external_bots(guild)


# =========================================================
# TRYOUT / POSITIONS
# =========================================================

class TryoutModal(discord.ui.Modal, title="Prueba — Santacho FC"):
    gamertag = discord.ui.TextInput(label="Gamertag / ID", placeholder="Ej: ArmenKR20", max_length=50)
    perfil = discord.ui.TextInput(label="Edad / País / Plataforma", placeholder="Ej: 22 / Colombia / PS5", max_length=100)
    posiciones = discord.ui.TextInput(label="Posición principal y secundaria", placeholder="Ej: MCO / MC", max_length=60)
    horarios = discord.ui.TextInput(label="Horarios disponibles", placeholder="Ej: Lun-Jue 8pm-11pm COL", max_length=120)
    experiencia = discord.ui.TextInput(
        label="Experiencia / estilo / por qué Santacho",
        style=discord.TextStyle.paragraph,
        max_length=700
    )

    async def on_submit(self, interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return

        guild = interaction.guild
        member = interaction.user
        marker = f"ticket_user_id:{member.id}"

        for ch in guild.text_channels:
            if ch.topic and marker in ch.topic:
                await interaction.response.send_message(
                    f"Ya tienes una prueba abierta: {ch.mention}", ephemeral=True
                )
                return

        await interaction.response.defer(ephemeral=True, thinking=True)

        cat = category_by_name(guild, CAT_TRYOUT)
        if not cat:
            cat = await ensure_category(guild, CAT_TRYOUT)

        ow = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=True, attach_files=True, embed_links=True
            )
        }
        for name in STAFF_ROLES:
            role = role_by_name(guild, name)
            if role:
                ow[role] = discord.PermissionOverwrite(
                    view_channel=True, read_message_history=True,
                    send_messages=True, manage_messages=True
                )

        channel = await guild.create_text_channel(
            f"🧪・prueba-{safe_channel_name(member.display_name)}-{str(member.id)[-4:]}",
            category=cat,
            topic=f"Santacho FC tryout | {marker}",
            overwrites=ow
        )

        embed = discord.Embed(
            title="🧪 𝐍𝐔𝐄𝐕𝐀 𝐒𝐎𝐋𝐈𝐂𝐈𝐓𝐔𝐃 𝐃𝐄 𝐏𝐑𝐔𝐄𝐁𝐀",
            description=f"Jugador: {member.mention}",
            color=GOLD,
        )
        embed.add_field(name="🎮 Gamertag", value=str(self.gamertag), inline=False)
        embed.add_field(name="👤 Perfil", value=str(self.perfil), inline=False)
        embed.add_field(name="⚽ Posiciones", value=str(self.posiciones), inline=False)
        embed.add_field(name="⏰ Horarios", value=str(self.horarios), inline=False)
        embed.add_field(name="🏆 Experiencia", value=str(self.experiencia), inline=False)

        await channel.send(
            content=f"{member.mention} — bienvenido a tu prueba privada.",
            embed=embed,
            view=TicketStaffView()
        )

        await interaction.followup.send(
            f"✅ Solicitud enviada: {channel.mention}", ephemeral=True
        )


class TryoutPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Quiero probar",
        emoji="🧪",
        style=discord.ButtonStyle.primary,
        custom_id="santacho:v3:tryout"
    )
    async def open_tryout(self, interaction, button):
        await interaction.response.send_modal(TryoutModal())


class PositionSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Portero", value="PO", emoji="🧤"),
            discord.SelectOption(label="Defensa central", value="DFC", emoji="🛡️"),
            discord.SelectOption(label="Lateral derecho", value="LD", emoji="🏃"),
            discord.SelectOption(label="Lateral izquierdo", value="LI", emoji="🏃"),
            discord.SelectOption(label="MCD", value="MCD", emoji="⚙️"),
            discord.SelectOption(label="MC", value="MC", emoji="🎛️"),
            discord.SelectOption(label="MCO", value="MCO", emoji="🎨"),
            discord.SelectOption(label="MD", value="MD", emoji="⚡"),
            discord.SelectOption(label="MI", value="MI", emoji="⚡"),
            discord.SelectOption(label="DC", value="DC", emoji="🎯"),
        ]
        super().__init__(
            placeholder="Selecciona de 1 a 3 posiciones",
            min_values=1,
            max_values=3,
            options=options,
            custom_id="santacho:v3:positions"
        )

    async def callback(self, interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return

        member = interaction.user
        guild = interaction.guild

        all_roles = [role_by_name(guild, n) for n in POSITION_ROLES.values()]
        all_roles = [r for r in all_roles if r]
        selected = [role_by_name(guild, POSITION_ROLES[v]) for v in self.values]
        selected = [r for r in selected if r]
        remove = [r for r in all_roles if r in member.roles and r not in selected]

        try:
            if remove:
                await member.remove_roles(*remove, reason="Santacho FC positions")
            if selected:
                await member.add_roles(*selected, reason="Santacho FC positions")
        except discord.Forbidden:
            await interaction.response.send_message(
                "No pude darte los roles. El rol del bot debe estar arriba de los roles de posición.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "✅ Posiciones: " + ", ".join(r.name for r in selected),
            ephemeral=True
        )


class PositionPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PositionSelect())


def ticket_user_id(channel):
    if not channel.topic:
        return None
    m = re.search(r"ticket_user_id:(\d+)", channel.topic)
    return int(m.group(1)) if m else None


class TicketStaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def staff_check(self, interaction):
        if not isinstance(interaction.user, discord.Member) or not is_staff(interaction.user):
            await interaction.response.send_message("⛔ Solo staff.", ephemeral=True)
            return False
        return True

    async def target(self, interaction):
        if not isinstance(interaction.channel, discord.TextChannel):
            return None
        uid = ticket_user_id(interaction.channel)
        if not uid:
            return None
        return interaction.guild.get_member(uid)

    @discord.ui.button(label="A prueba", emoji="🧪", style=discord.ButtonStyle.primary, custom_id="santacho:v3:trial")
    async def trial(self, interaction, button):
        if not await self.staff_check(interaction):
            return
        member = await self.target(interaction)
        role = role_by_name(interaction.guild, ROLE_TRIAL)
        if member and role:
            await member.add_roles(role)
            await interaction.response.send_message(f"🧪 {member.mention} quedó **A PRUEBA**.")
        else:
            await interaction.response.send_message("No pude encontrar jugador/rol.", ephemeral=True)

    @discord.ui.button(label="Plantilla", emoji="⭐", style=discord.ButtonStyle.success, custom_id="santacho:v3:roster")
    async def roster(self, interaction, button):
        if not await self.staff_check(interaction):
            return
        member = await self.target(interaction)
        roster = role_by_name(interaction.guild, ROLE_ROSTER)
        trial = role_by_name(interaction.guild, ROLE_TRIAL)
        if member and roster:
            if trial and trial in member.roles:
                await member.remove_roles(trial)
            await member.add_roles(roster)

            accepted = text_by_name(interaction.guild, CH_ACCEPTED)
            if accepted:
                await accepted.send(f"⭐ {member.mention} se incorpora a **Santacho FC**.")

            await interaction.response.send_message(f"⭐ {member.mention} pasó a **PLANTILLA**.")
        else:
            await interaction.response.send_message("No pude encontrar jugador/rol.", ephemeral=True)

    @discord.ui.button(label="Rechazar", emoji="❌", style=discord.ButtonStyle.danger, custom_id="santacho:v3:reject")
    async def reject(self, interaction, button):
        if not await self.staff_check(interaction):
            return
        member = await self.target(interaction)
        name = member.mention if member else "Jugador"
        await interaction.response.send_message(
            f"❌ {name} no fue seleccionado en esta oportunidad."
        )

    @discord.ui.button(label="Cerrar", emoji="🔒", style=discord.ButtonStyle.secondary, custom_id="santacho:v3:close")
    async def close(self, interaction, button):
        if not await self.staff_check(interaction):
            return
        await interaction.response.send_message("🔒 Cerrando ticket...")
        await asyncio.sleep(1.2)
        await interaction.channel.delete(reason="Santacho FC ticket cerrado")


# =========================================================
# PANELES
# =========================================================

async def ensure_panel(channel, marker, embed, view):
    title = embed.title or marker
    async for msg in channel.history(limit=60):
        if msg.author != channel.guild.me or not msg.embeds:
            continue
        footer = msg.embeds[0].footer.text or ""
        if footer.startswith("SANTACHO_V4_") or footer.startswith("SANTACHO_V5_"):
            try:
                await msg.delete()
            except discord.HTTPException:
                pass
            continue
        if msg.embeds[0].title == title:
            await msg.edit(embed=embed, view=view)
            return msg
    return await channel.send(embed=embed, view=view)


async def ensure_panels(guild):
    print("\n[5/6] Verificando paneles...")

    welcome_ch = text_by_name(guild, CH_WELCOME)
    if welcome_ch:
        embed = discord.Embed(
            title="🟡⚫ 𝐁𝐈𝐄𝐍𝐕𝐄𝐍𝐈𝐃𝐎 𝐀 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂",
            description=(
                "**Clubes Pro • FC27**\n\n"
                "Esta es la casa de **Santacho FC**: competición, plantilla, pruebas y comunidad.\n\n"
                f"📜 Lee {text_by_name(guild, CH_RULES).mention if text_by_name(guild, CH_RULES) else 'las reglas'}\n"
                f"🧪 ¿Quieres jugar? Ve a {text_by_name(guild, CH_TRY).mention if text_by_name(guild, CH_TRY) else 'pruebas'}\n"
                f"⚽ Habla con la comunidad en {text_by_name(guild, CH_GENERAL).mention if text_by_name(guild, CH_GENERAL) else 'la cancha'}"
            ),
            color=GOLD,
        )
        embed.add_field(name="𝐍𝐮𝐞𝐬𝐭𝐫𝐚 𝐢𝐝𝐞𝐧𝐭𝐢𝐝𝐚𝐝", value="**El escudo está primero.**", inline=False)
        await ensure_panel(welcome_ch, "SANTACHO_V5_WELCOME", embed, discord.ui.View(timeout=None))

    bots_ch = text_by_name(guild, CH_BOT_COMMANDS)
    if bots_ch:
        embed = discord.Embed(
            title="🤖 𝐂𝐄𝐍𝐓𝐑𝐎 𝐃𝐄 𝐁𝐎𝐓𝐒",
            description=(
                "Usa este canal para comandos de aplicaciones externas y mantener **la cancha** limpia.\n\n"
                "📅 **SeshBot** — eventos, horarios y RSVP\n"
                "📊 **Statbot** — actividad y estadísticas del servidor\n"
                "🟡⚫ **Santacho FC** — pruebas, tickets, posiciones, convocatorias y resultados"
            ),
            color=GOLD,
        )
        await ensure_panel(bots_ch, "SANTACHO_V5_BOTS", embed, discord.ui.View(timeout=None))

    try_ch = text_by_name(guild, CH_TRY)
    if try_ch:
        embed = discord.Embed(
            title="🧪 𝐏𝐑𝐔𝐄𝐁𝐀𝐒 — 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂",
            description=(
                "¿Quieres vestir el escudo?\n\n"
                "Pulsa **Quiero probar** y completa el formulario.\n"
                "Se abrirá un canal privado con nuestro staff."
            ),
            color=GOLD
        )
        embed.add_field(
            name="𝐋𝐨 𝐪𝐮𝐞 𝐛𝐮𝐬𝐜𝐚𝐦𝐨𝐬",
            value="🎙️ Comunicación\n⚽ Juego colectivo\n🧠 Disciplina\n🔥 Mentalidad competitiva",
            inline=False
        )
        await ensure_panel(try_ch, "SANTACHO_V3_TRYOUT", embed, TryoutPanelView())

    pos_ch = text_by_name(guild, CH_POSITIONS)
    if pos_ch:
        embed = discord.Embed(
            title="⚽ 𝐄𝐋𝐈𝐆𝐄 𝐓𝐔𝐒 𝐏𝐎𝐒𝐈𝐂𝐈𝐎𝐍𝐄𝐒",
            description=(
                "Escoge entre **1 y 3 posiciones**.\n\n"
                "El bot actualizará tus roles automáticamente."
            ),
            color=GOLD
        )
        await ensure_panel(pos_ch, "SANTACHO_V3_POSITIONS", embed, PositionPanelView())




# =========================================================
# ESTADÍSTICAS PERSISTENTES EN DISCORD
# =========================================================

STAT_MARKER = "SANTACHO_PLAYER_STAT:"


def empty_stats():
    return {"pj": 0, "goles": 0, "asistencias": 0, "mvp": 0, "porterias": 0}


async def get_data_channel(guild):
    ch = text_by_name(guild, CH_BOT_DATA)
    if ch:
        return ch
    cat = category_by_name(guild, CAT_STAFF)
    if not cat:
        cat = await ensure_category(guild, CAT_STAFF)
    return await guild.create_text_channel(
        CH_BOT_DATA,
        category=cat,
        overwrites=data_channel_overwrites(guild),
        reason="Santacho FC V5 stats storage",
    )


async def find_stat_message(guild, user_id: int):
    channel = await get_data_channel(guild)
    marker = f"{STAT_MARKER}{user_id}"
    async for message in channel.history(limit=500):
        if message.author == guild.me and message.content.startswith(marker):
            return message
    return None


def parse_stat_message(message):
    stats = empty_stats()
    if not message:
        return stats
    try:
        raw = message.content.split("\n", 1)[1]
        data = json.loads(raw)
        for key in stats:
            stats[key] = int(data.get(key, 0))
    except Exception:
        pass
    return stats


async def save_player_stats(guild, member, stats):
    channel = await get_data_channel(guild)
    payload = json.dumps(stats, ensure_ascii=False, separators=(",", ":"))
    content = f"{STAT_MARKER}{member.id}\n{payload}"
    msg = await find_stat_message(guild, member.id)
    if msg:
        await msg.edit(content=content)
    else:
        await channel.send(content)


async def load_player_stats(guild, member):
    return parse_stat_message(await find_stat_message(guild, member.id))


async def all_player_stats(guild):
    channel = await get_data_channel(guild)
    rows = []
    async for message in channel.history(limit=500):
        if message.author != guild.me or not message.content.startswith(STAT_MARKER):
            continue
        first = message.content.split("\n", 1)[0]
        try:
            uid = int(first.split(":", 1)[1])
        except Exception:
            continue
        member = guild.get_member(uid)
        if member:
            rows.append((member, parse_stat_message(message)))
    return rows


def member_positions(member):
    positions = []
    for key, role_name in POSITION_ROLES.items():
        if any(r.name == role_name for r in member.roles):
            positions.append(key)
    return positions


async def upsert_clean_embed(channel, title, embed):
    async for msg in channel.history(limit=50):
        if msg.author == channel.guild.me and msg.embeds and msg.embeds[0].title == title:
            await msg.edit(embed=embed, view=None)
            return msg
    return await channel.send(embed=embed)


async def refresh_roster_panel(guild):
    channel = text_by_name(guild, CH_ROSTER)
    if not channel:
        return

    official = []
    for member in guild.members:
        if member.bot:
            continue
        if any(r.name in {ROLE_STARTER, ROLE_ROSTER} for r in member.roles):
            official.append(member)
    official.sort(key=lambda m: m.display_name.lower())

    embed = discord.Embed(
        title="👥 𝐏𝐋𝐀𝐍𝐓𝐈𝐋𝐋𝐀 𝐎𝐅𝐈𝐂𝐈𝐀𝐋 — 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂",
        description="Jugadores oficiales del club y sus posiciones actuales.",
        color=GOLD,
    )

    if not official:
        embed.add_field(name="Plantilla", value="Todavía no hay jugadores registrados.", inline=False)
    else:
        lines = []
        for member in official:
            pos = " / ".join(member_positions(member)) or "Sin posición"
            status = "⭐ Titular" if any(r.name == ROLE_STARTER for r in member.roles) else "🔄 Plantilla"
            lines.append(f"**{member.display_name}** — `{pos}` • {status}")
        embed.add_field(name=f"Jugadores — {len(official)}", value="\n".join(lines)[:1024], inline=False)

    await upsert_clean_embed(channel, embed.title, embed)


async def refresh_stats_panel(guild):
    channel = text_by_name(guild, CH_PLAYER_STATS)
    if not channel:
        return
    rows = await all_player_stats(guild)
    rows.sort(key=lambda item: (item[1]["goles"] + item[1]["asistencias"], item[1]["goles"], item[1]["mvp"]), reverse=True)

    embed = discord.Embed(
        title="📊 𝐄𝐒𝐓𝐀𝐃Í𝐒𝐓𝐈𝐂𝐀𝐒 — 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂",
        description="Estadísticas oficiales registradas por el staff.",
        color=GOLD,
    )
    if not rows:
        embed.add_field(name="Sin datos", value="Usa `/sumarstats` para empezar a registrar estadísticas.", inline=False)
    else:
        lines = []
        for i, (member, s) in enumerate(rows[:20], start=1):
            lines.append(
                f"`{i:>2}.` **{member.display_name}** — PJ {s['pj']} • ⚽ {s['goles']} • 🎯 {s['asistencias']} • ⭐ {s['mvp']} • 🧤 {s['porterias']}"
            )
        embed.add_field(name="Ranking", value="\n".join(lines)[:1024], inline=False)
    await upsert_clean_embed(channel, embed.title, embed)


async def refresh_mvp_panel(guild):
    channel = text_by_name(guild, CH_MVP)
    if not channel:
        return
    rows = await all_player_stats(guild)
    rows.sort(key=lambda item: (item[1]["mvp"], item[1]["goles"] + item[1]["asistencias"]), reverse=True)

    embed = discord.Embed(title="⭐ 𝐑𝐀𝐍𝐊𝐈𝐍𝐆 𝐌𝐕𝐏", description="Jugadores con más reconocimientos MVP.", color=GOLD)
    valid = [(m, s) for m, s in rows if s["mvp"] > 0]
    if not valid:
        embed.add_field(name="MVP", value="Todavía no hay MVP registrados.", inline=False)
    else:
        lines = [f"`{i}.` **{m.display_name}** — ⭐ {s['mvp']}" for i, (m, s) in enumerate(valid[:10], 1)]
        embed.add_field(name="Top MVP", value="\n".join(lines)[:1024], inline=False)
    await upsert_clean_embed(channel, embed.title, embed)


async def refresh_public_player_panels(guild):
    await refresh_roster_panel(guild)
    await refresh_stats_panel(guild)
    await refresh_mvp_panel(guild)

    await refresh_public_player_panels(guild)

    await ensure_external_bot_panels(guild)


# =========================================================
# BOT + SLASH COMMANDS
# =========================================================

class SantachoBot(commands.Bot):
    def __init__(self, guild_id):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
        self.guild_id = guild_id

    async def setup_hook(self):
        self.add_view(TryoutPanelView())
        self.add_view(PositionPanelView())
        self.add_view(TicketStaffView())

        obj = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=obj)
        await self.tree.sync(guild=obj)


@app_commands.guild_only()
@app_commands.command(name="disponibilidad", description="Publica disponibilidad semanal.")
@app_commands.describe(semana="Ej: 7-13 septiembre")
async def disponibilidad(interaction: discord.Interaction, semana: str = "Esta semana"):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return

    channel = text_by_name(interaction.guild, CH_AVAIL)
    if not channel:
        await interaction.response.send_message("No encontré el canal.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐈𝐋𝐈𝐃𝐀𝐃 𝐒𝐄𝐌𝐀𝐍𝐀𝐋",
        description=(
            f"**Semana:** {semana}\n\n"
            "✅ Disponible\n❌ No disponible\n❓ Por confirmar"
        ),
        color=GOLD
    )
    msg = await channel.send(embed=embed)
    for e in ("✅", "❌", "❓"):
        await msg.add_reaction(e)

    await interaction.response.send_message(f"✅ Publicado en {channel.mention}.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="convocatoria", description="Publica una convocatoria.")
@app_commands.describe(rival="Rival", fecha="Fecha", hora="Hora", competicion="Competición")
async def convocatoria(interaction: discord.Interaction, rival: str, fecha: str, hora: str, competicion: str = "Partido oficial"):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return

    channel = text_by_name(interaction.guild, CH_CALLED)
    if not channel:
        await interaction.response.send_message("No encontré el canal.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"🟡⚫ 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 𝐅𝐂 🆚 {rival}",
        description=(
            f"🏆 **{competicion}**\n"
            f"📅 **{fecha}**\n"
            f"⏰ **{hora}**\n\n"
            "✅ Voy\n❌ No puedo\n❓ Por confirmar\n\n"
            "**Conéctate 15 minutos antes.**"
        ),
        color=GOLD
    )
    msg = await channel.send(embed=embed)
    for e in ("✅", "❌", "❓"):
        await msg.add_reaction(e)

    await interaction.response.send_message(f"✅ Publicado en {channel.mention}.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="resultado", description="Publica el resultado final.")
async def resultado(
    interaction: discord.Interaction,
    rival: str,
    santacho: app_commands.Range[int, 0, 99],
    rival_goles: app_commands.Range[int, 0, 99],
    mvp: str = "Por definir"
):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return

    channel = text_by_name(interaction.guild, CH_RESULTS)
    if not channel:
        await interaction.response.send_message("No encontré el canal.", ephemeral=True)
        return

    status = "🏆 𝐕𝐈𝐂𝐓𝐎𝐑𝐈𝐀" if santacho > rival_goles else "🤝 𝐄𝐌𝐏𝐀𝐓𝐄" if santacho == rival_goles else "❌ 𝐃𝐄𝐑𝐑𝐎𝐓𝐀"

    embed = discord.Embed(
        title=f"{status} — 𝐒𝐀𝐍𝐓𝐀𝐂𝐇𝐎 {santacho}-{rival_goles} {rival}",
        description=f"⭐ **MVP:** {mvp}",
        color=GOLD
    )
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Resultado publicado.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="paneles", description="Verifica los paneles de Santacho.")
async def paneles(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo administrador.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await ensure_panels(interaction.guild)
    await interaction.followup.send("✅ Paneles listos.", ephemeral=True)




@app_commands.guild_only()
@app_commands.command(name="organizar", description="Vuelve a ordenar y limpiar Santacho FC.")
async def organizar(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo administrador.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    await ensure_roles(interaction.guild)
    await ensure_structure(interaction.guild)
    await apply_v6_layout(interaction.guild)
    await ensure_panels(interaction.guild)
    await interaction.followup.send("✅ Santacho FC quedó limpio y organizado.", ephemeral=True)




@app_commands.guild_only()
@app_commands.command(name="jugador", description="Muestra las estadísticas de un jugador.")
async def jugador(interaction: discord.Interaction, jugador: discord.Member):
    stats = await load_player_stats(interaction.guild, jugador)
    posiciones = " / ".join(member_positions(jugador)) or "Sin posición"
    embed = discord.Embed(title=f"📊 {jugador.display_name}", color=GOLD)
    embed.add_field(name="Posiciones", value=posiciones, inline=False)
    embed.add_field(name="Partidos", value=str(stats["pj"]), inline=True)
    embed.add_field(name="Goles", value=str(stats["goles"]), inline=True)
    embed.add_field(name="Asistencias", value=str(stats["asistencias"]), inline=True)
    embed.add_field(name="MVP", value=str(stats["mvp"]), inline=True)
    embed.add_field(name="Porterías a cero", value=str(stats["porterias"]), inline=True)
    await interaction.response.send_message(embed=embed)


@app_commands.guild_only()
@app_commands.command(name="sumarstats", description="Suma estadísticas oficiales a un jugador.")
async def sumarstats(
    interaction: discord.Interaction,
    jugador: discord.Member,
    partidos: app_commands.Range[int, 0, 20] = 0,
    goles: app_commands.Range[int, 0, 50] = 0,
    asistencias: app_commands.Range[int, 0, 50] = 0,
    mvp: app_commands.Range[int, 0, 20] = 0,
    porterias: app_commands.Range[int, 0, 20] = 0,
):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo puede registrar estadísticas.", ephemeral=True)
        return
    stats = await load_player_stats(interaction.guild, jugador)
    stats["pj"] += partidos
    stats["goles"] += goles
    stats["asistencias"] += asistencias
    stats["mvp"] += mvp
    stats["porterias"] += porterias
    await save_player_stats(interaction.guild, jugador, stats)
    await refresh_public_player_panels(interaction.guild)
    await interaction.response.send_message(f"✅ Estadísticas actualizadas para **{jugador.display_name}**.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="setstats", description="Fija las estadísticas totales de un jugador.")
async def setstats(
    interaction: discord.Interaction,
    jugador: discord.Member,
    partidos: app_commands.Range[int, 0, 999],
    goles: app_commands.Range[int, 0, 999],
    asistencias: app_commands.Range[int, 0, 999],
    mvp: app_commands.Range[int, 0, 999] = 0,
    porterias: app_commands.Range[int, 0, 999] = 0,
):
    if not isinstance(interaction.user, discord.Member) or not is_staff(interaction.user):
        await interaction.response.send_message("⛔ Solo staff puede usar este comando.", ephemeral=True)
        return
    stats = {"pj": partidos, "goles": goles, "asistencias": asistencias, "mvp": mvp, "porterias": porterias}
    await save_player_stats(interaction.guild, jugador, stats)
    await refresh_public_player_panels(interaction.guild)
    await interaction.response.send_message("✅ Estadísticas reemplazadas.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="plantilla", description="Actualiza el panel público de plantilla.")
async def plantilla(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await refresh_roster_panel(interaction.guild)
    await interaction.followup.send("✅ Plantilla actualizada.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="tabla", description="Actualiza la tabla pública de estadísticas.")
async def tabla(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    await refresh_stats_panel(interaction.guild)
    await refresh_mvp_panel(interaction.guild)
    await interaction.followup.send("✅ Estadísticas actualizadas.", ephemeral=True)


@app_commands.guild_only()
@app_commands.command(name="alineacion", description="Publica el XI inicial de Santacho FC.")
async def alineacion(interaction: discord.Interaction, rival: str, formacion: str, xi: str):
    if not isinstance(interaction.user, discord.Member) or not is_leadership(interaction.user):
        await interaction.response.send_message("⛔ Solo liderazgo.", ephemeral=True)
        return
    channel = text_by_name(interaction.guild, CH_LINEUPS)
    if not channel:
        await interaction.response.send_message("No encontré el canal de alineaciones.", ephemeral=True)
        return
    embed = discord.Embed(
        title=f"📋 𝐗𝐈 𝐈𝐍𝐈𝐂𝐈𝐀𝐋 — 🆚 {rival}",
        description=f"**Formación:** {formacion}\n\n{xi}",
        color=GOLD,
    )
    embed.set_footer(text=f"Publicado por {interaction.user.display_name}")
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Alineación publicada en {channel.mention}.", ephemeral=True)




@app_commands.guild_only()
@app_commands.command(
    name="configurarbots",
    description="Configura SeshBot y Statbot dentro de Santacho FC."
)
@app_commands.describe(
    sesh="Selecciona SeshBot si no fue detectado automáticamente",
    statbot="Selecciona Statbot si no fue detectado automáticamente",
)
async def configurarbots(
    interaction: discord.Interaction,
    sesh: Optional[discord.Member] = None,
    statbot: Optional[discord.Member] = None,
):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Solo un administrador puede usar este comando.", ephemeral=True)
        return

    if sesh and not sesh.bot:
        await interaction.response.send_message("⛔ El miembro elegido como Sesh no es un bot.", ephemeral=True)
        return
    if statbot and not statbot.bot:
        await interaction.response.send_message("⛔ El miembro elegido como Statbot no es un bot.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True, thinking=True)

    await ensure_structure(interaction.guild)
    found_sesh, found_statbot = await configure_external_bots(
        interaction.guild,
        sesh=sesh,
        statbot=statbot,
    )
    await ensure_external_bot_panels(interaction.guild)
    await organize_categories(interaction.guild)

    sesh_text = found_sesh.mention if found_sesh else "❌ No detectado"
    stat_text = found_statbot.mention if found_statbot else "❌ No detectado"

    message = (
        "✅ **Zona de bots configurada.**\n\n"
        f"📅 SeshBot: {sesh_text}\n"
        f"📊 Statbot: {stat_text}\n\n"
        f"🤖 {text_by_name(interaction.guild, CH_BOT_COMMANDS).mention if text_by_name(interaction.guild, CH_BOT_COMMANDS) else CH_BOT_COMMANDS}\n"
        f"📅 {text_by_name(interaction.guild, CH_BOT_EVENTS).mention if text_by_name(interaction.guild, CH_BOT_EVENTS) else CH_BOT_EVENTS}\n"
        f"📊 {text_by_name(interaction.guild, CH_BOT_STATS).mention if text_by_name(interaction.guild, CH_BOT_STATS) else CH_BOT_STATS}"
    )

    if not found_sesh or not found_statbot:
        message += (
            "\n\nSi alguno dice **No detectado**, ejecuta `/configurarbots` otra vez "
            "y selecciónalo manualmente en los campos correspondientes."
        )

    await interaction.followup.send(message, ephemeral=True)


# =========================================================
# ARRANQUE
# =========================================================

def get_config():
    # En Railway el token se guarda como variable privada.
    token = os.getenv("DISCORD_TOKEN", "").strip()

    # Tu servidor Santacho FC actual. Se puede reemplazar creando GUILD_ID en Railway.
    guild_raw = os.getenv("GUILD_ID", "1546604546279608420").strip()

    if not token:
        raise SystemExit(
            "Falta DISCORD_TOKEN. En Railway abre Variables y crea DISCORD_TOKEN con el token del bot."
        )

    try:
        guild_id = int(guild_raw)
    except ValueError:
        raise SystemExit("GUILD_ID debe contener solamente números.")

    return token, guild_id


TOKEN, GUILD_ID = get_config()
bot = SantachoBot(GUILD_ID)

bot.tree.add_command(disponibilidad)
bot.tree.add_command(convocatoria)
bot.tree.add_command(resultado)
bot.tree.add_command(paneles)
bot.tree.add_command(organizar)
bot.tree.add_command(jugador)
bot.tree.add_command(sumarstats)
bot.tree.add_command(setstats)
bot.tree.add_command(plantilla)
bot.tree.add_command(tabla)
bot.tree.add_command(alineacion)
bot.tree.add_command(configurarbots)


@bot.event
async def on_ready():
    print("\n" + "=" * 62)
    print(f"🟡⚫ SANTACHO FC RAILWAY conectado como {bot.user}")
    print("=" * 62)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ No encontré el servidor.")
        return

    print(f"Servidor: {guild.name}")

    try:
        if not guild.me.guild_permissions.administrator:
            print("⚠️ Recomendación: dale Administrador al bot.")

        await migrate_names(guild)
        await ensure_roles(guild)
        await ensure_structure(guild)
        await apply_v6_layout(guild)
        await ensure_panels(guild)

        try:
            if guild.name != SERVER_NAME:
                await guild.edit(name=SERVER_NAME)
        except discord.HTTPException:
            pass

        print("\n[6/6] TERMINADO")
        print("✅ Santacho FC V6 quedó configurado y actualizado.")
        print("✅ NO cierres esta ventana si quieres que botones/tickets sigan funcionando.")
        print("✅ Comandos: /disponibilidad /convocatoria /alineacion /resultado /jugador /sumarstats /setstats /plantilla /tabla /paneles /organizar /configurarbots")

    except Exception as exc:
        print(f"\n❌ ERROR: {type(exc).__name__}: {exc}")
        print("Toma una captura y envíamela.")


try:
    bot.run(TOKEN, log_handler=None)
except discord.LoginFailure:
    print("❌ Token inválido.")
