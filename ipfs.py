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
            'address_two': 1, 'data_one': 'F1', 'next_port_one': '5001', 'next_address_one': 0, 'data_two': 'G1',
            'next_port_two': '5001', 'next_address_two': 1})
        requests.post('http://127.0.0.1:5001/pre/add', json={
            'file_one': 'file1', 'port_one': '5001', 'address_one': 0, 'file_two': 'file2', 'port_two': '5001',
            'address_two': 1, 'data_one': 'F2', 'next_port_one': '5002', 'next_address_one': 0, 'data_two': 'G2',
            'next_port_two': '5002', 'next_address_two': 1})
        requests.post('http://127.0.0.1:5002/pre/add', json={
            'file_one': 'file1', 'port_one': '5002', 'address_one': 0, 'file_two': 'file2', 'port_two': '5002',
            'address_two': 1, 'data_one': 'F3', 'next_port_one': '5003', 'next_address_one': 0, 'data_two': 'G3',
            'next_port_two': '5003', 'next_address_two': 1})
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

    def edit(self, file_name, previous_data, new_data, current_port):
        data = []
        route = []
        count = 0
        counter = 0
        route.append((requests.post('http://127.0.0.1:5000/node/info', json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1

        node_counter = 5000
        for i in data:
            if i[0] == previous_data:
                i[0] = new_data
                break
            node_counter += 1

        for i in route:
            self.fat.append([i[0], i[1], i[2]])

        consensus_counter = 0
        network = self.nodes
        for node in network:
            if node != current_port:
                response = requests.post(f'http://{node}/validate', json={
                    'file_name': file_name, 'sender_port': current_port
                })
                if response.status_code == 200:
                    consensus_counter += 1
        value = self.consensus(consensus_counter, current_port)
        if value:
            requests.post(f'http://127.0.0.1:{node_counter}/update/data', json={
                'data': new_data, 'address': route[1][2]
            })

            network = self.nodes
            for node in network:
                requests.post(f'http://{node}/new/transaction', json={})
        else:
            self.fat = []

    def new_transaction(self):
        last_block = self.last_block
        previous_hash = self.hash(last_block)
        self.new_block(previous_hash)

    def validation_fat(self, file_name, sender_port):
        data = []
        route = []
        count = 0
        counter = 0
        fat = []
        route.append((requests.post('http://127.0.0.1:5000/node/info', json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1
        route.append((requests.post(f'http://127.0.0.1:{data[counter][1]}/node/info',
                                    json={'file_name': file_name})).json())
        data.append((requests.post(f'http://127.0.0.1:{route[count][1]}/data/info',
                                   json={'node_address': route[count][2]})).json())
        count += 1
        counter += 1

        for i in route:
            self.fat.append([i[0], i[1], i[2]])

        fat.append(requests.get(f'http://{sender_port}/get/fat/info').json())
        if self.fat == fat:
            return True

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

    def get_node_info(self, file_name):
        for i in self.node_info:
            if i[0] == file_name:
                return i

    def get_data_info(self, node_address):
        return self.data_info[node_address]

    def update_data(self, data, address):
        self.data_info[address][0] = data

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


@app.route('/new/transaction', methods=['POST'])
def new_transaction():
    blockchain.new_transaction()
    return jsonify()


@app.route('/validate', methods=['POST'])
def validate():
    values = request.get_json()
    required = ['file_name', 'sender_port']
    if not all(keys in values for keys in required):
        return 'Error', 400
    blockchain.validation_fat(values['file_name'], values['sender_port'])
    return jsonify(), 200


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
        return 'Error', 400
    blockchain.pre_add_info(values['file_one'], values['port_one'], values['address_one'], values['file_two'],
                            values['port_two'], values['address_two'],
                            values['data_one'], values['next_port_one'], values['next_address_one'], values['data_two'],
                            values['next_port_two'], values['next_address_two'])
    return jsonify()


@app.route('/edit', methods=['POST'])
def edit():
    values = request.get_json()
    required = ['file_name', 'previous_data', 'new_data', 'current_port']
    if not all(keys in values for keys in required):
        return 'Error', 400
    blockchain.edit(values['file_name'], values['previous_data'], values['new_data'], values['current_port'])
    return jsonify()


@app.route('/get/node/info', methods=['GET'])
def get_node_info():
    response = blockchain.node_info
    return jsonify(response)


@app.route('/get/data/info', methods=['GET'])
def get_data_info():
    response = blockchain.data_info
    return jsonify(response)


@app.route('/get/fat/info', methods=['GET'])
def get_fat_info():
    response = blockchain.fat
    return jsonify(response)


@app.route('/node/info', methods=['GET', 'POST'])
def node_info():
    values = request.get_json()
    required = ['file_name']
    if not all(keys in values for keys in required):
        return 'Error', 400
    response = blockchain.get_node_info(values['file_name'])
    return jsonify(response)


@app.route('/data/info', methods=['GET', 'POST'])
def data_info():
    values = request.get_json()
    required = ['node_address']
    if not all(keys in values for keys in required):
        return 'Error', 400
    response = blockchain.get_data_info(values['node_address'])
    return jsonify(response)


@app.route('/update/data', methods=['POST'])
def update():
    values = request.get_json()
    required = ['data', 'address']
    if not all(keys in values for keys in required):
        return 'Error', 400
    blockchain.update_data(values['data'], values['address'])
    return jsonify()


@app.route('/get/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
