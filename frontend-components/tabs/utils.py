import socket
import threading
import queue

class Client():

    def __init__(self, server_ip : str, server_port : int):
        self.sock = socket.socket()
        self.sock.connect((server_ip, server_port))

        self.recieved_msg = queue.Queue(20)

        self.recieve_tread = threading.Thread(target=self._get_recieved_on_thread, args=(self.recieved_msg,))
        self.recieve_tread.start()

    def send(self, val : str):
        self.sock.send(val.encode())

    def _get_recieved_on_thread(self, recieved_msg):
        while True:
            inp = self.sock.recv(1024).decode()
            if not recieved_msg.full():
                recieved_msg.put(inp)


    def recieve(self):
        msg = ''
        if not self.recieved_msg.empty():
            msg = self.recieved_msg.get()
    
        return msg