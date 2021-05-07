# IPFS Blockchain

## running
1. Python 3.6+
2. Install pipenv
```$ pip install pipenv```
   
3. install requirements
```$ pipenv install```
   
4. Running server
- ```$ python ipfs.py```
- ```$ python ipfs.py -p 5001```
- ```$ python ipfs.py -p 5002```
- ```$ python ipfs.py -p 5003```

5. use postman as the api

## Validation
- once an edit is made
- a fat log will be created
- every other node will compare the fat log with the original fat log
- if fat log matches and 51% of network agrees
- new block added to blockchain
- fs.py updates the data with the new edit

## Others
- static network with 4 nodes
- request launch with /new/request
```{
    "data": "Example", 
    "location": 3, 
    "sender_port": "127.0.0.1:5000
    }```
  