#!/usr/bin/env python3
"""Deploys apps as docker containers onto remote server"""

import arg_manager, ssh_client, docker_setup, docker


def main():
    """Main script"""

    args = arg_manager.get_cli_args()
    ssh = ssh_client.ssh_connect(args)
    docker_setup.set_up_docker(ssh)
    microservices = docker.build_apps(ssh, args)
    docker.run_containers(ssh, microservices)
    docker.health_check(ssh, args)
    ssh_client.ssh_close(ssh)

    return


main()
