from uuid import UUID, uuid4

import pytest

from sololedger import Client


class TestClientCreation:
    def test_create_with_factory(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        assert isinstance(client.id, UUID)
        assert client.first_name == "John"
        assert client.last_name == "Doe"
        assert client.email == "john@acme.com"
        assert client.phone is None
        assert client.description is None

    def test_create_with_all_fields(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            phone="+1234567890",
            description="Important client",
        )

        assert client.first_name == "John"
        assert client.last_name == "Doe"
        assert client.email == "john@acme.com"
        assert client.phone == "+1234567890"
        assert client.description == "Important client"

    def test_create_with_explicit_id(self):
        client_id = uuid4()
        client = Client(
            id=client_id,
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        assert client.id == client_id
        assert client.first_name == "John"
        assert client.last_name == "Doe"
        assert client.email == "john@acme.com"

    def test_full_name_property(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        assert client.full_name == "John Doe"


class TestClientEquality:
    def test_clients_with_same_values_are_equal(self):
        client_id = uuid4()
        client1 = Client(
            id=client_id,
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )
        client2 = Client(
            id=client_id,
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        assert client1 == client2

    def test_clients_with_different_ids_are_not_equal(self):
        client1 = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )
        client2 = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        assert client1 != client2


class TestClientImmutability:
    def test_client_first_name_is_immutable(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        with pytest.raises(AttributeError):
            client.first_name = "Jane"

    def test_client_last_name_is_immutable(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        with pytest.raises(AttributeError):
            client.last_name = "Smith"

    def test_client_email_is_immutable(self):
        client = Client.create(
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
        )

        with pytest.raises(AttributeError):
            client.email = "new@acme.com"
