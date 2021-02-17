# CS262-Hw1-Chatroom
NOTES: Sorry, we just realized a last minute problem that crashes the relay functionality, we need to fix that ASAP. 

CS262 programming homework 1
This assignment is complished with multi-threaded server and clients. Each connection would be managed by a main thread for command communication and another thread to relay the message.
The port is pre-assigned as 8084 and 8086. 
Required Python3

How to run the server: 

  1. First open up the terminal and run the server:
```
python server.py
```
  2. Then open a new terminal and run the client:
  
 ```
 python client.py
 ```
 Follow the instruction in the terminal to use the chatroom application. 
 
  3. You can open multiple clients and communicate between them.

When a client is connected to the server, it will receive the following welcome message:
```python
'Welcome! Connected to the server.\nThis is a chat room app. We support the following command listed below with its corresponding command code:\
                            \n 0. Help\n 1. Log in\n 2. Send message to other users\n 3. Register\n 4. List all registered users\
                            \n 5. Delete account\n -1. Log out'
```




