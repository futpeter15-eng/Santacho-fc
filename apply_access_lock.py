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

        print(f"Aplicando acceso restringido estricto en: {guild.name}")

        # Conserva toda la lógica existente y después fuerza una regla simple:
        # @everyone solo puede ver REGLAS y HACER PRUEBAS.
        await main.enforce_permissions(guild)

        allowed_names = {main.CH_RULES, main.CH_TRY}
        info_cat = main.category_by_name(guild, main.CAT_INFO)

        # Categorías: ocultas por defecto; EMPIEZA AQUÍ visible para que aparezcan los dos canales públicos.
        for category in guild.categories:
            overwrites = dict(category.overwrites)
            current = overwrites.get(guild.default_role, discord.PermissionOverwrite())
            current.view_channel = (category == info_cat)
            overwrites[guild.default_role] = current
            try:
                await category.edit(overwrites=overwrites, reason="Santacho FC: acceso mínimo para nuevos")
            except discord.HTTPException as exc:
                print(f"WARN categoria {category.name}: {exc}")

        # Canales: preserva todos los overwrites de roles/miembros y cambia solo @everyone.
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                continue

            overwrites = dict(channel.overwrites)
            current = overwrites.get(guild.default_role, discord.PermissionOverwrite())
            current.view_channel = channel.name in allowed_names
            overwrites[guild.default_role] = current

            try:
                await channel.edit(overwrites=overwrites, reason="Santacho FC: nuevos solo ven reglas y hacer-pruebas")
            except discord.HTTPException as exc:
                print(f"WARN canal {channel.name}: {exc}")

        visible = [
            ch.name
            for ch in guild.channels
            if not isinstance(ch, discord.CategoryChannel)
            and ch.permissions_for(guild.default_role).view_channel
        ]
        extra = [name for name in visible if name not in allowed_names]

        print("Canales visibles para @everyone:", ", ".join(visible) or "ninguno")
        print("Canales extra visibles:", ", ".join(extra) or "ninguno")
        print("Acceso restringido aplicado sin modificar pruebas, tickets ni aceptación.")
        await self.close()


async def run():
    intents = discord.Intents.default()
    intents.guilds = True
    client = AccessLockClient(intents=intents)
    await client.start(main.TOKEN)


if __name__ == "__main__":
    asyncio.run(run())
