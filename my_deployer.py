import sys
import argparse
import paramiko


EXPECTED_DOCKER_VERSION = "18.09"
LOCAL_SCRIPT_PATH = "./install_or_update_docker.sh"
REMOTE_SCRIPT_PATH = "/home/steeve/install_or_update_docker.sh"


def get_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--server")
    parser.add_argument("--user", choices=['root'])
    parser.add_argument("--microservice")

    if len(sys.argv) < 2:

        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()

    return(args)


def ssh_connect(args):

    server = args.server
    user = args.user
    password = "Makaveli"

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(server, username=user, password=password)

    except:
        print("ERROR: SSH connection to " + server + " failed")
        sys.exit(1)

    print ("SSH connection to " + server + " successful")

    return(ssh)


def ssh_command(ssh, command, print_output):

    stdin, stdout, stderr = ssh.exec_command(command)
    command_output = stdout.readlines()

    terminal_output = ""

    if (print_output):

        for line in command_output:
            terminal_output += line

        print(terminal_output)

    return(command_output)


def ssh_close(ssh):

    ssh.close()
    print("SSH connection closed")

    return


def get_docker_version(ssh):

    docker_version = ""

    command = "docker ps"
    command_output = ssh_command(ssh, command, False)

    if (command_output != []):

        command = "docker --version"
        command_output = ssh_command(ssh, command, False)

        for line in command_output:
            docker_version += line

        docker_version = docker_version.split(",")[0]
        docker_version = docker_version.split("Docker version ")[1]
        docker_version = docker_version.split(".")[0] + "." + docker_version.split(".")[1]

    return(docker_version)


def set_up_docker(ssh):

    docker_version = get_docker_version(ssh)

    if (docker_version == ""):

        print("Docker not found on remote host. Let's install it!")
        install_or_update_docker(ssh, "install")

    elif (docker_version != "" and docker_version != EXPECTED_DOCKER_VERSION):

        print("Current Docker version on remote host is " + docker_version)
        print("Let's update it to Docker " + EXPECTED_DOCKER_VERSION)
        install_or_update_docker(ssh, "update")

    else:
        print("Docker is up-to-date, proceeding")

    return


def install_or_update_docker(ssh, callback):

    local_path = LOCAL_SCRIPT_PATH
    remote_path = REMOTE_SCRIPT_PATH

    if (callback == "install"):
        message = "Installing Docker-ce "

    elif (callback == "update"):
        message = "Updating Docker to "

    message += EXPECTED_DOCKER_VERSION + "..."
    print(message)

    ftp_client = ssh.open_sftp()
    ftp_client.put(local_path, remote_path)

    command = "chmod 755 " + remote_path + "&& sh " + remote_path
    command_output = ssh_command(ssh, command, True)

    ftp_client.remove(remote_path)
    ftp_client.close()

    return


def main():

    args = get_cli_args()
    ssh = ssh_connect(args)
    set_up_docker(ssh)
    ssh_close(ssh)

    return


main()
