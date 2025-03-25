import os
import docker


class DockerManager:
    def __init__(self, container_name="gitlab-ci-local",
                 container_image="ubuntu:24.04",
                 ports=None,
                 environment=None,
                 volumes=None,
                 install_dependencies=False,
                 sleep=True
                ):
        """
        Initializes the DockerManager with container configuration.
        """
        self.client = docker.from_env()
        self.container_name = container_name
        self.container_image = container_image
        self.current_directory = os.getcwd()
        self.install_dependencies = install_dependencies
        self.sleep = sleep

        self.volumes = {
            self.current_directory: {'bind': '/ws', 'mode': 'ro'},
            '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}
        }

        if volumes:
            for volume in volumes:
                if isinstance(volume, dict):
                    self.volumes.update(volume)
                elif isinstance(volume, str):
                    self.volumes[volume] = {'bind': volume, 'mode': 'rw'}

        self.ports = ports if ports else {}
        self.environment = environment if environment else {}
        self.bash_script = """
            apt-get update
            apt-get install -y wget curl git git-flow rsync
            wget -qO- https://get.docker.com | bash
            wget -O /etc/apt/sources.list.d/gitlab-ci-local.sources \
                https://gitlab-ci-local-ppa.firecow.dk/gitlab-ci-local.sources
            apt-get update
            apt-get install -y gitlab-ci-local
        """

    def __run_container(self):
        """
        Runs the container with a default sleep command.
        """
        self.ensure_network_exists('gitlab-ci-local')
        command = "sleep infinity" if self.sleep else None

        container = self.client.containers.run(
            self.container_image,
            command=command,
            detach=True,
            stdin_open=True,
            tty=True,
            auto_remove=False,
            volumes=self.volumes,
            working_dir='/ws',
            network='gitlab-ci-local',
            name=self.container_name,
            ports=self.ports,
            environment=self.environment
        )

    def exec_command(self, command, print_output=False, container_name=None):
        """
        Executes a command in the running container,
        optionally printing logs in real time.

        :param command: The command to execute in the container.
        :param print_output: If True, print the output in real time.
            If False, only return the output.
        :param container_name: The name of the container to execute the command in.
            If None, use self.container_name.
        :return: The full output of the command as a string.
        """
        try:
            # If a specific container name is provided, use it; otherwise, default to self.container_name
            target_container = container_name if container_name else self.container_name

            # Prepare the command to execute
            command = f"bash -c '{command}'"
            exec_instance = self.client.api.exec_create(
                target_container,
                command,
                tty=True,
                stdin=True
            )

            # Execute the command and stream the output
            output_stream = self.client.api.exec_start(
                exec_instance,
                stream=True
            )

            output = ""

            for chunk in output_stream:
                decoded_chunk = chunk.decode("utf-8")
                output += decoded_chunk

                if print_output:
                    print(decoded_chunk, end="")

            return output

        except Exception as e:
            error_message = f"Error occurred while executing the command: {e}"

            if print_output:
                print(error_message)

            return error_message

    def stop_container(self, container_name=None):
        """
        Stops the specified container and delete.
        If no container_name is provided, it does nothing regarding the network deletion.

        :param container_name: Optional name of the container to stop.
        """
        try:
            target_container_name = container_name if container_name else self.container_name

            # Get the target container
            container = self.client.containers.get(target_container_name)

            # Stop and remove the container
            container.stop()
            print(f"Container ({target_container_name}) stopped.")

            container.remove()
            print(f"Container ({target_container_name}) removed.")

        except Exception as e:
            print(f"Error occurred while stopping the container ({target_container_name}): {e}")

    def create_and_configure_container(self, print_output=False):
        """
        Creates the container and runs the setup script.
        """
        # Run container
        self.__run_container()

        if print_output:
            print(f"Container is created: {self.container_name}")

        # Execute the setup bash script if install_dependencies is True
        if self.install_dependencies:
            self.exec_command(self.bash_script, print_output)

    def ensure_network_exists(self, network_name="gitlab-ci-local"):
        """
        Ensures that a Docker network with the given name exists. If not, it creates the network.
        """
        try:
            # Check if the network already exists
            networks = self.client.networks.list(names=[network_name])
            if not networks:
                # Create the network if it does not exist
                self.client.networks.create(network_name, driver="bridge")
                print(f"Network '{network_name}' has been created.")
        except Exception as e:
            print(f"Error while ensuring network '{network_name}': {e}")

    def delete_network(self, network_name="gitlab-ci-local"):
        """
        :param network_name: Name of the Docker network to delete after stopping the container.
        """
        try:
            # Check if the network exists before trying to delete it
            network = self.client.networks.list(names=[network_name])
            if network:
                self.client.networks.get(network[0].id).remove()
                print(f"Network ({network_name}) deleted.")
            else:
                print(f"Network ({network_name}) does not exist or is already deleted.")

        except Exception as e:
            print(f"Error occurred while stopping the container ({container_name}): {e}")
