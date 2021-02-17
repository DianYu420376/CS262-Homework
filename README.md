# CS262-Hw1-Chatroom
NOTES: Sorry, we just realized a last minute problem that crashes the relay functionality, we need to fix that ASAP. 

CS262 programming homework 1
This assignment is complished with multi-threaded server and clients. Each connection would be managed by a main thread for command communication and another thread to relay the message.
The port is pre-assigned as 8084 and 8086. 
Required Python3

### How to run the server: 

  #### 1. First open up the terminal and run the server:
```
python server.py
```
  #### 2. Then open a new terminal and run the client:
  
 ```
 python client.py
 ```
 Follow the instruction in the terminal to use the chatroom application. 
 
  #### 3. You can open multiple clients and communicate between them.

When a client is connected to the server, it will receive the following welcome message:
```
Welcome! Connected to the server.
This is a chat room app. We support the following command listed below with its corresponding command code:
0. Help
1. Log in 
2. Send message to other users
3.  Register
4.  List all registered users
5.  Delete account
-1. Log out
```
Commands listed above are supported in our chatroom app. The client interface will ask the client to select from the above command codes and then ask client to provide further information for the command (e.g. the client needs to provide username and password for logging in or registration).

### Communication Protocol
Messages sent between the server and clients follows the following structure:  
++++++++++++++++++++  
| HEADER | CMD-CODE | MSGS |  
++++++++++++++++++++    
where HEADER contains the length of the total message (including the command code), and is padded to make sure it is of exact length set to `header_length = 10` in our implementation. CMD-CODE stand for the command code taking value from -1 to 5. Then followed by the text messages MSGS need to be sent. Command code and messages are separated by the `'\n'` deliminator. 

As for parsing the messages, the parser first receive the HEADER to get the total message length, then the parser will receive the message with buffer size equals to the message length.

For review's interest, the packing and unpacking function of the messages are implemented as follows:
```python
def pack_msg(code, msg): # Pack the message
    msg_encoded = f"{code}\n{msg}".encode('utf-8')
    msg_packed = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
    return msg_packed

def get_response(socket): # Unpack the message
    message_length = int(socket.recv(header_length).decode('utf-8').strip())
    msg = socket.recv(message_length).decode('utf-8')
    msgs = msg.split('\n')
    # print(msgs)
    try:
        msg_code = int(msgs[0])
    except ValueError:
        msg = "msg_code received is not integer, conversion failed"
        msg_code = -1
        return msg_code, msg
    if len(msgs) == 2:
        msg = msgs[1]
    else:
        msg = msgs[1:]
    return msg_code, msg
```



