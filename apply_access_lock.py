import asyncio
import discord
import main


class AccessLockClient(discord.Client):
    async def on_ready(self):
        guild = self.get_guild(main.GUILD_ID)
        if guild is None:
            print(f"ERROR: no se encontró el servidor {main.GUILD_ID}")
            await self.close()
            return

        print(f"Aplicando acceso restringido en: {guild.name}")
        await main.enforce_permissions(guild)

        visible = [
            ch.name
            for ch in guild.channels
            if not isinstance(ch, discord.CategoryChannel)
            and ch.permissions_for(guild.default_role).view_channel
        ]
        allowed = {main.CH_RULES, main.CH_TRY}
        extra = [name for name in visible if name not in allowed]

        print("Canales visibles para @everyone:", ", ".join(visible) or "ninguno")
        print("Canales extra visibles:", ", ".join(extra) or "ninguno")
        print("Acceso restringido aplicado sin modificar el flujo de pruebas/aceptación.")
        await self.close()


async def run():
    intents = discord.Intents.default()
    intents.guilds = True
    client = AccessLockClient(intents=intents)
    await client.start(main.TOKEN)


if __name__ == "__main__":
    asyncio.run(run())
