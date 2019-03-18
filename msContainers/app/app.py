import subprocess
import json
from flask import Flask, jsonify, request


app = Flask(__name__)


def get_containers(show_all):

    command = ["docker", "container", "ls", "--format", "{{.ID}}, {{.Image}}, {{.Status}}"]

    if (show_all):
        command[3:3] = ["-a"]

    containers = subprocess.check_output(command)

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

    return jsonify({'code':200, 'message': 'OK', 'data': data}),200


@app.route('/container/<id>', methods=['GET'])

def get_one(id):

    return jsonify({'code':200, 'message': 'OK', 'data': "data"}),200


#ERROR ROUTE
@app.errorhandler(404)

def not_found(error):
	return jsonify({'code':404,'message': 'Not Found'}),404


if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5002)
