from uuid import UUID, uuid4

from sololedger import Activity


class TestActivity:
    def test_create_activity_with_explicit_id(self):
        activity_id = uuid4()
        activity = Activity(id=activity_id, name="Developer")

        assert activity.id == activity_id
        assert activity.name == "Developer"

    def test_create_activity_with_factory(self):
        activity = Activity.create(name="Guitar Teacher")

        assert isinstance(activity.id, UUID)
        assert activity.name == "Guitar Teacher"

    def test_activities_with_same_id_are_equal(self):
        activity_id = uuid4()
        activity1 = Activity(id=activity_id, name="Developer")
        activity2 = Activity(id=activity_id, name="Developer")

        assert activity1 == activity2

    def test_activities_with_different_ids_are_not_equal(self):
        activity1 = Activity.create(name="Developer")
        activity2 = Activity.create(name="Developer")

        assert activity1 != activity2

    def test_activity_is_immutable(self):
        activity = Activity.create(name="Developer")

        try:
            activity.name = "New Name"
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass
