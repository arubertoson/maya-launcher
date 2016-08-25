
from click.testing import CliRunner

from mayalauncher import cli


def test_mayalauncher():
    runner = CliRunner()
    result = runner.invoke(cli.cli)
    print(repr(result.output))
    print(repr(result.exit_code))

    assert result.output == 'hello\n'
    assert result.exit_code == 0


if __name__ == '__main__':
    test_mayalauncher()
