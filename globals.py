#!/usr/bin/env python3
"""All globals variables live here"""

LOG_FILE = 'my_deployer.log'

EXPECTED_DOCKER_VERSION = "18.09"
LOCAL_WORK_DIR = "./"
REMOTE_WORK_DIR = "/home/steeve/Documents/my_deployer/"
LOCAL_SCRIPT_PATH = LOCAL_WORK_DIR + "install_or_update_docker.sh"
REMOTE_SCRIPT_PATH = REMOTE_WORK_DIR + "install_or_update_docker.sh"

APPS = ['msContainers', 'msDaisy', 'all']
USERS = ['root']
