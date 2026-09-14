import asyncio
import importlib.util
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

os.environ["DISCORD_TOKEN"] = "offline-test-token"
spec = importlib.util.spec_from_file_location("santacho_app", "main.py")
app = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app
spec.loader.exec_module(app)


def interaction():
    i = SimpleNamespace()
    i.response = SimpleNamespace(defer=AsyncMock(), send_message=AsyncMock(),
                                 is_done=Mock(return_value=True))
    i.followup = SimpleNamespace(send=AsyncMock())
    i.user = Mock(spec=app.discord.Member)
    i.user.id = 77
    i.user.mention = "<@77>"
    i.channel = Mock(spec=app.discord.TextChannel)
    i.channel.id = 555
    i.channel.topic = "Santacho FC tryout | ticket_user_id:77"
    i.channel.edit = AsyncMock()
    i.channel.delete = AsyncMock()
    i.channel.send = AsyncMock()
    i.message = SimpleNamespace(edit=AsyncMock())
    i.guild = SimpleNamespace(id=app.GUILD_ID, fetch_channel=AsyncMock(return_value=i.channel),
        fetch_member=AsyncMock(), get_member=Mock(return_value=None))
    return i


class Reliability(unittest.IsolatedAsyncioTestCase):
    async def test_all_existing_controls_remain_persistent(self):
        views = [app.TryoutPanelView(), app.PositionPanelView(), app.TicketStaffView(),
                 app.WelcomeView(), app.DirectTryoutView(), app.AvailabilityView()]
        self.assertTrue(all(v.is_persistent() for v in views))
        ids = {item.custom_id for v in views for item in v.children}
        self.assertTrue({"santacho:v3:trial", "santacho:v3:roster", "santacho:v3:reject",
                         "santacho:v3:close", "santacho:dm:private_tryout"} <= ids)

    async def test_staff_controls_acknowledge_before_network(self):
        i = interaction()
        async def fetch_channel(_):
            i.response.defer.assert_awaited_once()
            return i.channel
        i.guild.fetch_channel.side_effect = fetch_channel
        member = SimpleNamespace(roles=[], mention="<@77>")
        i.guild.fetch_member.return_value = member
        role = object()
        member.add_roles = AsyncMock()
        with patch.object(app, "is_staff", return_value=True), patch.object(app, "required_role", AsyncMock(return_value=role)):
            await app.TicketStaffView().trial.callback(i)
        member.add_roles.assert_awaited_once()
        i.followup.send.assert_awaited_once()

    async def test_non_staff_cannot_change_ticket(self):
        i = interaction()
        with patch.object(app, "is_staff", return_value=False):
            await app.TicketStaffView().close.callback(i)
        i.response.send_message.assert_awaited_once()
        i.channel.edit.assert_not_awaited()
        i.channel.delete.assert_not_awaited()

    async def test_close_preserves_channel_and_private_history(self):
        i = interaction()
        private = {"only": "staff"}
        with patch.object(app, "is_staff", return_value=True), patch.object(app, "staff_only_overwrites", return_value=private):
            await app.TicketStaffView().close.callback(i)
        i.channel.delete.assert_not_awaited()
        args = i.channel.edit.await_args.kwargs
        self.assertEqual(args["overwrites"], private)
        self.assertIn("ticket_status:closed", args["topic"])
        self.assertEqual(args["name"], "cerrada-555")

    async def test_archived_ticket_rejects_old_controls(self):
        i = interaction()
        i.channel.topic += " | ticket_status:closed"
        with patch.object(app, "is_staff", return_value=True):
            await app.TicketStaffView().trial.callback(i)
        i.guild.fetch_member.assert_not_awaited()
        self.assertIn("archivado", i.followup.send.await_args.args[0])

    async def test_lock_serializes_and_releases_after_error(self):
        order = []
        async def work(n):
            async with app.operation_lock(("test", 1)):
                order.append(("start", n))
                await asyncio.sleep(0.001)
                order.append(("end", n))
        await asyncio.gather(work(1), work(2))
        self.assertEqual(order, [("start", 1), ("end", 1), ("start", 2), ("end", 2)])
        with self.assertRaises(ValueError):
            async with app.operation_lock(("test", 2)):
                raise ValueError()
        self.assertNotIn(("test", 2), app._operation_locks)

    async def test_stats_search_matches_exact_id_beyond_500_records(self):
        author = object()
        guild = SimpleNamespace(me=author)
        expected = SimpleNamespace(author=author, content='SANTACHO_PLAYER_STAT:12\n{"pj": 9}')
        messages = [SimpleNamespace(author=author, content='SANTACHO_PLAYER_STAT:123\n{"pj": 1}')] * 501 + [expected]
        async def history():
            for m in messages:
                yield m
        channel = SimpleNamespace(history=Mock(return_value=history()))
        with patch.object(app, "get_data_channel", AsyncMock(return_value=channel)):
            found = await app.find_stat_message(guild, 12)
        self.assertIs(found, expected)
        channel.history.assert_called_once_with(limit=None)

    async def test_restart_does_not_reorganize_server(self):
        app.bot.startup_started = False
        app.bot.startup_complete = False
        guild = SimpleNamespace(name="Santacho FC", me=SimpleNamespace(guild_permissions=SimpleNamespace(administrator=True)))
        with patch.dict(os.environ, {"SANTACHO_FULL_SETUP": "0"}), patch.object(app.bot, "get_guild", return_value=guild), patch.object(app, "text_by_name", return_value=None), patch.object(app, "refresh_control_center", AsyncMock()) as refresh, patch.object(app, "audit_guild", return_value=[]), patch.object(app, "migrate_names", AsyncMock()) as migrate:
            await app.on_ready()
            await app.on_ready()
            migrate.assert_not_awaited()
            refresh.assert_awaited_once()
        self.assertTrue(app.bot.startup_complete)

    async def test_new_members_do_not_get_accepted_access(self):
        everyone = object()
        guild = SimpleNamespace(default_role=everyone, me=None)
        with patch.object(app, "role_by_name", return_value=None):
            private = app.accepted_category_overwrites(guild)
            entry = app.onboarding_readonly_overwrites(guild)
        self.assertFalse(private[everyone].view_channel)
        self.assertTrue(entry[everyone].view_channel)
        self.assertFalse(entry[everyone].send_messages)

    async def test_roster_repeat_does_not_announce_again(self):
        i = interaction()
        roster = SimpleNamespace(name=app.ROLE_ROSTER)
        community = SimpleNamespace(name=app.ROLE_COMMUNITY)
        member = SimpleNamespace(roles=[roster, community], mention="<@77>",
                                 add_roles=AsyncMock(), remove_roles=AsyncMock())
        i.guild.fetch_member.return_value = member
        accepted = SimpleNamespace(send=AsyncMock())
        with patch.object(app, "is_staff", return_value=True), patch.object(app, "required_role", AsyncMock(return_value=roster)), patch.object(app, "role_by_name", side_effect=lambda g, n: community if n == app.ROLE_COMMUNITY else None), patch.object(app, "text_by_name", return_value=accepted), patch.object(app, "refresh_roster_panel", AsyncMock()), patch.object(app, "send_official_welcome", AsyncMock()) as welcome:
            await app.TicketStaffView().roster.callback(i)
        welcome.assert_not_awaited()
        accepted.send.assert_not_awaited()
        member.add_roles.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
