"""Collection of tests around cookiecutter's command-line interface."""

import json
import os
import sys

import pytest
from click.testing import CliRunner

from cookiecutter.utils.paths import rmtree
from cookiecutter.__main__ import main
from cookiecutter.main import cookiecutter


@pytest.fixture(scope='session')
def cli_runner():
    """Fixture that returns a helper function to run the cookiecutter cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run cookiecutter cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.fixture
def remove_fake_project_dir(request):
    """Remove the fake project directory created during the tests."""

    def fin_remove_fake_project_dir():
        if os.path.isdir('fake-project'):
            rmtree('fake-project')

    request.addfinalizer(fin_remove_fake_project_dir)


@pytest.fixture
def make_fake_project_dir(request):
    """Create a fake project to be overwritten in the according tests."""
    os.makedirs('fake-project')


@pytest.fixture(params=['-V', '--version'])
def version_cli_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Verify correct version output by `cookiecutter` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('Cookiecutter')


@pytest.mark.usefixtures('make_fake_project_dir', 'remove_fake_project_dir')
def test_cli_error_on_existing_output_directory(monkeypatch, cli_runner):
    """Test cli invocation without `overwrite-if-exists` fail if dir exist."""
    test_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..')
    monkeypatch.chdir(test_dir)

    result = cli_runner('tests/fixtures/fake-repo-pre/', '--no-input')
    assert result.exit_code != 0
    result_output = result.output.split('\n')[-2]
    expected_error_msg = 'Error: "fake-project" directory already exists'
    assert result_output == expected_error_msg
    # assert result.output == expected_error_msg


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli(cli_runner):
    """Test cli invocation work without flags if directory not exist."""
    result = cli_runner('tests/fixtures/fake-repo-pre/', '--no-input')
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Fake Project**' in f.read()


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_verbose(cli_runner):
    """Test cli invocation display log if called with `verbose` flag."""
    result = cli_runner('tests/fixtures/fake-repo-pre/', '--no-input', '-v')
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Fake Project**' in f.read()


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_replay(mocker, cli_runner):
    """Test cli invocation display log with `verbose` and `replay` flags."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--replay', '-v')

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=True,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_replay_file(mocker, cli_runner):
    """Test cli invocation correctly pass --replay-file option."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--replay-file', '~/custom-replay-file', '-v')

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        replay='~/custom-replay-file',
        context_file=None,
        context_key=None,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_exit_on_noinput_and_replay(mocker, cli_runner):
    """Test cli invocation fail if both `no-input` and `replay` flags passed."""
    mock_cookiecutter = mocker.patch(
        'cookiecutter.cli.cli_parser.cookiecutter', side_effect=cookiecutter
    )

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--no-input', '--replay', '-v')

    assert result.exit_code == 1

    expected_error_msg = (
        "You can not use both replay and no_input or extra_context at the same time."
    )

    assert expected_error_msg in result.output

    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        True,
        context_file=None,
        context_key=None,
        replay=True,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.fixture(params=['-f', '--overwrite-if-exists'])
def overwrite_cli_flag(request):
    """Pytest fixture return all `overwrite-if-exists` invocation options."""
    return request.param


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_run_cookiecutter_on_overwrite_if_exists_and_replay(
    mocker, cli_runner, overwrite_cli_flag
):
    """Test cli invocation with `overwrite-if-exists` and `replay` flags."""
    mock_cookiecutter = mocker.patch(
        'cookiecutter.cli.cli_parser.cookiecutter', side_effect=cookiecutter
    )

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--replay', '-v', overwrite_cli_flag)

    assert result.exit_code == 0

    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=True,
        overwrite_if_exists=True,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_overwrite_if_exists_when_output_dir_does_not_exist(
    cli_runner, overwrite_cli_flag
):
    """Test cli invocation with `overwrite-if-exists` and `no-input` flags.

    Case when output dir not exist.
    """
    result = cli_runner(
        'tests/fixtures/fake-repo-pre/', '--no-input', overwrite_cli_flag
    )

    assert result.exit_code == 0
    assert os.path.isdir('fake-project')


@pytest.mark.usefixtures('make_fake_project_dir', 'remove_fake_project_dir')
def test_cli_overwrite_if_exists_when_output_dir_exists(cli_runner, overwrite_cli_flag):
    """Test cli invocation with `overwrite-if-exists` and `no-input` flags.

    Case when output dir already exist.
    """
    result = cli_runner(
        'tests/fixtures/fake-repo-pre/', '--no-input', overwrite_cli_flag
    )
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')


@pytest.fixture(params=['-o', '--output-dir'])
def output_dir_flag(request):
    """Pytest fixture return all output-dir invocation options."""
    return request.param


@pytest.fixture
def output_dir(tmpdir):
    """Pytest fixture return `output_dir` argument as string."""
    return str(tmpdir.mkdir('output'))


def test_cli_output_dir(mocker, cli_runner, output_dir_flag, output_dir):
    """Test cli invocation with `output-dir` flag changes output directory."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, output_dir_flag, output_dir)

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=False,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_dir,
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.fixture(params=['-h', '--help', 'help'])
def help_cli_flag(request):
    """Pytest fixture return all help invocation options."""
    return request.param


def test_cli_help(cli_runner, help_cli_flag):
    """Test cli invocation display help message with `help` flag."""
    result = cli_runner(help_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith('Usage')


@pytest.fixture
def user_config_path(tmpdir):
    """Pytest fixture return `user_config` argument as string."""
    return str(tmpdir.join('tests/config.yaml'))


def test_user_config(mocker, cli_runner, user_config_path):
    """Test cli invocation works with `config-file` option."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--config-file', user_config_path)

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=False,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=user_config_path,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


def test_default_user_config_overwrite(mocker, cli_runner, user_config_path):
    """Test cli invocation ignores `config-file` if `default-config` passed."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(
        template_path, '--config-file', user_config_path, '--default-config',
    )

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=False,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=user_config_path,
        default_config=True,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


def test_default_user_config(mocker, cli_runner):
    """Test cli invocation accepts `default-config` flag correctly."""
    mock_cookiecutter = mocker.patch('cookiecutter.cli.cli_parser.cookiecutter')

    template_path = 'tests/fixtures/fake-repo-pre/'
    result = cli_runner(template_path, '--default-config')

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        context_file=None,
        context_key=None,
        replay=False,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir='.',
        config_file=None,
        default_config=True,
        extra_context=None,
        password=None,
        directory=None,
        accept_hooks=True,
    )


@pytest.mark.skipif(
    sys.version_info[0] == 3 and sys.version_info[1] == 6 and sys.version_info[2] == 1,
    reason="Outdated pypy3 version on Travis CI/CD with wrong OrderedDict syntax.",
)
def test_echo_undefined_variable_error(monkeypatch, tmpdir, cli_runner):
    """Cli invocation return error if variable undefined in template."""
    cwd = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
    monkeypatch.chdir(cwd)

    output_dir = str(tmpdir.mkdir('output'))
    template_path = 'undefined-variable/file-name'

    result = cli_runner(
        '--no-input', '--default-config', '--output-dir', output_dir, template_path,
    )

    assert result.exit_code == 1

    error = "Unable to create file '{{cookiecutter.foobar}}'"
    assert error in result.output

    message = (
        "Error message: 'collections.OrderedDict object' has no attribute 'foobar'"
    )
    assert message in result.output

    context = {
        'cookiecutter': {
            'github_username': 'hackebrot',
            'project_slug': 'testproject',
            '_template': template_path,
            '_output_dir': output_dir,
        }
    }
    context_str = json.dumps(context, indent=4, sort_keys=True)
    assert context_str in result.output


def test_echo_unknown_extension_error(tmpdir, cli_runner):
    """Cli return error if extension incorrectly defined in template."""
    output_dir = str(tmpdir.mkdir('output'))
    template_path = 'tests/fixtures/test-extensions/unknown/'

    result = cli_runner(
        '--no-input', '--default-config', '--output-dir', output_dir, template_path,
    )

    assert result.exit_code == 1

    assert 'Unable to load extension: ' in result.output


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_extra_context(cli_runner):
    """Cli invocation replace content if called with replacement pairs."""
    result = cli_runner(
        'tests/fixtures/fake-repo-pre/', '--no-input', '-v', 'project_name=Awesomez',
    )
    assert result.exit_code == 0
    assert os.path.isdir('fake-project')
    with open(os.path.join('fake-project', 'README.rst')) as f:
        assert 'Project name: **Awesomez**' in f.read()


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_cli_extra_context_invalid_format(cli_runner):
    """Cli invocation raise error if called with unknown argument."""
    result = cli_runner(
        'tests/fixtures/fake-repo-pre/',
        '--no-input',
        '-v',
        'ExtraContextWithNoEqualsSoInvalid',
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for '[EXTRA_CONTEXT]...'" in result.output
    assert 'should contain items of the form key=value' in result.output


@pytest.fixture
def debug_file(tmpdir):
    """Pytest fixture return `debug_file` argument as path object."""
    return tmpdir.join('fake-repo.log')


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_debug_file_non_verbose(cli_runner, debug_file):
    """Test cli invocation writes log to `debug-file` if flag enabled.

    Case for normal log output.
    """
    assert not debug_file.exists()

    result = cli_runner(
        '--no-input', '--debug-file', str(debug_file), 'tests/fixtures/fake-repo-pre/',
    )
    assert result.exit_code == 0

    assert debug_file.exists()

    context_log = (
        "DEBUG cookiecutter.main: context_file is "
        "tests/fixtures/fake-repo-pre/cookiecutter.json"
    )
    assert context_log in debug_file.readlines(cr=False)
    assert context_log not in result.output


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_debug_file_verbose(cli_runner, debug_file):
    """Test cli invocation writes log to `debug-file` if flag enabled.

    Case for verbose log output.
    """
    assert not debug_file.exists()

    result = cli_runner(
        '--verbose',
        '--no-input',
        '--debug-file',
        str(debug_file),
        'tests/fixtures/fake-repo-pre/',
    )
    assert result.exit_code == 0

    assert debug_file.exists()

    context_log = (
        "DEBUG cookiecutter.main: context_file is "
        "tests/fixtures/fake-repo-pre/cookiecutter.json"
    )
    assert context_log in debug_file.readlines(cr=False)
    assert context_log in result.output


@pytest.mark.usefixtures('make_fake_project_dir', 'remove_fake_project_dir')
def test_debug_list_installed_templates(cli_runner, debug_file, user_config_path):
    """Verify --list-installed command correct invocation."""
    fake_template_dir = os.path.dirname(os.path.abspath('fake-project'))
    os.makedirs(os.path.dirname(user_config_path))
    with open(user_config_path, 'w') as config_file:
        config_file.write('cookiecutters_dir: "%s"' % fake_template_dir)
    open(os.path.join('fake-project', 'cookiecutter.json'), 'w').write('{}')

    result = cli_runner(
        '--list-installed', '--config-file', user_config_path, str(debug_file),
    )

    assert "1 installed templates:" in result.output
    assert result.exit_code == 0


def test_debug_list_installed_templates_failure(
    cli_runner, debug_file, user_config_path
):
    """Verify --list-installed command error on invocation."""
    os.makedirs(os.path.dirname(user_config_path))
    with open(user_config_path, 'w') as config_file:
        config_file.write('cookiecutters_dir: "/notarealplace/"')

    result = cli_runner(
        '--list-installed', '--config-file', user_config_path, str(debug_file)
    )

    assert "Error: Cannot list installed templates." in result.output
    assert result.exit_code == -1


@pytest.mark.usefixtures('remove_fake_project_dir')
def test_directory_repo(cli_runner):
    """Test cli invocation works with `directory` option."""
    result = cli_runner(
        'tests/fixtures/fake-repo-dir/', '--no-input', '-v', '--directory=my-dir',
    )
    assert result.exit_code == 0
    assert os.path.isdir("fake-project")
    with open(os.path.join("fake-project", "README.rst")) as f:
        assert "Project name: **Fake Project**" in f.read()


cli_accept_hook_arg_testdata = [
    ("--accept-hooks=yes", None, True),
    ("--accept-hooks=no", None, False),
    ("--accept-hooks=ask", "yes", True),
    ("--accept-hooks=ask", "no", False),
]


@pytest.mark.parametrize(
    "accept_hooks_arg,user_input,expected", cli_accept_hook_arg_testdata
)
def test_cli_accept_hooks(
    mocker,
    cli_runner,
    output_dir_flag,
    output_dir,
    accept_hooks_arg,
    user_input,
    expected,
):
    """Test cli invocation works with `accept-hooks` option."""
    mock_cookiecutter = mocker.patch("cookiecutter.cli.cli_parser.cookiecutter")

    template_path = "tests/fixtures/fake-repo-pre/"
    result = cli_runner(
        template_path, output_dir_flag, output_dir, accept_hooks_arg, input=user_input
    )

    assert result.exit_code == 0
    mock_cookiecutter.assert_called_once_with(
        template_path,
        None,
        False,
        replay=False,
        context_file=None,
        context_key=None,
        overwrite_if_exists=False,
        output_dir=output_dir,
        config_file=None,
        default_config=False,
        extra_context=None,
        password=None,
        directory=None,
        skip_if_file_exists=False,
        accept_hooks=expected,
    )