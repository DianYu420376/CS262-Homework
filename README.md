# CS262-Hw1-Chatroom

CS262 programming homework 1
This assignment is complished with multi-threaded server and clients. Each connection would be managed by a main thread for command communication and another thread to relay the message. ALL functions have been tested and should work correctly with multiple clients chatting with each other. You can chat with online/offline users. Once offline users logged in, all messages should be relayed in one second delay. 

The port is pre-assigned as 8084 and 8086. 
Required Python3. You have to make sure your port 8084 and 8086 is available if you meet any connection issue.

#### There are already two tester users added, the username:password for them are: tester:abc123 abc:abc

Keep in mind that you can only send messages to pre-added or registered users. Everything should work dynamically.  

Notebook is appened at the end of this README

### How to run/test the server: 

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
Commands listed above are supported in our chatroom app. The client interface will ask the client to select from the above command codes and then ask client to provide further information for the command (e.g. the client needs to provide username and password for logging in or registration). Detailed description of each command is as follows:  
`0. Help` - Returns the help message that is shown above.  
`1. Log in` - Log in for an existing account. User will further be asked to type in his/her username and corresponding password.   
`2. Send message to other users` - Send text messages to existing accounts, user will further be asked to type in the username that he/she wants to send the message to, as well as the message he/she wants to send.  
`3. Register` - Creating a new account. User will further be asked to create his/her username and corresponding password, then he/she will be automatically logged in as a new user.  
`4. List all registered users` - Return a list containing all existing accounts.  
`5. Delete account` - Delete account for an already logged in user. User will be asked to type in his/her password again to confirm the deletion.  
`-1. Log out` - Log out.


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



## Notebook
### Main program design path:
We intended to have one thread that handles all the communications. After finishing the first
version of code, we found it's nearly impossible if want to stick to blocking recv/send because the `recv()` would 
keep waiting until enough bytes are flushed. Then we decided to add one more thread 
specially for relaying all information. 
Then, since we have two threads now, there should be a mechanism that they can exchange information 
to relay messages. We then adopted a dictionary of queue that each queue would maintain 
all messages to the users which is the key for each entry of dict. To prevent from race
condition, we used the `threading.lock()` to lock the resource.
### Protocol design:
We initially just wanted to use simple messages like succesful/failure to as simple
communication. Then we feel it actually complicates the message recognition. Instead,
we design a protocol (more detailed description shown in the above README section) such that the message from client would contain the 
1. the 10 bytes header contains the length of message body
2. the message body that contains the command code and data separated by new line operator `'\n'` 

We use new line operator because the user can't input any of that since hitting return 
would just reach EOF from user's perspective.
### Miscellaneous:
We initially implement the deletion function that user can input the username and 
password to delete any entry. Then we realized it doesn't make sense because user should only be
able to delete their own account.

Because the two-threads per client design of our program, we spent a lot of time 
to debug to bring them up at the same time. The coordination between two threads is 
quite hard to design. 
