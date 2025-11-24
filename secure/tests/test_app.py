
#1 
# imports 
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secure.base_test import BaseSeleniumTest
#1 end 


# 2 
# Actual test cases for the secure app
class TestSecureApp(BaseSeleniumTest):
 

    # Helper methods 
    def wait_and_type(self, by, value, text):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        ).send_keys(text)
    
    # helper method to wait and click an element
    def wait_and_click(self, by, value):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, value))
        ).click()
    
#2 end

    #3
    def test_register_login_create_note(self):
        driver = self.driver

        # --- Register ---
        driver.get(self.base_url + "register")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        self.wait_and_type(By.NAME, "username", "testuser")
        self.wait_and_type(By.NAME, "password", "Password123")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Register')]")

        # Wait for redirect to login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Login
        driver.get(self.base_url + "login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "csrf_token"))
        )
        
        # Login with the new user 
        self.wait_and_type(By.NAME, "username", "testuser")
        self.wait_and_type(By.NAME, "password", "Password123")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Login')]")

        # Wait for notes page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Your notes']"))
        )

        # --- Create note ---
        driver.get(self.base_url + "new_note")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "csrf_token"))
        )

        # Fill out note form 
        self.wait_and_type(By.NAME, "title", "Test Note")
        self.wait_and_type(By.NAME, "content", "This is a test note")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Save Note')]")

        # Wait for redirect back to notes page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Your notes']"))
        )

        # Wait for flash message
        flash_msg = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "flash-messages"))
        )
        self.assertIn("Note created successfully", flash_msg.text)


# Verify the new note appears in the notes list
if __name__ == "__main__":
    unittest.main()
