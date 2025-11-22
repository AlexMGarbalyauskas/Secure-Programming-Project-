import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secure.base_test import BaseSeleniumTest

class TestSecureApp(BaseSeleniumTest):

    def test_register_login_create_note(self):
        driver = self.driver

        # ---- REGISTER ----
        driver.get(self.base_url + "register")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.XPATH, "//button[contains(text(),'Register')]").click()

        # Wait for redirect to login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # ---- LOGIN ----
        driver.get(self.base_url + "login")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("Password123")
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

        # Wait until Notes page loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'Your Notes')]"))
        )
        assert "Notes" in driver.page_source

        # ---- CREATE NOTE ----
        driver.get(self.base_url + "new_note")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        ).send_keys("Test Note")
        driver.find_element(By.NAME, "content").send_keys("This is a test note")

        # Wait until Create button is clickable and click
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save Note')]"))
        ).click()

        # Wait for flash message
        flash_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul/li[contains(text(),'Note created successfully')]"))
        )
        assert "Note created successfully" in flash_msg.text


if __name__ == "__main__":
    unittest.main()
