import sys, subprocess
import json
import paramiko
from flask import Flask, jsonify, request


app = Flask(__name__)


def ssh_connect():

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect('172.16.15.24', username='root', password='Makaveli')

    except:
        print("ERROR: SSH connection failed")
        sys.exit(1)

    print("--- SSH connection successful ---")

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

        print(error_output)

    if (print_stdout):

        for line in stdout_output:
            standard_output += line

        print(standard_output)

    return(stdout_output)


def get_containers(show_all):

    all = " "

    if (show_all):
        all = " -a "

    ssh = ssh_connect()
    command = "docker container ls" + all + "--format '{{.ID}}, {{.Image}}, {{.Status}}'"

    containers = ssh_command(ssh, command, True)

    return(containers)


def containers_to_dict(containers):

    containers = containers.decode("utf-8")
    containers = containers.split('\n')

    containers_list = []
    data = []

    for container in containers:

        if (container != ''):

            container = container.split(', ')
            containers_list.append(container)

    keys = ["HASH", "IMAGE", "UPTIME"]

    for container_list in containers_list:
        dictionary = dict(zip(keys, container_list))
        data.append(dictionary)

    return(data)


@app.route('/containers', methods=['GET'])

def get_all():

    show_all = False
    all = request.args.get("all")

    if (all and all == "true"):
        show_all = True

    containers = get_containers(show_all)
    data = containers_to_dict(containers)

    print(container)
    # print(data)

    return jsonify({'code':200, 'message': 'OK', 'data': containers}),200


@app.route('/container/<id>', methods=['GET'])

def get_one(id):

    return jsonify({'code':200, 'message': 'OK', 'data': "data"}),200


#ERROR ROUTE
@app.errorhandler(404)

def not_found(error):
	return jsonify({'code':404,'message': 'Not Found'}),404


if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5002)
