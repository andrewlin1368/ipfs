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
## postman
1. /start
2. /edit
   ```
   {
    "file_name":"file1",
    "previous_data":"F3",
    "new_data":"F100",
    "current_port":"127.0.0.1:5000"
   }
   ```

## Validation
```[['file_name','node_port','node_address']]```

```[['data','next_node','next_node_address']]```
  
