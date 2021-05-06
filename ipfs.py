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
        self.new_fat_log(value=False)

    def new_request(self, data, location, sender_port):
        self.data = filesystem.get_data()
        next_location = self.data[location][1]
        self.data[location] = [data, next_location]
        for i in self.data:
            if i[1] != -2:
                self.fat.append(i[1])

    def store_fat(self,update_fat):


    # create fat logs
    def new_fat_log(self, value):
        if self.validate() is True:
            if value is False:
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



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
