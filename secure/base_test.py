# secure/base_test.py
import unittest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import subprocess
import time
import atexit
import os

class BaseSeleniumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Flask app
        cls.flask_process = subprocess.Popen(
            ["python", os.path.join(os.path.dirname(__file__), "app.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # wait for server to start

        # Setup Firefox driver
        options = Options()
        options.headless = True
        cls.driver = webdriver.Firefox(options=options)
        cls.driver.maximize_window()
        cls.base_url = "http://127.0.0.1:5002/"

        # Ensure server is killed at the end
        atexit.register(cls.flask_process.kill)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.flask_process.kill()
