#!/usr/bin/env python3
"""All globals variables live here"""

APPS = ['msContainers', 'msDaisy', 'all']  # list of apps to deploy
LOG_FILE = 'my_deployer.log'  # log file
EXPECTED_DOCKER_VERSION = "18.09"  # Docker version expected on remote server
LOCAL_WORK_DIR = "./"  # current dir
REMOTE_WORK_DIR = "/home/steeve/Documents/my_deployer/"  # remote server work dir
LOCAL_SCRIPT_PATH = LOCAL_WORK_DIR + "install_or_update_docker.sh"  # Docker install or update script
REMOTE_SCRIPT_PATH = REMOTE_WORK_DIR + "install_or_update_docker.sh"  # Docker install or update script remote location
USERS = ['root']  # remote server user
REMOTE_SSH_PASSWORD = "Makaveli"
