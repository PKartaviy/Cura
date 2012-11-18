from testEthernetAdapter import *

server = PrintServer(PrintServer.DEFAULT_PORT, VirtualPrinter())
server.start()

try:
    while(1):
        time.sleep(0.5)
except:
    server.stop()
