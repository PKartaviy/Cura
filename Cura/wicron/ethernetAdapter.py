import __init__

import socket
from util.machineCom import VirtualPrinter
from threading import Thread

# The goal of this ethernet adapter to have the same interface and 
# behaviout as a printer connected by serial port.

def getMyIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    ip = ''
    try:
        s.connect(('8.8.8.8', 80));
        ip = s.getsockname()[0];
    except socket.error as e:
        ip = 'localhost'
        
    s.close()
    return ip

class EthernetClient(socket.socket):
    def __init__(self, _socket = None, timeout = 0.1):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM, proto=0, _sock=_socket)
        self.inMessage = ''
        self.settimeout(timeout)
        
    def write(self, data):
        self.sendall(data)
  
    # return '' if no data was read before timeout
    # in case of errors throws exception
    def readline(self):
        returnPos = -1
        while returnPos == -1:
            income = ''
            try:
                income = self.recv(4096)
            except socket.timeout:
                #we ignore timeout and return ''
                return ''
            if not len(income):
                raise socket.error
            self.inMessage += income
            returnPos = self.inMessage.find("\n")
        result = self.inMessage[:returnPos+1]
        self.inMessage = self.inMessage[returnPos+1:]
        return result

class  EthernetServer:
    def __init__(self, port, timeout = 0.1):
        # We use multithreading because we have one general resource - printer,
        # which is used in every thread
        # In CPython only one thread can be run simulteneously
        # This causes perfomancy problems but it usually doesn't make sense in IO tasks
        # If you don't have general resource and you want better perfomance than
        # it is better for you to use multiprocessing.
        self.port = port
        self.creatorThread = None
        self.serversocket = None
        self.enableWork = False
        self.timeout = timeout
        
    def __del__(self):
        self.stop()

    def start(self):
        host = getMyIp()
        if( not self.creatorThread):
            self.enableWork = True
            
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serversocket.bind((host, self.port))
            self.serversocket.listen(5)
            self.serversocket.settimeout(self.timeout)
            
            self.creatorThread = Thread(target = self.__creator__)
            self.creatorThread.start()

    def stop(self):
        self.enableWork = False
            
        if (self.creatorThread):
            self.creatorThread.join()
            self.creatorThread = None
        
        self.serversocket.close()
        

    def __creator__(self):
        host = getMyIp()
        
        socketThreades = []
        while(self.enableWork):
            try:
                (clientSocket, address) = self.serversocket.accept()
            except:
                #timeout
                continue
            else:
                s = EthernetClient(_socket = clientSocket)

                socketThreades.append(Thread(target = self.__processSocket__, args=(s,)))
                socketThreades[-1].start()

        for process in socketThreades:
            process.join()

    def __processSocket__(self, _socket):
        _socket.settimeout(self.timeout)
        socketWorking = True
        while ( socketWorking and self.enableWork):
            inp = ''
            try:
                inp = _socket.readline()
            except:
                socketWorking = False

            if socketWorking:
                out = self.processData(inp)
                if len(out):
                    _socket.write(out)
        _socket.close()
        
    # Should process input string from client and return output to client
    # If output contains no elementh than it won't be sent 
    def processData(self, inp):
        return inp

class PrintServer(EthernetServer):
    DEFAULT_PORT = 3000
    def __init__(self, port, printer=VirtualPrinter()):
        EthernetServer.__init__(self, port)
        self.printer = printer
    
    def processData(self, inp):
        self.printer.write(inp)
        return self.printer.readline()
        
    @classmethod
    def findPrintServer(cls, port, maskString="255.255.255.0"):
        return ServerFinder().findServer(port, maskString)

class ServerFinder:
    def __init__(self):
        self.ip = None        
        
    def __checkIp__(self, ip):
        client = EthernetClient()
        try:
            client.connect((ip, self.port))
        except:
            return False
        else:
            client.close()
            self.ip = ip
            return True
            
    def findServer(self, port, subnetMaskString):
        self.port = port
        ServerFinder.netLoop(getMyIp(), subnetMaskString, self.__checkIp__)
        return self.ip
    
    @staticmethod
    def netLoop(ipString, maskString, functor):
        maskString = maskString.split('.')
        mask = [int(num) for num in maskString]
        
        ip = ipString.split('.')
        ip = [int(num) for num in ip]
        
        base = []
        change = []
        for i in range(len(mask)):
            base.append(mask[i] & ip[i])
            change.append( (~mask[i]) & 0xFF)
            
        testIp = [0, 0, 0, 0]
        ipDiff = [0, 0, 0, 0]
        for ipDiff[0] in range(change[0]+1):
            for ipDiff[1] in range(change[1]+1):
                for ipDiff[2] in range(change[2]+1):
                    for ipDiff[3] in range(change[3]+1):
                        for i in range(len(ip)):
                            testIp[i] = base[i] + ipDiff[i]
                        testIpStr = ''.join(str(ipPiece)+'.' for ipPiece in testIp)[:-1]
                        
                        if functor(testIpStr):
                            return