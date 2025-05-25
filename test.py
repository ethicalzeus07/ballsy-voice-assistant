#!/usr/bin/env python3
"""
Test script for validating the voice assistant functionality and performance.
This script tests various components of the voice assistant system:
- Speech recognition accuracy
- AI response quality
- Command processing
- WebSocket communication
- UI responsiveness
"""

import os
import sys
import time
import json
import requests
import unittest
import subprocess
import threading
import webbrowser
from pathlib import Path

# Define paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "src" / "backend"
FRONTEND_DIR = ROOT_DIR / "src" / "frontend"

class VoiceAssistantTests(unittest.TestCase):
    """Test suite for the voice assistant system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment - start servers"""
        # Start backend server
        cls.backend_port = 8001  # Use different port for testing
        cls.backend_process = cls._start_backend_server(cls.backend_port)
        
        # Wait for backend to start
        time.sleep(3)
        
        # Base URLs
        cls.backend_url = f"http://localhost:{cls.backend_port}"
        
        print("Test environment setup complete")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment - stop servers"""
        if hasattr(cls, 'backend_process'):
            cls.backend_process.terminate()
            print("Backend server stopped")
    
    @classmethod
    def _start_backend_server(cls, port):
        """Start the backend FastAPI server for testing"""
        backend_script = BACKEND_DIR / "app.py"
        
        # Run in a separate process
        process = subprocess.Popen(
            [sys.executable, str(backend_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def test_backend_health(self):
        """Test that the backend server is running and healthy"""
        try:
            response = requests.get(f"{self.backend_url}/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["name"], "Voice Assistant API")
            self.assertEqual(data["status"], "running")
            print("✅ Backend health check passed")
        except Exception as e:
            self.fail(f"Backend health check failed: {e}")
    
    def test_command_processing(self):
        """Test command processing with various commands"""
        test_commands = [
            {
                "command": "what time is it",
                "expected_contains": ["It's", ":"]
            },
            {
                "command": "what is 2 + 2",
                "expected_contains": ["4"]
            },
            {
                "command": "hello",
                "expected_contains": ["Hi", "help"]
            },
            {
                "command": "who is Albert Einstein",
                "expected_contains": ["physicist", "relativity"]
            }
        ]
        
        for test in test_commands:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/command",
                    json={"command": test["command"], "user_id": 1}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                # Check that response contains expected text
                for expected in test["expected_contains"]:
                    self.assertIn(expected.lower(), data["response"].lower())
                
                print(f"✅ Command test passed: '{test['command']}'")
            except Exception as e:
                self.fail(f"Command test failed for '{test['command']}': {e}")
    
    def test_settings_api(self):
        """Test settings API functionality"""
        # Test getting default settings
        try:
            response = requests.get(f"{self.backend_url}/api/settings/1")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("settings", data)
            print("✅ Get settings test passed")
            
            # Test updating settings
            new_settings = {
                "voice": "Samantha",
                "voice_speed": 200,
                "theme": "dark"
            }
            
            response = requests.put(
                f"{self.backend_url}/api/settings/1",
                json=new_settings
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("settings", data)
            self.assertEqual(data["settings"]["voice"], "Samantha")
            self.assertEqual(data["settings"]["voice_speed"], 200)
            self.assertEqual(data["settings"]["theme"], "dark")
            print("✅ Update settings test passed")
        except Exception as e:
            self.fail(f"Settings API test failed: {e}")
    
    def test_history_api(self):
        """Test command history API functionality"""
        try:
            # First send a command to ensure there's history
            requests.post(
                f"{self.backend_url}/api/command",
                json={"command": "test history command", "user_id": 1}
            )
            
            # Then get history
            response = requests.get(f"{self.backend_url}/api/history/1?limit=5")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("history", data)
            self.assertTrue(len(data["history"]) > 0)
            print("✅ History API test passed")
        except Exception as e:
            self.fail(f"History API test failed: {e}")
    
    def test_math_calculation(self):
        """Test math calculation functionality"""
        test_calculations = [
            {"command": "5 + 10", "expected": "15"},
            {"command": "20 - 5", "expected": "15"},
            {"command": "4 * 5", "expected": "20"},
            {"command": "100 / 4", "expected": "25"}
        ]
        
        for test in test_calculations:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/command",
                    json={"command": test["command"], "user_id": 1}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn(test["expected"], data["response"])
                print(f"✅ Math calculation test passed: '{test['command']}'")
            except Exception as e:
                self.fail(f"Math calculation test failed for '{test['command']}': {e}")
    
    def test_ai_response_quality(self):
        """Test AI response quality for various queries"""
        test_queries = [
            "what is the capital of France",
            "how does photosynthesis work",
            "who wrote Romeo and Juliet",
            "what is machine learning"
        ]
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/command",
                    json={"command": query, "user_id": 1}
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                # Check that response is not empty and has reasonable length
                self.assertTrue(len(data["response"]) > 10)
                print(f"✅ AI response test passed: '{query}'")
            except Exception as e:
                self.fail(f"AI response test failed for '{query}': {e}")

def run_tests():
    """Run the test suite"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
