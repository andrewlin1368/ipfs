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
        self.fat = []
        self.chain = []
        self.nodes = set()
        self.new_block(previous_hash='0')
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


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
