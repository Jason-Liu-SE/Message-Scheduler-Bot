import pytest

from helpers.message_scheduler import mongo_utils as ms_mongo
from helpers.ticket_bot import mongo_utils as ticket_mongo
from tests.fakes.discord import FakeGuild, FakeMember


@pytest.mark.integration
class TestTicketMongoUtils:
    async def test_register_and_update_user(self, fake_db):
        member1 = FakeMember(44, "Pat")
        member2 = FakeMember(12, "Tim")
        await ticket_mongo.register_user_with_db(member1)
        user = await ticket_mongo.get_user_object(44)
        assert user["tickets"] == 0
        assert user["incoming_trades"] == []

        await ticket_mongo.register_user_with_db(member1)
        assert ticket_mongo.PymongoManager.count_in_collection("tickets", {}) == 1

        await ticket_mongo.register_user_with_db(member2)
        assert ticket_mongo.PymongoManager.count_in_collection("tickets", {}) == 2

        await ticket_mongo.update_user_object(44, {"tickets": 9})
        assert (await ticket_mongo.get_user_object(44))["tickets"] == 9

    async def test_ranked_users_and_rewards(self, fake_db):
        fake_db.seed(
            "tickets",
            [
                {"_id": 1, "tickets": 2},
                {"_id": 2, "tickets": 8},
            ],
        )
        ranked = await ticket_mongo.get_ranked_user_objects("tickets", "DESC")
        assert list(ranked.keys()) == [2, 1]

        from bson import ObjectId

        reward_id = ObjectId()
        await ticket_mongo.update_reward_object(
            reward_id, {"name": "Hat", "cost": 3, "stock": 1}
        )
        assert await ticket_mongo.count_rewards({}) == 1
        reward = await ticket_mongo.get_reward_object(reward_id)
        assert reward["name"] == "Hat"
        await ticket_mongo.delete_reward_object(reward_id)
        assert await ticket_mongo.count_rewards({}) == 0

    async def test_bulk_user_helpers_update_and_create_records(self, fake_db):
        await ticket_mongo.create_user_objects([1, 2])
        await ticket_mongo.update_user_objects({1: {"tickets": 7}, 2: {"tickets": 4}})

        users = await ticket_mongo.get_user_objects([1, 2])

        assert users[1]["tickets"] == 7
        assert users[2]["tickets"] == 4

    async def test_reward_query_helper_applies_sort_skip_and_limit(self, fake_db):
        fake_db.seed(
            "rewards",
            [
                {"_id": 1, "name": "Alpha"},
                {"_id": 2, "name": "Beta"},
                {"_id": 3, "name": "Gamma"},
            ],
        )

        rewards = await ticket_mongo.get_many_reward_objects(
            {}, sort_field="name", skip=1, limit=1
        )

        assert list(rewards) == [2]


@pytest.mark.integration
class TestSchedulerMongoUtils:
    async def test_register_server_and_schedule_posts(self, fake_db):
        guild = FakeGuild(guild_id=77)
        await ms_mongo.register_server_with_db(guild)
        message = await ms_mongo.get_message_object(77)
        assert message["message"] == ""

        from bson import ObjectId

        post_id = ObjectId()
        await ms_mongo.update_schedule(
            post_id, {"server_id": 77, "message": "hi", "time": None}
        )
        posts = await ms_mongo.get_schedule_by_server_id(77)
        assert post_id in posts
        fetched = await ms_mongo.get_post_by_id(post_id)
        assert fetched["message"] == "hi"
        await ms_mongo.delete_server_posts(77)
        assert await ms_mongo.get_schedule_by_server_id(77) == {}

    async def test_delete_post_and_update_message_object(self, fake_db):
        await ms_mongo.update_message_object(77, {"message": "draft"})
        assert (await ms_mongo.get_message_object(77))["message"] == "draft"

        await ms_mongo.update_schedule(12, {"server_id": 77, "message": "post"})
        await ms_mongo.delete_post_by_id(12)

        assert await ms_mongo.get_post_by_id(12) is None
