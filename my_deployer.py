#!/usr/bin/env python3
"""Deploys apps as docker containers onto remote server"""

# custom modules
import arg_manager
import ssh_client
import docker_setup
import docker


def main():
    """Main script"""

    args = arg_manager.get_cli_args()  # retrieving cli args
    ssh = ssh_client.ssh_connect(args)  # establishing ssh link
    docker_setup.set_up_docker(ssh)  # making sure Docker is set up correctly
    microservices = docker.build_apps(ssh, args)  # building images
    docker.run_containers(ssh, microservices)  # running containers from images
    docker.health_check(ssh, args)  # checking health
    ssh_client.ssh_close(ssh)  # closing ssh link

    return


main()
