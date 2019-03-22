#!/usr/bin/env python3
"""Gets Docker environment ready"""

from termcolor import colored

import ssh_client, globals


def get_docker_version(ssh):
    """Checks Docker version if any"""

    docker_version = ""

    command = "docker ps"
    command_output = ssh_client.ssh_command(ssh, command, False)

    if (command_output != []):

        command = "docker --version"
        command_output = ssh_client.ssh_command(ssh, command, False)

        for line in command_output:
            docker_version += line

        docker_version = docker_version.split(",")[0]
        docker_version = docker_version.split("Docker version ")[1]
        docker_version = docker_version.split(".")[0] + "." + docker_version.split(".")[1]

    return(docker_version)


def install_or_update_docker(ssh, callback):
    """Installs or updates Docker"""

    local_path = globals.LOCAL_SCRIPT_PATH
    remote_path = globals.REMOTE_SCRIPT_PATH

    if (callback == "install"):
        message = "--- Installing Docker-ce "

    elif (callback == "update"):
        message = "\n--- Updating Docker to "

    message += globals.EXPECTED_DOCKER_VERSION + "..."
    print(colored(message, 'yellow'))

    ftp_client = ssh.open_sftp()
    ftp_client.put(local_path, remote_path)

    command = "chmod 755 " + remote_path + "&& sh " + remote_path
    command_output = ssh_client.ssh_command(ssh, command, True)

    ftp_client.remove(remote_path)
    ftp_client.close()

    print(colored("Done\n", 'yellow'))

    return


def set_up_docker(ssh):
    """Main Docker environment setup"""

    print(colored("\n--- Checking current Docker version...", 'yellow'))

    docker_version = get_docker_version(ssh)

    if (docker_version == ""):

        print(colored("\nDocker not found on remote host", 'yellow'))
        install_or_update_docker(ssh, "install")

    elif (docker_version != "" and docker_version != globals.EXPECTED_DOCKER_VERSION):

        print(colored("Current Docker version on remote host is " + docker_version, 'yellow'))
        print(colored("Updating to Docker " + globals.EXPECTED_DOCKER_VERSION, 'yellow'))

        install_or_update_docker(ssh, "update")

    else:
        print(colored("\nDocker is up-to-date, proceeding", 'green'))

    return
