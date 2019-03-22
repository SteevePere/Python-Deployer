#!/usr/bin/env python3
"""Provides Docker methods to deploy apps"""

import time
from termcolor import colored

# custom modules
import ssh_client
import globals


def build_apps(ssh, args):
    """Builds images on remote server"""

    print(colored("\n--- Building services...\n", 'yellow'))
    ftp_client = ssh.open_sftp()
    microservices = args.microservice  # retrieving from cli

    if ("all" in args.microservice):

        microservices = globals.APPS
        microservices.remove('all')  # getting final app array

    for microservice in microservices:
        # pathes
        local_dockerfile_path = globals.LOCAL_WORK_DIR + microservice + "/Dockerfile"
        remote_dockerfile_path = globals.REMOTE_WORK_DIR + microservice
        local_app_path = globals.LOCAL_WORK_DIR + microservice + "/app.py"
        remote_app_path = globals.REMOTE_WORK_DIR + microservice + "/app.py"

        try:
            ftp_client.chdir(remote_dockerfile_path)  # trying to move to Dockerfile dir to see if exists

        except IOError:
            ftp_client.mkdir(remote_dockerfile_path)  # if does not exist, create it

        remote_dockerfile_path = remote_dockerfile_path + "/Dockerfile"
        ftp_client.put(local_dockerfile_path, remote_dockerfile_path)  # moving Dockerfile
        ftp_client.put(local_app_path, remote_app_path)  # moving app
        print(colored("\t- Building " + microservice + "...\n", 'yellow'))

        build_image(ssh, microservice)

    ftp_client.close()

    print(colored("Done\n", 'yellow'))

    return(microservices)


def build_image(ssh, microservice):
    """Builds a docker image"""

    remote_dockerfile_path = globals.REMOTE_WORK_DIR + microservice
    microservice = microservice.lower()  # to lowercase for Docker

    command = "cd " + remote_dockerfile_path + " && docker build -t " + microservice + ":latest ."  # moving to Dockerfile dir and building
    ssh_client.ssh_command(ssh, command, True)

    return


def get_container_id(ssh, microservice):
    """Gets a container's id from its name"""

    command = "docker ps -qf" + " 'name=" + microservice + "'"  # id from name
    container_id = ssh_client.ssh_command(ssh, command, False)

    return(container_id)


def remove_container(ssh, microservice):
    """Removes a Docker container"""

    print(colored("--- Removing pre-existing container...", 'yellow'))

    command = "docker rm -f " + microservice
    ssh_client.ssh_command(ssh, command, True)

    return


def stop_container(ssh, microservice, container_id):
    """Stops a Docker container"""

    print(colored("--- Stopping previous version of " + microservice + "...", 'yellow'))

    container_id = container_id[0]  # getting from list
    command = "docker stop " + container_id
    ssh_client.ssh_command(ssh, command, True)

    return


def run_container(ssh, microservice):
    """Runs a Docker container"""

    print(colored("--- Running new version of service...", 'yellow'))

    command = "docker run -d --name " + microservice + " --network=host " + microservice + ":latest"  # binding ports to host network
    run_output = ssh_client.ssh_command(ssh, command, True)

    return(run_output)


def start_container(ssh, container_id):
    """Starts a Docker container"""

    print(colored("--- Starting container " + container_id, 'yellow'))

    command = "docker start " + container_id
    ssh_client.ssh_command(ssh, command, True)

    return


def restart_container(ssh, container_id):
    """Retarts a Docker container"""

    print(colored("--- Restarting container " + container_id, 'yellow'))

    command = "docker restart " + container_id
    ssh_client.ssh_command(ssh, command, True)

    return


def rename_container(ssh, old_name, new_name):
    """Renames a Docker container"""

    remove_container(ssh, new_name)  # to avoid conflicts
    command = "docker rename " + old_name + " " + new_name
    ssh_client.ssh_command(ssh, command, True)

    return


def run_containers(ssh, microservices):
    """Main container deployment logic"""

    for microservice in microservices:

        microservice = microservice.lower()  # to lowercase for Docker
        container_id = get_container_id(ssh, microservice)

        if not (container_id):  # if container is not running, we'll run one from new image

            print(colored("No running container for " + microservice, 'yellow'))
            remove_container(ssh, microservice)  # removing any pre-existing idle containers to avoid conflicts
            run_container(ssh, microservice)

        else:  # container is already running

            stop_container(ssh, microservice, container_id)
            backup_container = microservice + "_backup"  # keeping as backup in case new one fails
            rename_container(ssh, microservice, backup_container)
            run_container(ssh, microservice)
            time.sleep(0.5)  # sleeping here so that we can get the id (otherwise too fast)
            new_container_id = get_container_id(ssh, microservice)

            if not (new_container_id):  # new run was unsuccessful

                print(colored("New container failed, restoring from previous version...", 'red'))
                start_container(ssh, backup_container)
                rename_container(ssh, backup_container, microservice)  # so that running container remains named after app

    return


def health_check(ssh, args):
    """Checks container's health and runs appropriate actions"""

    if (args.healthcheck):  # healthcheck is optional

        microservices = args.microservice

        if ("all" in args.microservice):
            microservices = globals.APPS  # "all" was previously removed

        for microservice in microservices:

            microservice = microservice.lower()  # to lowercase for Docker

            print(colored("\n--- Checking health of " + microservice + "...", 'yellow'))

            command = "docker inspect " + microservice + " --format '{{.State.Health.Status}}'"
            health = ssh_client.ssh_command(ssh, command, False)
            health = str(health[0].rstrip().strip())  # parsing return

            if (health != "healthy" and health != "starting"): # container needs a restart

                print(colored("Container is " + health, 'red'))
                restart_container(ssh, microservice)

            else:
                print(colored("Container is " + health, 'green'))

    return
