from cli import main


def test_list_command(capsys) -> None:
    assert main(["list"]) == 0

