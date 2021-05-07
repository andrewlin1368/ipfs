import hashlib
import json
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request
from fs import FileServer

filesystem = FileServer()


class Blockchain:
    def __init__(self):
        self.data = []
        self.chain = []
        self.fat = []
        self.nodes = set()
        self.new_block(previous_hash='0')
        self.update_block()
        self.create_nodes(address='http://127.0.0.1:5000')
        self.create_nodes(address='http://127.0.0.1:5001')
        self.create_nodes(address='http://127.0.0.1:5002')
        self.create_nodes(address='http://127.0.0.1:5003')

    def create_nodes(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid')

    def update_block(self):
        self.data = filesystem.get_data()
        for i in self.data:
            if i[1] != -2:
                self.fat.append(i[1])
        self.new_fat_log()

    def new_request(self, data, location, sender_port):
        self.data = filesystem.get_data()
        next_location = self.data[location][1]
        self.data[location] = [data, next_location]
        for i in self.data:
            if i[1] != -2:
                self.fat.append(i[1])
        network = self.nodes
        for node in network:
            if node != sender_port:
                response = requests.get(f'http://{sender_port}/get/fat')
                if response.status_code == 200:
                    requests.post(f'http://{node}/update/fat', json={
                        'fat': response.json()['fat']
                    })

        network = self.nodes
        counter = 0
        for node in network:
            if node != sender_port:
                response = requests.post(f'http://{node}/validate/fat', json={})
                if response.status_code == 200:
                    counter += 1

        if self.consensus(counter, sender_port) is True:
            network = self.nodes
            response = requests.get(f'http://{sender_port}/get/fat')
            if response.status_code == 200:
                for node in network:
                    requests.post(f'http://{node}/final/fat', json={'fat': response.json()['fat']})
                    requests.post(f'http://{node}/add/block', json={})

        filesystem.edit_data(data,location)
        print(filesystem.data)

    def consensus(self, counter, sender_port):
        total_nodes = 0
        network = self.nodes
        for node in network:
            if node != sender_port:
                total_nodes += 1
        if counter / total_nodes > 0.5:
            return True
        return False

    def validate_fat(self):
        self.data = filesystem.get_data()
        check = []
        for i in self.data:
            if i[1] != -2:
                check.append(i[1])
        if check == self.fat:
            return True
        return False

    def store_fat(self, fats):
        self.fat = fats

    def final_fat(self, fats):
        self.fat = fats

    # create fat logs
    def new_fat_log(self):
        if self.validate() is True:
            last_block = self.last_block
            previous_hash = self.hash(last_block)
            self.new_block(previous_hash)

    def new_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'fat': self.fat,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.fat = []
        self.data = []
        self.chain.append(block)
        return block

    def validate(self):
        previous_block = self.chain[0]
        counter = 1
        while counter < len(self.chain):
            current_block = self.chain[counter]
            previous_hash = self.hash(previous_block)
            if current_block['previous_hash'] != previous_hash:
                return False
            previous_block = current_block
            counter += 1
        return True

    @staticmethod
    def hash(block):
        block_hash = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_hash).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/add/block', methods=['POST'])
def add_block():
    blockchain.new_fat_log()
    return jsonify(), 201


@app.route('/new/request', methods=['POST'])
def new_request():
    values = request.get_json()
    required = ['data', 'location', 'sender_port']
    if not all(keys in values for keys in required):
        return 'Missing request info', 400
    blockchain.new_request(values['data'], values['location'], values['sender_port'])
    response = {'message': "REQUEST DONE"}
    return jsonify(response), 201


# get chain
@app.route('/get/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/get/data', methods=['GET'])
def get_data():
    response = {
        'data': blockchain.data
    }
    return jsonify(response), 200


@app.route('/get/fat', methods=['GET'])
def get_fat():
    response = {
        'fat': blockchain.fat
    }
    return jsonify(response), 200


@app.route('/update/fat', methods=['POST'])
def update_fat():
    values = request.get_json()
    required = ['fat']
    if not all(keys in values for keys in required):
        return 'Missing request info', 400
    blockchain.store_fat(values['fat'])
    response = {'message': "UPDATE DONE"}
    return jsonify(response), 201


@app.route('/validate/fat', methods=['POST'])
def validate_fat():
    blockchain.validate()
    return jsonify(), 200


@app.route('/final/fat', methods=['POST'])
def final_fat():
    values = request.get_json()
    required = ['fat']
    if not all(keys in values for keys in required):
        return 'Missing request info', 400
    blockchain.final_fat(values['fat'])
    return jsonify(), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
