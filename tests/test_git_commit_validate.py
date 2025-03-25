def add_gitlab_ci_file(setup_git_repo):
    """
    Add .gitlab-ci.yml file for GitLab CI pipeline configuration.
    """
    gitlab_ci = """
    ---
    include:
    - local: '.ci/build.yml'

    stages:
    - build
    - delete
    """.strip()
    setup_git_repo.create_file_and_commit('.gitlab-ci.yml', gitlab_ci, "Add gitlab-ci")


def add_ci_variables_file(setup_git_repo):
    """
    Add .ci/ci-variables.sh file with environment variables for CI.
    """
    ci_variables = """
variables:
  DOCKER_IMAGE_PREFIX: "docker.io/library"
  BUILD_BASE_IMAGE: "docker:27.4.0-rc.2-dind-alpine3.20"
before_script:
  - export GIT_USER_EMAIL="gitlab-ci-local@mycorp.com"
  - export GIT_USER_NAME="gitlab-ci-local"
    """.strip()
    setup_git_repo.create_file_and_commit('.ci/ci-variables.yml', ci_variables, "Add ci-variables into master")


def test_git_commit_validate(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert "[INFO] The commit email does match" in result, f"Expected message not found: {result}"
    assert "[INFO] Tag type is valid and found" in result, f"Expected message not found: {result}"
    assert "[INFO] Commit is on master or main branch" in result, f"Expected message not found: {result}"


def test_git_if_commit_email_does_not_match(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True, git_user_name="gitlab-ci-local", git_email="gitlab-ci-local@mycorp.com")

    setup_git_repo.change_branch('master')

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    ci_variables = """
variables:
  DOCKER_IMAGE_PREFIX: "docker.io/library"
  BUILD_BASE_IMAGE: "docker:27.4.0-rc.2-dind-alpine3.20"
before_script:
  - export GIT_USER_EMAIL="foo@bar.com"
  - export GIT_USER_NAME="gitlab-ci-local"
    """.strip()
    commit_message = "Add ci-variables into master"
    setup_git_repo.create_file_and_commit('.ci/ci-variables.yml', ci_variables, commit_message)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert "[ERROR] The commit email does not match with another email address" in result, f"Expected message not found: {result}"


def test_if_tag_invalid_type(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 2024080-1122 -m \"Set tag\" && gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert "[ERROR] Tag type is invalid" in result, f"Expected message not found: {result}"


def test_if_commit_is_not_on_master_branch(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.1 -m \"Set tag\" && gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert "[INFO] Commit is on master or main branch" in result, f"Expected message not found: {result}"
