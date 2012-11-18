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

from util.machineCom import VirtualPrinter

TEST_HOST = getMyIp()
TEST_PORT = PrintServer.DEFAULT_PORT

def lambda_print(x):
    print x
    
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

class AbstractServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.connected, cls.server, cls.client) = start(TEST_HOST, TEST_PORT, server = EthernetServer(TEST_PORT))
        
    @classmethod
    def tearDownClass(cls):
        stop(cls.server, cls.client)
        
class TestEthernetAdapter(AbstractServerTest):
    def testConnection(self):
        self.assertTrue(TestEthernetAdapter.connected)
   
    def testTransmission(self):
        if(not TestEthernetAdapter.connected):
            self.skipTest("Failed to connect to server")

        counter = 5
        while counter>0:
            counter-=1
            msg = "Hello, friend\n"
            TestEthernetAdapter.client.write(msg)
            answer = self.client.readline()
            self.assertTrue(len(answer)>0)
         
    def testLongTransmissions(self):
        if(not TestEthernetAdapter.connected):
            self.skipTest("Failed to connect to server")

        num = 10000
        msg = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(num))
        msg += '\n'

        TestEthernetAdapter.client.write(msg)
        answer = TestEthernetAdapter.client.readline()
        
        self.assertEqual(msg, answer)
        
    def testMultiClients(self):
        if(not TestEthernetAdapter.connected):
            self.skipTest("Failed to connect to server")

        N = 25
        clients = [ EthernetClient() for c in range(0, N)]
        
        testMsgA = "Test input A \n"
        testMsgB = "Test input B \n"
        for client in clients:
            client.connect((TEST_HOST, TEST_PORT))
            
            client.write(testMsgA)
            out  = client.readline()
            self.assertEqual(testMsgA, out)
            
            client.write(testMsgB)
            out  = client.readline()
            self.assertEqual(testMsgB, out)


class IpCounter:
    def __init__(self):
        self.ipNum = 0
            
    def f(self, ip):
        self.ipNum += 1
        return False

class AbstractPrintServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (cls.connected, cls.server, cls.client) = \
        start(TEST_HOST, TEST_PORT, server = PrintServer(TEST_PORT, VirtualPrinter())) 
        cls.client = PrinterClient(_socket = cls.client)
        cls.virtualPrinter = VirtualPrinter() 
        
    @classmethod
    def tearDownClass(cls):
        stop(cls.server, cls.client)

class TestPrintServer(AbstractPrintServerTest):
    # Note: In current realization virtual printer has one queue of messages
    # Thus if several sockets will connect to VirtualPrinter than each thread wiil receive only part of messages
    def testVsVirtualPrinter(self):
        if(not TestPrintServer.connected):
            self.skipTest("Failed to connect to server")
        for i in xrange(0, 3):
            vp = self.virtualPrinter.readline()
            if vp =='':
                break
                     
            attempts = 10
            rvp = ''
            while rvp=='' and attempts >0 :
                attempts -= 1
                rvp = self.client.readline()
            self.assertEqual(vp, rvp)
            
        for i in range(1):
            outMsg = 'M105\n'
            self.virtualPrinter.write(outMsg)
            self.client.write(outMsg)
            
            vp = self.virtualPrinter.readline()
            rvp = self.client.readline()
            #print 'VIRTUAL: ',vp, 'REMOTE: ', rvp 
            self.assertEqual(vp, rvp)
            
            vp = self.virtualPrinter.readline()
            rvp = self.client.readline()
            #print 'VIRTUAL: ',vp, 'REMOTE: ', rvp 
            self.assertEqual(vp, rvp)
        
        

class TestPrintServerFinder(AbstractPrintServerTest):
    def testNetLoop(self):
        counter = IpCounter()
        ServerFinder.netLoop("1.2.3.255", "254.254.254.254", counter.f)
        self.assertEqual(counter.ipNum, 16)
        
    def testFindPrintServer(self):
        # I assume that server run's on my PC
        # I use mask which is tight to my ip to make test short
        ipFound = PrintServer.findPrintServer(TEST_PORT, "255.255.255.230")
        print "Server ip", getMyIp(), " found server ", ipFound
        self.assertEqual(getMyIp(), ipFound)

    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEthernetAdapter)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPrintServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPrintServerFinder)
    unittest.TextTestRunner(verbosity=2).run(suite)

