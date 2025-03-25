from helper.git_manager import GitManager
from helper.docker_manager import DockerManager


def main():
    docker_manager = DockerManager(
        "gitlab-ci-local",
        "ubuntu:24.04",
        install_dependencies=True
    )

    docker_manager.create_and_configure_container(print_output=True)

    git_manager = GitManager(docker_manager)
    git_manager.initialize_gitflow_repository(print_output=True)

    git_manager.change_branch("develop", print_output=True)

    file_path = "version.txt"
    content = "1.0.0-SNAPSHOT"
    commit_message = "Add version file"
    git_manager.create_file_and_commit(
        file_path,
        content,
        commit_message,
        print_output=True
    )

    command = "cd /tmp/gitlab-pipeline && gitlab-ci-local startRelease"
    result = docker_manager.exec_command(command, print_output=True)

    docker_manager.stop_container()

if __name__ == "__main__":
    main()
