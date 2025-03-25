from helper.docker_manager import DockerManager


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


def test_dockerignore_file_exists(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')

    dockerfile = """
    FROM alpine

    RUN apk add nano
    ADD . /
    """.strip()
    setup_git_repo.create_file_and_commit('Dockerfile', dockerfile, "Add Dockerfile")

    setup_git_repo.create_file_and_commit('.dockerignore', "foobar", "Add .dockerignore")
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] The .dockerignore file exists. Appending lines to it' in result, f"Expected message not found: {result}"


def test_dockerignore_file_not_exists(setup_git_repo, setup_docker_container):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')

    dockerfile = """
    FROM alpine

    RUN apk add nano
    ADD . /
    """.strip()
    setup_git_repo.create_file_and_commit('Dockerfile', dockerfile, "Add Dockerfile")

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert '[INFO] The .dockerignore file does not exist. Creating it' in result, f"Expected message not found: {result}"
