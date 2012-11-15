import unittest
import time
from ethernetAdapter import *
from multiprocessing import Process

TEST_HOST = "localhost"
TEST_PORT = 3000

class TestEthernetAdapter(unittest.TestCase):
    def setUp(self):
        self.server = EthernetServer(TEST_PORT)
        self.process = Process(target = self.server.start)
        self.process.start()
        self.client = EthernetClient()
        
        # Try to connect to server
        # We have to wait until server starts
        attempts = 50
        delay = 0.01
        while attempts>0:
            --attempts
            try:
                self.client.connect((TEST_HOST, TEST_PORT))
            except:
                time.sleep(delay)
            else:
                break
        self.assertTrue(attempts > 0)
    
        
    def testTransmission(self):
        counter = 10
        while counter>0:
            counter-=1
            msg = "Hello, friend\n"
            print "Client: " + msg
            self.client.write(msg)
            answer = self.client.readline()
            self.assertTrue(len(answer)>0)
            print "Server: " + answer

if __name__ == '__main__':
    unittest.main()
