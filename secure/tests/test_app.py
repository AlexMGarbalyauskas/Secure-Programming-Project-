#1
#Imports
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secure.base_test import BaseSeleniumTest
#1 end 





#2 
# main test class automating registration, login, and note creation
class TestSecureApp(BaseSeleniumTest):
    
    # Helper to wait for element and type
    def wait_and_type(self, by, value, text):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, value))
        ).send_keys(text)

    def wait_and_click(self, by, value):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, value))
        ).click()

    def test_register_login_create_note(self):
        driver = self.driver

       
        # Register a new user
        driver.get(self.base_url + "register")

        # Wait for form fields + CSRF
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "csrf_token"))
        )
        
        # Fill in registration form
        self.wait_and_type(By.NAME, "username", "testuser")
        self.wait_and_type(By.NAME, "password", "Password123")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Register')]")

        # Wait for redirect to login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
# 2 end 
       





# 3 
        # Login with the new user
        driver.get(self.base_url + "login")
        
        # Wait for form fields + CSRF
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "csrf_token"))
        )

        # Fill in login form
        self.wait_and_type(By.NAME, "username", "testuser")
        self.wait_and_type(By.NAME, "password", "Password123")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Login')]")

        # Wait until Notes page loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(),'Your Notes')]")
            )
        )
# 3 end 





#4      
        # Create a new note

        driver.get(self.base_url + "new_note")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "csrf_token"))
        )
        
        # Fill in note form
        self.wait_and_type(By.NAME, "title", "Test Note")
        self.wait_and_type(By.NAME, "content", "This is a test note")
        self.wait_and_click(By.XPATH, "//button[contains(text(),'Save Note')]")
# 4 end 
        





        # Verify note creation success message
    
        flash_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//li[contains(text(),'Note created successfully')]")
            )
        )
        
        # Verify flash message content
        self.assertIn("Note created successfully", flash_msg.text)




# Start of db.py additions 
if __name__ == "__main__":
    unittest.main()
