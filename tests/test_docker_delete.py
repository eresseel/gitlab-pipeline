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
    CI_SERVER_HOST: "gitlab.com"
    CI_COMMIT_REF_NAME: "1.0.0"
    CI_PROJECT_NAMESPACE: "foo"
    CI_PROJECT_NAME: "bar"
    CI_PROJECT_NAMESPACE: "dummy"
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
    setup_git_repo.create_file_and_commit('.ci/ci-variables.yml', ci_variables, "Add ci-variables")


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
def test_docker_image_delete(setup_git_repo, setup_docker_container, docker_registry_user, docker_registry_password, docker_registry_url):
    setup_git_repo.initialize_gitflow_repository(reinitialize=True)

    docker_registry = setup_docker_registry()

    setup_git_repo.change_branch('master')

    dockerfile = """
    FROM alpine

    RUN apk add nano
    """.strip()
    setup_git_repo.create_file_and_commit('Dockerfile', dockerfile, "Add Dockerfile")

    setup_git_repo.create_file_and_commit('version.txt', '1.0.0', 'Add version.txt')
    add_gitlab_ci_file(setup_git_repo)
    add_ci_variables_file(setup_git_repo)
    add_gitlab_ci_local_variables(setup_git_repo, docker_registry_user, docker_registry_password, docker_registry_url)

    command = "cd /tmp/gitlab-pipeline && git tag -a 1.0.0 -m \"Set tag\" && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startBuild"
    setup_docker_container.exec_command(command)

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local --volume /var/run/docker.sock:/var/run/docker.sock --network gitlab-ci-local startImageDelete"
    result = setup_docker_container.exec_command(command)

    docker_registry.stop_container()
    assert '[INFO] Docker image delete succeeded for localhost:5000/dummy/bar:1.0.0' in result, f"Expected message not found: {result}"
