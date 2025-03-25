import pytest
from helper.docker_manager import DockerManager
from helper.git_manager import GitManager


@pytest.fixture(scope="module")
def setup_docker_container():
    docker_manager = DockerManager(
        container_name="gitlab-ci-local",
        container_image="ubuntu:24.04",
        install_dependencies=True
    )
    docker_manager.create_and_configure_container(print_output=False)

    yield docker_manager

    docker_manager.stop_container()
    docker_manager.delete_network()


@pytest.fixture()
def setup_git_repo(setup_docker_container):
    docker_manager = setup_docker_container
    git_manager = GitManager(docker_manager)

    git_manager.initialize_gitflow_repository(print_output=False)

    yield git_manager
