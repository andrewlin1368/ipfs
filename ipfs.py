import hashlib
import json
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.node_info = []
        self.data_info = []
        self.fat = []
        self.chain = []
        self.nodes = set()
        self.new_block(previous_hash='0')
        self.create_nodes(address='http://127.0.0.1:5000')
        self.create_nodes(address='http://127.0.0.1:5001')
        self.create_nodes(address='http://127.0.0.1:5002')
        self.create_nodes(address='http://127.0.0.1:5003')

    def pre_add(self):
        requests.post('http://127.0.0.1:5000/pre/add', json={
            'file_one': 'file1', 'port_one': '5000', 'address_one': 0, 'file_two': 'file2', 'port_two': '5000',
            'address_two': 1, 'data_one': 'F1', 'next_port_one': '5001', 'next_address_one': 0, 'data_two': 'G3',
            'next_port_two': '5003', 'next_address_two': 1})
        requests.post('http://127.0.0.1:5001/pre/add', json={
            'file_one': 'file1', 'port_one': '5001', 'address_one': 0, 'file_two': 'file2', 'port_two': '5001',
            'address_two': 1, 'data_one': 'F2', 'next_port_one': '5002', 'next_address_one': 0, 'data_two': 'G2',
            'next_port_two': '5000', 'next_address_two': 1})
        requests.post('http://127.0.0.1:5002/pre/add', json={
            'file_one': 'file1', 'port_one': '5002', 'address_one': 0, 'file_two': 'file2', 'port_two': '5002',
            'address_two': 1, 'data_one': 'F3', 'next_port_one': '5003', 'next_address_one': 0, 'data_two': 'G1',
            'next_port_two': '5001', 'next_address_two': 1})
        requests.post('http://127.0.0.1:5003/pre/add', json={
            'file_one': 'file1', 'port_one': '5003', 'address_one': 0, 'file_two': 'file2', 'port_two': '5003',
            'address_two': 1, 'data_one': 'F4', 'next_port_one': '-1', 'next_address_one': -1, 'data_two': 'G4',
            'next_port_two': '-1', 'next_address_two': -1})

    def pre_add_info(self, file_one, port_one, address_one, file_two, port_two, address_two,
                     data_one, next_port_one, next_address_one, data_two, next_port_two, next_address_two):
        self.node_info.append([file_one, port_one, address_one])
        self.node_info.append([file_two, port_two, address_two])
        self.data_info.append([data_one, next_port_one, next_address_one])
        self.data_info.append([data_two, next_port_two, next_address_two])

    def create_nodes(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid')

    def consensus(self, counter, sender_port):
        total_nodes = 0
        network = self.nodes
        for node in network:
            if node != sender_port:
                total_nodes += 1
        if counter / total_nodes > 0.5:
            return True
        return False

    def new_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'fat': self.fat,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.fat = []
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


@app.route('/start', methods=['POST'])
def start():
    blockchain.pre_add()
    return jsonify()


@app.route('/pre/add', methods=['POST'])
def pre_add():
    values = request.get_json()
    required = ['file_one', 'port_one', 'address_one', 'file_two', 'port_two', 'address_two',
                'data_one', 'next_port_one', 'next_address_one', 'data_two', 'next_port_two', 'next_address_two']
    if not all(keys in values for keys in required):
        return 'Transaction invalid', 400
    blockchain.pre_add_info(values['file_one'], values['port_one'], values['address_one'], values['file_two'],
                            values['port_two'], values['address_two'],
                            values['data_one'], values['next_port_one'], values['next_address_one'], values['data_two'],
                            values['next_port_two'], values['next_address_two'])
    return jsonify()


@app.route('/get/node/info', methods=['GET'])
def get_node_info():
    response = blockchain.node_info
    return jsonify(response)


@app.route('/get/data/info', methods=['GET'])
def get_data_info():
    response = blockchain.data_info
    return jsonify(response)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
