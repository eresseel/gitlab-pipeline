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


def test_git_email(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0-SNAPSHOT', 'Add version.txt')
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert "[INFO] Email: gitlab-ci-local@mycorp.com" in result, f"Expected message not found: {result}"


def test_git_user_name(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0-SNAPSHOT', 'Add version.txt')
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = setup_docker_container.exec_command(command)

    assert "[INFO] User: gitlab-ci-local" in result, f"Expected message not found: {result}"
