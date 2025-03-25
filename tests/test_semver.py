import pytest

def add_ci_variables_file(setup_git_repo):
    """
    Add .ci/ci-variables.sh file with environment variables for CI.
    """
    ci_variables = """
variables:
  DOCKER_IMAGE_PREFIX: "docker.io/library"
  GITFLOW_BASE_IMAGE: "docker:27.4.0-rc.2-dind-alpine3.20"
before_script:
  - export GIT_USER_EMAIL="gitlab-ci-local@mycorp.com"
  - export GIT_USER_NAME="gitlab-ci-local"
    """.strip()
    setup_git_repo.create_file_and_commit('.ci/ci-variables.yml', ci_variables, "Add ci-variables")


@pytest.mark.parametrize('file_path, content, commit_message, error_message', [
    ('README.md', '1.0.0-SNAPSHOT', 'Add README.md file', '[ERROR] version.txt does not exist.'),
    ('version.txt', 'alma-SNAPSOT', 'Add version.txt file', '[ERROR] develop branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT'),
    ('version.txt', 'alma', 'Add version.txt file', '[ERROR] develop branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT'),
    ('version.txt', '-SNAPSHOT', 'Add version.txt file', '[ERROR] develop branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT'),
    ('version.txt', '1.0.0-SNAPSHOT', 'Add version.txt file', '[INFO] Version is valid for develop branch: 1.0.0-SNAPSHOT')
])
def test_semver_settings(setup_git_repo, setup_docker_container, file_path, content, commit_message, error_message):
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert error_message in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('branch, file_path, content, commit_message, success_message', [
    ('master', 'version.txt', '1.0.0', 'Add version.txt file', '[INFO] Version is valid for master branch: 1.0.0'),
    ('master', 'version.txt', '1.0.1', 'Add version.txt file', '[INFO] Version is valid for master branch: 1.0.1'),
    ('develop', 'version.txt', '1.0.0-SNAPSHOT', 'Add version.txt file', '[INFO] Version is valid for develop branch: 1.0.0-SNAPSHOT'),
    ('develop', 'version.txt', '1.0.1-SNAPSHOT', 'Add version.txt file', '[INFO] Version is valid for develop branch: 1.0.1-SNAPSHOT'),
    ('feature/test', 'version.txt', '1.0.0-SNAPSHOT', 'Add version.txt file', '[INFO] Version is valid for feature/test branch: 1.0.0-SNAPSHOT'),
    ('release/1.0.0', 'version.txt', '1.0.0', 'Add version.txt file', '[INFO] Version is valid for release/1.0.0 branch: 1.0.0'),
    ('hotfix/1.0.1', 'version.txt', '1.0.1', 'Add version.txt file', '[INFO] Version is valid for hotfix/1.0.1 branch: 1.0.1')
])
def test_semver_valid_branch_settings(setup_git_repo, setup_docker_container, branch, file_path, content, commit_message, success_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_branch(branch)
    setup_git_repo.change_branch(branch)

    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert success_message in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('branch, file_path, content, commit_message, error_message', [
    ('master', 'version.txt', '1.0.0-SNAPSHOT', 'Add version.txt file', '[ERROR] master branch should have a release version (e.g., 1.0.0).'),
    ('develop', 'version.txt', '1.0.0', 'Add version.txt file', '[ERROR] develop branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT).'),
    ('feature/test', 'version.txt', '1.0.0', 'Add version.txt file', '[ERROR] feature/test branch should have a -SNAPSHOT version (e.g., 1.0.0-SNAPSHOT).'),
    ('release/1.0.0', 'version.txt', '1.0.0-SNAPSHOT', 'Add version.txt file', '[ERROR] release/1.0.0 branch should have a release version (e.g., 1.0.0).'),
    ('hotfix/1.0.1', 'version.txt', '1.0.1-SNAPSHOT', 'Add version.txt file', '[ERROR] hotfix/1.0.1 branch should have a release version (e.g., 1.0.0).'),
    ('foo', 'version.txt', '1.0.1-SNAPSHOT', 'Add version.txt file', '[ERROR] Unrecognized branch foo.')
])
def test_semver_invalid_branch_settings(setup_git_repo, setup_docker_container, branch, file_path, content, commit_message, error_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_branch(branch)
    setup_git_repo.change_branch(branch)

    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert error_message in result, f"Expected message not found: {result}"
