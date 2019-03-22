"""Remote Docker API"""

import sys, subprocess
import json
import paramiko
from flask import Flask, jsonify, request


app = Flask(__name__)
HOST = '192.168.0.38'
USERNAME = 'root'
PASSWORD = 'Makaveli'
KEYS_ALL = ["HASH", "IMAGE", "UPTIME"]
KEYS_ONE = ["LONG_HASH", "IMAGE", "UPTIME", "VOLUMES", "PORTS"]


def ssh_connect():
    """Connects to remote server via SSH"""

    ssh = paramiko.SSHClient()  # initialize SSH client
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)

    except:
        print("ERROR: SSH connection failed")
        sys.exit(1)

    print("--- SSH connection successful ---")

    return(ssh)


def ssh_command(ssh, command, print_stdout):
    """Sends Unix commands to remote server via SSH"""

    stdin, stdout, stderr = ssh.exec_command(command)
    stdout_output = stdout.readlines()  # retrieving standard output
    stderr_output = stderr.readlines()  # retrieving error output

    standard_output = ""
    error_output = ""

    if (stderr_output):

        for line in stderr_output:
            error_output += line

        print(error_output)

    if (print_stdout):  # boolean passed to toggle standard output printout

        for line in stdout_output:
            standard_output += line

        print(standard_output)

    return(stdout_output)


def get_container(id):
    """Gets container info from its id"""

    ssh = ssh_connect()
    command = "docker inspect " + id + " --format '{{.Id}}, {{.Image}}, {{.State.StartedAt}}, {{.Mounts}}, {{.NetworkSettings.Ports}}'"  # gets info
    container_info = ssh_command(ssh, command, False)

    return(container_info)


def get_containers(show_all):
    """Gets all containers info"""

    all = " "

    if (show_all):
        all = " -a "  # to add to command in oder to list all containers

    ssh = ssh_connect()
    command = "docker container ls" + all + "--format '{{.ID}}, {{.Image}}, {{.Status}}'"
    containers = ssh_command(ssh, command, False)

    return(containers)


def get_version(data):
    """Gets image version"""

    for container in data:

        image = container["IMAGE"]
        image_and_version = image.split(':')  # separating image from tag
        image = image_and_version[0]

        if (len(image_and_version) > 1):  # if tag exists
            version = image_and_version[1]
        else:
            version = "latest"  # default tag

        container["IMAGE"] = image  # inserting into dict
        container["VERSION"] = version # inserting into dict

    return(data)


def containers_to_dict(containers, one_or_all):
    """Parses docker ps output"""

    containers_list = []
    data = []
    keys = KEYS_ONE

    if (one_or_all is "all"):
        keys = KEYS_ALL  # different info for get container routes

    for container in containers:

        if (container != ''):

            container = container.split('\n')
            container = str(container[0])
            container = container.split(', ')
            containers_list.append(container)

    for container_list in containers_list:
        dictionary = dict(zip(keys, container_list))  # matching keys to values
        data.append(dictionary)

    if (one_or_all is "all"):
        data = get_version(data)  # getting version

    return(data)

# --- ROUTES

#GET ALL
@app.route('/containers', methods=['GET'])

def get_all():
    """Returns all containers"""

    show_all = False
    all = request.args.get("all")

    if (all and all == "true"):
        show_all = True

    containers = get_containers(show_all)
    data = containers_to_dict(containers, "all")

    return jsonify({'code':200, 'message': 'OK', 'data': data}),200


#GET ONE
@app.route('/container/<id>', methods=['GET'])

def get_one(id):
    """Returns one container"""

    containers_list = []
    data = []
    container = get_container(id)

    if (container == ['\n']):
	       return jsonify({'code':404,'message': 'Not Found'}),404

    data = containers_to_dict(container, "one")

    return jsonify({'code':200, 'message': 'OK', 'data': data}),200


#404
@app.errorhandler(404)

def not_found(error):
    """404 output"""

    return jsonify({'code':404,'message': 'Not Found'}),404


if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5002)
