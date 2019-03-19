import sys
import argparse
import paramiko

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
        print("ERROR: SSH connection to " + server + " failed")
        sys.exit(1)

    print ("--- SSH connection to " + server + " successful ---")

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
    print("--- SSH connection closed ---")

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
    print(message)

    ftp_client = ssh.open_sftp()
    ftp_client.put(local_path, remote_path)

    command = "chmod 755 " + remote_path + "&& sh " + remote_path
    command_output = ssh_command(ssh, command, True)

    ftp_client.remove(remote_path)
    ftp_client.close()

    print("Done")

    return


def set_up_docker(ssh):

    print("--- Checking current Docker version...")

    docker_version = get_docker_version(ssh)

    if (docker_version == ""):

        print("Docker not found on remote host")
        install_or_update_docker(ssh, "install")

    elif (docker_version != "" and docker_version != EXPECTED_DOCKER_VERSION):

        print("Current Docker version on remote host is " + docker_version)
        print("Let's update it to Docker " + EXPECTED_DOCKER_VERSION)
        install_or_update_docker(ssh, "update")

    else:
        print("Docker is up-to-date, proceeding")

    return


def build_apps(ssh, args):

    print("--- Building services...")

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

        print("- Building " + microservice + "...\n")
        build_image(ssh, microservice)

    ftp_client.close()

    print("Done")

    return(microservices)


def build_image(ssh, microservice):

    remote_dockerfile_path = REMOTE_WORK_DIR + microservice
    microservice = microservice.lower()

    command = "cd " + remote_dockerfile_path + " && docker build -t " + microservice + ":latest ."
    ssh_command(ssh, command, True)

    return


def run_containers(ssh, microservices):

    for microservice in microservices:

        print("--- Checking existing version for " + microservice + "...")

        command = "docker ps -qf" + " 'name=" + microservice + "'"
        container_id = ssh_command(ssh, command, True)

        if not (container_id):
            print("No running container for " + microservice)
            # run container from build_image
        else:
            print("--- Stopping " + microservice + "...")

            command = "docker stop " + container_id
            ssh_command(ssh, command, True)

            command = "docker run --name " + microservice + " --network=host " + microservice + ":latest"
            run_output = ssh_command(ssh, command, True)
            print(run_output)

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
