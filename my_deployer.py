import sys
import time
import argparse
import paramiko
from termcolor import colored

APPS = ['msContainers', 'msDaisy', 'all']
USERS = ['root']
EXPECTED_DOCKER_VERSION = "18.09"

LOCAL_WORK_DIR = "./"
LOCAL_SCRIPT_PATH = LOCAL_WORK_DIR + "install_or_update_docker.sh"

REMOTE_WORK_DIR = "/home/steeve/Documents/my_deployer/"
REMOTE_SCRIPT_PATH = REMOTE_WORK_DIR + "install_or_update_docker.sh"


def get_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--server")
    parser.add_argument("--user", choices = USERS, required=True)
    parser.add_argument("--microservice", nargs='*', choices = APPS, required=True)

    if len(sys.argv) < 2:

        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()

    if not (args.microservice):
        parser.error('Please choose at least one --microservice to deploy')

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
        print(colored("ERROR: SSH connection to " + server + " failed", 'red'))
        sys.exit(1)

    print(colored("--- SSH connection to " + server + " successful ---", 'yellow'))

    return(ssh)


def ssh_command(ssh, command, print_stdout):

    stdin, stdout, stderr = ssh.exec_command(command)
    stdout_output = stdout.readlines()
    stderr_output = stderr.readlines()

    standard_output = ""
    error_output = ""

    if (stderr_output):

        for line in stderr_output:
            error_output += line

        print(colored(error_output, 'red'))

    if (print_stdout):

        for line in stdout_output:
            standard_output += line

        print(standard_output)

    return(stdout_output)


def ssh_close(ssh):

    ssh.close()
    print(colored("--- SSH connection closed ---", 'yellow'))

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


def install_or_update_docker(ssh, callback):

    local_path = LOCAL_SCRIPT_PATH
    remote_path = REMOTE_SCRIPT_PATH

    if (callback == "install"):
        message = "--- Installing Docker-ce "

    elif (callback == "update"):
        message = "--- Updating Docker to "

    message += EXPECTED_DOCKER_VERSION + "..."
    print(colored(message, 'yellow'))

    ftp_client = ssh.open_sftp()
    ftp_client.put(local_path, remote_path)

    command = "chmod 755 " + remote_path + "&& sh " + remote_path
    command_output = ssh_command(ssh, command, True)

    ftp_client.remove(remote_path)
    ftp_client.close()

    print(colored("Done", 'yellow'))

    return


def set_up_docker(ssh):

    print(colored("--- Checking current Docker version...", 'yellow'))

    docker_version = get_docker_version(ssh)

    if (docker_version == ""):

        print(colored("Docker not found on remote host", 'yellow'))
        install_or_update_docker(ssh, "install")

    elif (docker_version != "" and docker_version != EXPECTED_DOCKER_VERSION):

        print(colored("Current Docker version on remote host is " + docker_version, 'yellow'))
        print(colored("Let's update it to Docker " + EXPECTED_DOCKER_VERSION, 'yellow'))

        install_or_update_docker(ssh, "update")

    else:
        print(colored("Docker is up-to-date, proceeding", 'yellow'))

    return


def build_apps(ssh, args):

    print(colored("--- Building services...", 'yellow'))

    ftp_client = ssh.open_sftp()
    microservices = args.microservice

    if ("all" in args.microservice):

        microservices = APPS
        microservices.remove('all')

    for microservice in microservices:

        local_dockerfile_path = LOCAL_WORK_DIR + microservice + "/Dockerfile"
        remote_dockerfile_path = REMOTE_WORK_DIR + microservice

        local_app_path = LOCAL_WORK_DIR + microservice + "/app.py"
        remote_app_path = REMOTE_WORK_DIR + microservice + "/app.py"

        try:
            ftp_client.chdir(remote_dockerfile_path)

        except IOError:
            ftp_client.mkdir(remote_dockerfile_path)

        remote_dockerfile_path = remote_dockerfile_path + "/Dockerfile"
        ftp_client.put(local_dockerfile_path, remote_dockerfile_path)
        ftp_client.put(local_app_path, remote_app_path)

        print(colored("- Building " + microservice + "...\n", 'yellow'))

        build_image(ssh, microservice)

    ftp_client.close()

    print(colored("Done", 'yellow'))

    return(microservices)


def build_image(ssh, microservice):

    remote_dockerfile_path = REMOTE_WORK_DIR + microservice
    microservice = microservice.lower()

    command = "cd " + remote_dockerfile_path + " && docker build -t " + microservice + ":latest ."
    ssh_command(ssh, command, True)

    return


def get_container_id(ssh, microservice):

    print(colored("--- Checking current version for " + microservice + "...", 'yellow'))

    command = "docker ps -qf" + " 'name=" + microservice + "'"
    container_id = ssh_command(ssh, command, False)

    return(container_id)


def remove_container(ssh, microservice):

    print(colored("--- Removing pre-existing container...", 'yellow'))

    command = "docker rm -f " + microservice
    ssh_command(ssh, command, True)

    return


def stop_container(ssh, microservice, container_id):

    print(colored("--- Stopping " + microservice + "...", 'yellow'))

    container_id = container_id[0]
    command = "docker stop " + container_id
    ssh_command(ssh, command, True)

    return


def run_container(ssh, microservice):

    print(colored("--- Running new version of service...", 'yellow'))

    command = "docker run -d --name " + microservice + " --network=host " + microservice + ":latest"
    run_output = ssh_command(ssh, command, True)

    return(run_output)


def start_container(ssh, container_id):

    container_id = container_id[0]

    print(colored("--- Restoring container " + container_id, 'yellow'))

    command = "docker start " + container_id
    ssh_command(ssh, command, True)

    return


def run_containers(ssh, microservices):

    for microservice in microservices:

        microservice = microservice.lower()
        container_id = get_container_id(ssh, microservice)

        if not (container_id):

            print(colored("No running container for " + microservice, 'yellow'))

            remove_container(ssh, microservice)
            run_container(ssh, microservice)

        else:

            stop_container(ssh, microservice, container_id)
            remove_container(ssh, microservice)
            run_container(ssh, microservice)

            time.sleep(0.5)
            new_container_id = get_container_id(ssh, microservice)

            if not (new_container_id):
                start_container(ssh, container_id)

    return


def main():

    args = get_cli_args()
    ssh = ssh_connect(args)
    set_up_docker(ssh)
    microservices = build_apps(ssh, args)
    run_containers(ssh, microservices)
    ssh_close(ssh)

    return


main()
