import pytest

from lvmscp.actor.actor import lvmscp as ScpActor


@pytest.mark.asyncio
async def test_actor(actor: ScpActor):

    assert actor


@pytest.mark.asyncio
async def test_ping(actor: ScpActor):

    command = await actor.invoke_mock_command("ping")
    await command

    assert command.status.did_succeed
    assert len(command.replies) == 2
    assert command.replies[1].message["text"] == "Pong."


@pytest.mark.asyncio
async def test_actor_no_config():

    with pytest.raises(RuntimeError):
        ScpActor.from_config(None)
