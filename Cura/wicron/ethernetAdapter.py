import __init__
import socket

class EthernetClient(socket.socket):
    def __init__(self, _socket = None):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM, proto=0, _sock=_socket)
        self.inMessage = ''
        
    def write(self, data):
        self.sendall(data)
  
    def readline(self):
        returnPos = -1
        while returnPos == -1:
            income = self.recv(4096)
            if not len(income):
                # I decided not to return inMessage 
                # because it is damaged - at least threre is no \n
                # at the end of string
                return ''
            self.inMessage += income
            returnPos = self.inMessage.find("\n")

        result = self.inMessage[:returnPos+1]
        self.inMessage = self.inMessage[returnPos+1:]
        return result

class  EthernetServer:
    def __init__(self, port):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
    
    def start(self):
        print "Inside process"
        host = ''
        # There is some problem in detection of your ip
        # when DNS server is not properly configured
        # http://mail.python.org/pipermail/python-bugs-list/2004-May/022890.html
        try:
            host = socket.gethostbyname(socket.gethostname())
        except:
            host = ''
        print host
        
        print "bind"
        self.serversocket.bind((host, self.port))
        print "listen"
        self.serversocket.listen(5)
        
        (clientSocket, address) = self.serversocket.accept()
        s = EthernetClient(_socket = clientSocket)
        
        result = "dummy"
        while len(result)>0:
            result = s.readline()
            s.write(result)

    
