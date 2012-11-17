# Add needed parent folders to path
import sys
sys.path.append('../')

import __init__

import unittest
import time
from ethernetAdapter import *
from multiprocessing import Process
import string
import random

TEST_HOST = getMyIp()
TEST_PORT = 3000

def start(host, port, server = None, client = None):
   if (not client):
       client = EthernetClient()
   if (not server):
       server = EthernetServer(port)
   try:
       server.start()
   except Exception as e :
       print "Failed to start server \n", e 
       return (False, None, None)
        
   # Try to connect to server
   # We have to wait until server starts
   attempts = 50
   delay = 0.02
   while attempts>0:
       attempts-=1
       try:
           client.connect((host, port))
       except:
           time.sleep(delay) 
       else:
           break

   if(attempts == 0):
       print "Failed to connect to server"
       return (False, None, None)
   return (True, server, client)

def stop(server, client):
    if(client):
        client.close()
    if(server):
        server.stop()
class TestEthernetAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "Test client server communication"
        print "Server will be run on this pc with IP:PORT=", str(TEST_HOST) + ":" + str(TEST_PORT)
        (cls.successfulConnection , cls.server, cls.client) = start(TEST_HOST, TEST_PORT)

    @classmethod
    def tearDownClass(cls):
        stop(cls.server, cls.client)

    def testConnection(self):
        self.assertTrue(TestEthernetAdapter.successfulConnection)
   
    def testTransmission(self):
        if(not TestEthernetAdapter.successfulConnection):
            self.skipTest("Failed to connect to server")

        counter = 5
        while counter>0:
            counter-=1
            msg = "Hello, friend\n"
            TestEthernetAdapter.client.write(msg)
            answer = self.client.readline()
            self.assertTrue(len(answer)>0)
         
    def testLongTransmissions(self):
        if(not TestEthernetAdapter.successfulConnection):
            self.skipTest("Failed to connect to server")

        num = 10000
        msg = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(num))
        msg += '\n'

        TestEthernetAdapter.client.write(msg)
        answer = TestEthernetAdapter.client.readline()
        
        self.assertEqual(msg, answer)
        
    def testMultiClients(self):
        if(not TestEthernetAdapter.successfulConnection):
            self.skipTest("Failed to connect to server")

        N = 100
        clients = [ EthernetClient() for c in range(0, N)]
        
        testMsg = "Test input \n"
        for client in clients:
            client.connect((TEST_HOST, TEST_PORT))
            client.write(testMsg)
            out  = client.readline()
            self.assertEqual(testMsg, out)

class TestPrintServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.connected, cls.server, cls.client) = start(TEST_HOST, TEST_PORT, server = PrintServer(TEST_PORT))
        cls.virtualPrinter = VirtualPrinter()

    @classmethod
    def tearDownClass(cls):
        stop(cls.server, cls.client)
     
    def testVsVirtualPrinter(self):
        if(not TestPrintServer.connected):
            self.skipTest("Failed to connect to server")
        for i in xrange(0, 5):
            vp = self.virtualPrinter.readline()
            if vp =='':
                break
            
            rvp = ''
            while rvp=='':
                rvp = self.client.readline()
            self.assertEqual(vp, rvp)
        
        for i in xrange(0, 100):
            print self.virtualPrinter.readline()

    
if __name__ == '__main__':
    unittest.main()
