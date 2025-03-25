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


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.1-SNAPSHOT', 'Add version.txt file')
])
def test_create_release_branch(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: develop' in result, f"Expected message not found: {result}"
    assert 'Switched to a new branch \'release/1.0.1\'' in result, f"Expected message not found: {result}"
    assert 'Set release version to 1.0.1' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.1-SNAPSHOT', 'Add version.txt file')
])
def test_if_exists_release_branch_then_broken_pipeline(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_release_branch('1.0.1')
    setup_git_repo.change_branch('develop')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: develop' in result, f"Expected message not found: {result}"
    assert 'fatal: a branch named \'release/1.0.1\' already exists' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.0', 'Add version.txt file')
])
def test_create_and_commit_hotfix_branch(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startHotfix"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: master' in result, f"Expected message not found: {result}"
    assert 'Switched to a new branch \'hotfix/1.0.1\'' in result, f"Expected message not found: {result}"
    assert 'Set hotfix version to 1.0.1' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.1', 'Add version.txt file')
])
def test_if_exists_hotfix_branch_then_broken_pipeline(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_hotfix_branch('1.0.2')
    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startHotfix"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: master' in result, f"Expected message not found: {result}"
    assert 'fatal: a branch named \'hotfix/1.0.2\' already exists' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.0', 'Add version.txt file')
])
def test_setting_release_tag(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startReleaseTag"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: master' in result, f"Expected message not found: {result}"
    assert 'Set release tag version to 1.0.0' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message', [
    ('version.txt', '1.0.0', 'Add version.txt file')
])
def test_if_exists_release_tag_then_broken_pipeline(setup_git_repo, setup_docker_container, file_path, content, commit_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_tag('1.0.0', 'Add tag')
    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startReleaseTag"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: master' in result, f"Expected message not found: {result}"
    assert '[ERROR] Release tag 1.0.0 already exists' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('file_path, content, commit_message, success_message', [
    ('version.txt', '1.2.4', 'Add version.txt file', 'Set next development version to 1.3.0'),
    ('version.txt', '1.5.0', 'Add version.txt file', 'Set next development version to 1.6.0')
])
def test_setting_next_version_on_develop(setup_git_repo, setup_docker_container, file_path, content, commit_message, success_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_branch('develop')
    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit(file_path, content, commit_message)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startNextVersion"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] Current branch: master' in result, f"Expected message not found: {result}"
    assert success_message in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('source_branch, target_branch, success_message', [
    ('feature/DEVOPS-12', 'develop', '[INFO] Feature branch is being merged into develop. Merge request can proceed.'),
    ('release/1.2.0', 'master', '[INFO] Release branch is being merged into master/main. Merge request can proceed.'),
    ('hotfix/1.5.5', 'main', '[INFO] Hotfix branch is being merged into develop/master/main. Merge request can proceed.'),
])
def test_merge_requests(setup_git_repo, setup_docker_container, source_branch, target_branch, success_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_branch('source_branch')
    setup_git_repo.change_branch('master')

    gitlab_ci_local_variables = f"""
    CI_MERGE_REQUEST_SOURCE_BRANCH_NAME: {source_branch}
    CI_MERGE_REQUEST_TARGET_BRANCH_NAME: {target_branch}
    """
    setup_git_repo.create_file_and_commit('.gitlab-ci-local-variables.yml', gitlab_ci_local_variables, "Add local variables")
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startMRTest"
    result = setup_docker_container.exec_command(command)

    assert f"Source branch: {source_branch}" in result, f"Expected message not found: {result}"
    assert f"Target branch: {target_branch}" in result, f"Expected message not found: {result}"
    assert success_message in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('source_branch, target_branch, error_message', [
    ('feature/DEVOPS-12', 'master', '[ERROR] Feature branches can only be merged into the develop branch.'),
    ('release/1.2.0', 'develop', '[ERROR] Release branches can only be merged into the master or main branch.'),
    ('hotfix/1.5.5', 'feature/DEVOPS-15', '[ERROR] Hotfix branches can only be merged into the develop, master, or main branch.'),
    ('alma/1.5.5', 'develop', '[ERROR] Invalid branch name pattern.')
])
def test_invalid_merge_requests(setup_git_repo, setup_docker_container, source_branch, target_branch, error_message):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_branch('source_branch')
    setup_git_repo.change_branch('master')

    gitlab_ci_local_variables = f"""
    CI_MERGE_REQUEST_SOURCE_BRANCH_NAME: {source_branch}
    CI_MERGE_REQUEST_TARGET_BRANCH_NAME: {target_branch}
    """
    setup_git_repo.create_file_and_commit('.gitlab-ci-local-variables.yml', gitlab_ci_local_variables, "Add local variables")
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startMRTest"
    result = setup_docker_container.exec_command(command)

    assert f"[INFO] Source branch: {source_branch}" in result, f"Expected message not found: {result}"
    assert f"[INFO] Target branch: {target_branch}" in result, f"Expected message not found: {result}"
    assert error_message in result, f"Expected message not found: {result}"


def test_only_version_txt_has_been_modified(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    add_ci_variables_file(setup_git_repo)
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0-SNAPSHOT', 'Add version.txt')

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert f"[ERROR] Only version.txt has been modified" in result, f"Expected message not found: {result}"
