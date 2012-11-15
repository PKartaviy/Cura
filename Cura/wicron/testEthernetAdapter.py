import unittest
import time
from ethernetAdapter import *
from multiprocessing import Process
import string
import random

TEST_HOST = "localhost"
TEST_PORT = 3000

class TestEthernetAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print "Setup class TestEthernetAdapter"
        cls.server = EthernetServer(TEST_PORT)
        cls.process = Process(target = cls.server.start)
        cls.process.start()
        cls.client = EthernetClient()
        
        # Try to connect to server
        # We have to wait until server starts
        attempts = 50
        delay = 0.01
        while attempts>0:
            attempts-=1
            try:
                cls.client.connect((TEST_HOST, TEST_PORT))
            except:
                time.sleep(delay)
            else:
                break
        cls.succesfulConection =  (attempts > 0)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.process.join()
        print "Tear down class TestEthernetAdapter"

    def testConnection(self):
        self.assertTrue(TestEthernetAdapter.succesfulConection)        
    def testTransmission(self):
        counter = 5
        while counter>0:
            counter-=1
            msg = "Hello, friend\n"
            print "Client: " + msg
            TestEthernetAdapter.client.write(msg)
            answer = self.client.readline()
            self.assertTrue(len(answer)>0)
            print "Server: " + answer
    
    def testLongTransmissions(self):
        num = 10000
        msg = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(num))
        msg += '\n'

        print "write big line"
        TestEthernetAdapter.client.write(msg)
        print "read big line"
        answer = TestEthernetAdapter.client.readline()
        
        self.assertEqual(msg, answer) 

if __name__ == '__main__':
    unittest.main()
