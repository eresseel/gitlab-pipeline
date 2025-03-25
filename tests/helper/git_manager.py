import shlex

class GitManager:
    repository_path = "/tmp/gitlab-pipeline"

    def __init__(self, docker_manager):
        """
        Initializes the GitManager with a reference
        to a DockerManager instance.
        """
        self.docker_manager = docker_manager

    def initialize_gitflow_repository(self, print_output=False, git_user_name="gitlab-ci-local", git_email="gitlab-ci-local@mycorp.com", reinitialize=False):
        """
        Initializes a Git repository in repository_path with GitFlow,
        copies necessary files, and makes the initial commit.
        """
        gitflow_setup_script = f"""
            git config --global user.name '{git_user_name}'
            git config --global user.email '{git_email}'
            git config --global init.defaultBranch master

            mkdir -p {self.repository_path}
            cd {self.repository_path}
            git init
            cp -R /ws/.ci/ .
            cp -R /ws/ci-src/ .
            cp -R /ws/.gitignore .
            cp -R /ws/.gitlab-ci.yml .
            git add --all
            git commit -am"Add pipelines"
        """

        if reinitialize:
            self.docker_manager.exec_command(f"rm -rf {self.repository_path}", print_output)

        self.docker_manager.exec_command(gitflow_setup_script, print_output)
        self.docker_manager.exec_command(
            f"cd {self.repository_path} && git flow init -d", print_output)

    def create_file_and_commit(
            self, file_path,
            content, commit_message,
            print_output=False):
        """
        Creates a file in the container's Git repository,
        adds it to Git, and commits it.

        :param file_path: Path to the file in the container.
        :param content: Content to write to the file.
        :param commit_message: Commit message for Git.
        """
        file_commands = [
            f'echo "{content}" > {file_path}',
            f'git add {file_path}',
            f'git commit -m "{commit_message}"'
        ]

        for command in file_commands:
            result = self.docker_manager.exec_command(
                f"cd {self.repository_path} && {command}",
                print_output
            )

            if "error" in result.lower():
                print(f"Error occurred while executing command: {command}")
                break

        return result

    def create_branch(self, branch_name, print_output=False):
        """
        Creates a new branch with the given name in the
        Git repository in the container.

        :param branch_name: Name of the branch to create.
        """
        command = f"cd {self.repository_path} && git checkout -b {branch_name}"
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while creating branch: {branch_name}")

        return result

    def create_feature_branch(self, branch_name, print_output=False):
        """
        Creates a new feature branch with the given name in the
        Git repository in the container.

        :param branch_name: Name of the branch to create.
        """
        command = f"cd {self.repository_path} && git flow feature start {branch_name}"
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while creating branch: {branch_name}")

        return result

    def create_release_branch(self, branch_name, print_output=False):
        """
        Creates a new release branch with the given name in the
        Git repository in the container.

        :param branch_name: Name of the branch to create.
        """
        command = f"cd {self.repository_path} && git flow release start {branch_name}"
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while creating branch: {branch_name}")

        return result

    def create_hotfix_branch(self, branch_name, print_output=False):
        """
        Creates a new hotfix branch with the given name in the
        Git repository in the container.

        :param branch_name: Name of the branch to create.
        """
        command = f"cd {self.repository_path} && git flow hotfix start {branch_name}"
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while creating branch: {branch_name}")

        return result

    def create_tag(self, tag, tag_message, print_output=False):
        """
        Creates a new hotfix branch with the given name in the
        Git repository in the container.

        :param tag: Name of the branch to create.
        :param tag_message: Comment a tag message.
        """
        command = f"cd {self.repository_path} && git tag -a {tag} -m \"{tag_message}\""
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while creating tag: {tag}")

        return result

    def change_branch(self, branch_name, print_output=False):
        """
        Switches to an existing branch in the Git repository in the container.

        :param branch_name: Name of the branch to switch to.
        """
        command = f"cd {self.repository_path} && git checkout {branch_name}"
        result = self.docker_manager.exec_command(command, print_output)

        if "error" in result.lower():
            print(f"Error occurred while switching to branch: {branch_name}")

        return result
