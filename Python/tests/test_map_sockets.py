# test_map_sockets.py
import unittest
import socket
import json
import threading
import time

class TestMapSocketCommunication(unittest.TestCase):
    def setUp(self):
        """Set up test server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', 65432))
        self.received_data = None
        self.server_running = True
        
        def server_thread():
            while self.server_running:
                try:
                    data, _ = self.server_socket.recvfrom(1024)
                    self.received_data = json.loads(data.decode('utf-8'))
                except:
                    break
        
        self.server_thread = threading.Thread(target=server_thread, daemon=True)
        self.server_thread.start()
    
    def test_socket_communication(self):
        """Test basic socket communication"""
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_data = {'test': 'data'}
        
        client_socket.sendto(
            json.dumps(test_data).encode('utf-8'),
            ('127.0.0.1', 65432)
        )
        
        time.sleep(0.1)
        self.assertIsNotNone(self.received_data)
        self.assertEqual(self.received_data, test_data)
    
    def tearDown(self):
        """Clean up"""
        self.server_running = False
        self.server_socket.close()
        time.sleep(0.1)

if __name__ == '__main__':
    unittest.main()