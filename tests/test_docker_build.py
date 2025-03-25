import os
import pytest
from helper.docker_manager import DockerManager


def add_gitlab_ci_local_variables(setup_git_repo, docker_registry_user, docker_registry_password, docker_registry_url):
    """
    Add .gitlab-ci-local-variables.yml file with GitLab CI local variables.
    """
    gitlab_ci_local_variables = f"""
    DOCKER_REGISTRY_USER: {docker_registry_user}
    DOCKER_REGISTRY_PASSWORD: {docker_registry_password}
    DOCKER_REGISTRY: {docker_registry_url}
    """.strip()
    setup_git_repo.create_file_and_commit('.gitlab-ci-local-variables.yml', gitlab_ci_local_variables, "Add gitlab-ci local variables")


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


def setup_docker_registry():
    """
    Sets up and configures a Docker registry container using DockerManager.
    """
    additional_volumes = [{
        f"{os.getcwd()}/tests/helper/auth": {"bind": "/auth", "mode": "ro"}
    }]

    docker_registry = DockerManager(
        container_name="gitlab-ci-registry",
        container_image="registry:2",
        ports={"5000/tcp": 5000},
        environment={
            "REGISTRY_AUTH": "htpasswd",
            "REGISTRY_AUTH_HTPASSWD_REALM": "Registry Realm",
            "REGISTRY_AUTH_HTPASSWD_PATH": "/auth/htpasswd"
        },
        volumes=additional_volumes,
        install_dependencies=False,
        sleep=False
    )
    docker_registry.create_and_configure_container(print_output=False)
    return docker_registry


@pytest.mark.parametrize('docker_registry_user, docker_registry_password, docker_registry_url', [
    ('foo','bar', 'localhost:5000'),
])
def test_docker_login(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    docker_registry = setup_docker_registry()

    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')

    add_gitlab_ci_local_variables(setup_git_repo, docker_registry_user, docker_registry_password, docker_registry_url)
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    docker_registry.stop_container()
    assert '[INFO] Docker login succeeded' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('docker_registry_user, docker_registry_password, docker_registry_url', [
    ('','', ''),
    ('foo','', ''),
    ('foo','bar', '')
])
def test_not_exists_docker_login_variable(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')

    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert "[ERROR] Required environment variables DOCKER_REGISTRY_USER, DOCKER_REGISTRY_PASSWORD, or DOCKER_REGISTRY are not set" in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('docker_registry_user, docker_registry_password, docker_registry_url', [
    ('foo2','bar', 'localhost:5000'),
    ('foo','bar2', 'localhost:5000'),
    ('foo','bar', 'dummy')
])
def test_invalid_docker_login(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    docker_registry = setup_docker_registry()

    setup_git_repo.change_branch('master')
    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')

    add_gitlab_ci_local_variables(setup_git_repo, docker_registry_user, docker_registry_password, docker_registry_url)
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    assert '[ERROR] Docker login failed' in result, f"Expected message not found: {result}"
    docker_registry.stop_container()


@pytest.mark.parametrize('docker_registry_user, docker_registry_password, docker_registry_url', [
    ('foo','bar', 'localhost:5000'),
])
def test_docker_build_and_push(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    docker_registry = setup_docker_registry()

    setup_git_repo.change_branch('master')

    gitlab_ci_local_variables = f"""
    DOCKER_REGISTRY_USER: {docker_registry_user}
    DOCKER_REGISTRY_PASSWORD: {docker_registry_password}
    DOCKER_REGISTRY: {docker_registry_url}
    CI_SERVER_HOST: "gitlab.com"
    CI_COMMIT_REF_NAME: "1.0.0"
    CI_PROJECT_NAMESPACE: "foo"
    CI_PROJECT_NAME: "bar"
    """.strip()
    setup_git_repo.create_file_and_commit('.gitlab-ci-local-variables.yml', gitlab_ci_local_variables, "Add gitlab-ci local variables")

    dockerfile = """
    FROM alpine

    RUN apk add nano
    """.strip()
    setup_git_repo.create_file_and_commit('Dockerfile', dockerfile, "Add Dockerfile")

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    docker_registry.stop_container()
    assert '[INFO] Docker build succeeded for localhost:5000/foo/bar:1.0.0' in result, f"Expected message not found: {result}"
    assert '[INFO] Docker push succeeded for localhost:5000/foo/bar:1.0.0' in result, f"Expected message not found: {result}"


@pytest.mark.parametrize('docker_registry_user, docker_registry_password, docker_registry_url', [
    ('foo','bar', 'localhost:5000'),
])
def test_failed_docker_build(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    docker_registry = setup_docker_registry()

    setup_git_repo.change_branch('master')

    gitlab_ci_local_variables = f"""
    DOCKER_REGISTRY_USER: {docker_registry_user}
    DOCKER_REGISTRY_PASSWORD: {docker_registry_password}
    DOCKER_REGISTRY: {docker_registry_url}
    CI_SERVER_HOST: "gitlab.com"
    CI_COMMIT_REF_NAME: "1.0.0"
    CI_PROJECT_NAMESPACE: "foo"
    CI_PROJECT_NAME: "bar"
    """.strip()
    setup_git_repo.create_file_and_commit('.gitlab-ci-local-variables.yml', gitlab_ci_local_variables, "Add gitlab-ci local variables")

    dockerfile = """
    FROM alpine

    RUN apk add foo
    """.strip()
    setup_git_repo.create_file_and_commit('Dockerfile', dockerfile, "Add Dockerfile")

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    result = setup_docker_container.exec_command(command)

    docker_registry.stop_container()
    assert '[ERROR] Docker build failed' in result, f"Expected message not found: {result}"
