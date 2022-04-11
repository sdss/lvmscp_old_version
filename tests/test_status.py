"""
@pytest.mark.asyncio
async def test_status(actor: ScpActor, lvmieb):

    print(actor.parser_args)
    assert actor.parser_args[0]["sp1"].name == "sp"

    command = await lvmieb.invoke_mock_command("ping")
    await command
    assert command.status.did_succeed

    assert command.replies[-1].message["text"] == "Pong."

    a = clu.testing.MockReplyList(lvmieb).parse_reply("pong")
    print(f"this is {a}")

    command = await actor.invoke_mock_command("labtemp")
    await command
    assert command.status.did_succeed

    assert command.replies[-1].message == "Pong."

"""
