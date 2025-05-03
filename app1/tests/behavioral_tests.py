from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from django.test import LiveServerTestCase
from datetime import datetime
import time
import os
import unittest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

'''
For Brandon: Add 'options.add_argument('--headless')' to options
'''


'''
Layout Library Behavioral Tests
'''
# 1. Log into the application
class Test01_LoginTestCase(LiveServerTestCase):
    def test01_login(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the page to load after the login attempt
        time.sleep(5)

        # Verify the URL after login
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        current_url = driver.current_url

        # Assert that the current URL is the expected one
        self.assertEqual(current_url, expected_url, f"Expected URL {expected_url} but got {current_url}")

# 2. Create a new folder in Layout Library
class Test02_CreateFolderTestCase(LiveServerTestCase):
    def test02_create_folder(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Create New Folder
        '''
        # Click 'New' Button
        new_button = driver.find_element(By.ID, 'newButton')
        new_button.click()

        # Select 'Folder'
        folder_button = driver.find_element(By.XPATH, "//a[text()='Folder']")
        folder_button.click()

        # Wait for the modal to open
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'folderModal'))
        )

        # Enter Folder name 
        folder_input = driver.find_element(By.ID, 'folderNameInput')
        folder_input.send_keys('CSCE 492')

        # Click Create button
        create_button = driver.find_element(By.ID, "create_folder_confirm")
        create_button.click()

        time.sleep(5)

# 3. Rename Folder in Layout Library
class Test03_RenameFolderTestCase(LiveServerTestCase):
    def test03_rename_folder(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Rename Folder
        '''
        # Click on folder menu (three dots button)
        folder_menu = driver.find_element(By.ID, 'folder_menu')
        folder_menu.click()

        # Click on Rename option
        rename_button = driver.find_element(By.ID, 'rename_folder')
        driver.execute_script("arguments[0].scrollIntoView(true);", rename_button)
        time.sleep(1)  # Allow the page to settle
        rename_button.click()

        # Enter new layout name
        name_input = driver.find_element(By.ID, 'new_folder_name')
        name_input.clear()
        name_input.send_keys('Renamed')

        # Click Rename button
        rename_confirm = driver.find_element(By.ID, "rename_folder_confirm")
        rename_confirm.click()

        time.sleep(5)

# 4. Delete Folder in Layout Library
class Test04_DeleteFolderTestCase(LiveServerTestCase):
    def test04_delete_folder(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Delete Folder
        '''
        # Click on folder menu (three dots button)
        folder_menu = driver.find_element(By.ID, 'folder_menu')
        folder_menu.click()

        # Click on Delete option
        delete_button = driver.find_element(By.ID, 'delete_folder')
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
        time.sleep(1)  # Allow the page to settle
        delete_button.click()

        # Click Confirm Delete button
        delete_confirm = driver.find_element(By.ID, "delete_folder_confirm")
        delete_confirm.click()

        time.sleep(5)

# 5. Rename Layout in Layout Library
class Test05_RenameLayoutTestCase(LiveServerTestCase):
    def test05_rename_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        time.sleep(5)

        '''
        Rename Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on Rename option
        rename_button = driver.find_element(By.ID, 'rename_drop')
        driver.execute_script("arguments[0].scrollIntoView(true);", rename_button)
        time.sleep(1)  # Allow the page to settle
        rename_button.click()

        # After opening the rename modal, add a wait for the modal to be visible and the button to be clickable
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "new_name"))
        )

        # Enter new layout name
        name_input = driver.find_element(By.ID, 'new_name')
        name_input.clear()
        name_input.send_keys('Renamed')

        rename_confirm = driver.find_element(By.ID, "rename_layout_confirm")
        rename_confirm.click()

        time.sleep(5)

# 6. Edit Layout in Layout Library
class Test06_EditLayoutTestCase(LiveServerTestCase):
    def test06_edit_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Edit Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on Edit option
        edit_button = driver.find_element(By.ID, 'edit_drop')
        driver.execute_script("arguments[0].scrollIntoView(true);", edit_button)
        time.sleep(1)  # Allow the page to settle
        edit_button.click()

        time.sleep(5)

# 7. Download Layout in Layout Library
class Test07_DownloadLayoutTestCase(LiveServerTestCase):
    def test07_download_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Download Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on Download option
        download_button = driver.find_element(By.ID, 'download_drop')
        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
        time.sleep(1)  # Allow the page to settle
        download_button.click()

        time.sleep(5)

# 8. View Version History in Layout Library
class Test08_ViewHistoryTestCase(LiveServerTestCase):
    def test08_view_history(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Move Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on History option
        history_button = driver.find_element(By.ID, "version_drop")
        driver.execute_script("arguments[0].scrollIntoView(true);", history_button)
        time.sleep(1)  # Allow the page to settle
        history_button.click()

        # Click Close button
        confirm_close = driver.find_element(By.ID, "close_history_button")
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_close)
        time.sleep(1)
        confirm_close.click()

        time.sleep(5)

# 9. Move Layout in Layout Library
class Test09_MoveLayoutTestCase(LiveServerTestCase):
    def test09_move_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Move Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on Move option
        move_button = driver.find_element(By.ID, "move_drop")
        driver.execute_script("arguments[0].scrollIntoView(true);", move_button)
        time.sleep(1)  # Allow the page to settle
        move_button.click()

        # Choose Folder Location
        folder_select = driver.find_element(By.ID, "folderSelect")
        folder_select_dropdown = Select(folder_select)

        # Either select by index (avoiding the current folder)
        folder_select_dropdown.select_by_index(1) 

        # Click Move button
        confirm_move = driver.find_element(By.ID, "move_layout_confirm")
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_move)
        time.sleep(1)
        confirm_move.click()

        time.sleep(5)

# 10. Delete Layout in Layout Library
class Test10_DeleteLayoutTestCase(LiveServerTestCase):
    def test10_delete_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Delete Layout
        '''
        # Click on layout menu (three dots button)
        layout_menu = driver.find_element(By.ID, 'layout_menu')
        layout_menu.click()

        # Click on Delete option
        delete_button = driver.find_element(By.ID, "delete_drop")
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
        time.sleep(1)  # Allow the page to settle
        delete_button.click()

        # After opening the rename modal, add a wait for the modal to be visible and the button to be clickable
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "confirmationModal"))
        )

        # Click Delete button
        confirm_delete = driver.find_element(By.ID, "delete_layout_confirm")
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_delete)
        time.sleep(1)
        confirm_delete.click()

        time.sleep(5)

# 11. Delete All Layouts in Layout Library
class Test11_DeleteAllLayoutsTestCase(LiveServerTestCase):
    def test11_delete_all_layouts(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        '''
        Delete All Layouts
        '''
        # Click on Delete All Layouts button
        delete_button = driver.find_element(By.ID, "delete_all_layouts")
        driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
        time.sleep(1)  # Allow the page to settle
        delete_button.click()

        # Click Delete button
        confirm_delete = driver.find_element(By.ID, "delete_all_layouts_confirm")
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_delete)
        time.sleep(1)
        confirm_delete.click()

        time.sleep(5)


'''
Measurements Page Behavioral Tests
'''
# 1. Convert Layout Test
class Test12_ConvertLayoutTestCase(LiveServerTestCase):
    def test12_convert_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing2')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Measurements Page
        '''
        # Locate the "Measurements Page" navigation link and click it
        measurements_page_link = driver.find_element(By.LINK_TEXT, 'Measure')
        measurements_page_link.click()

        # Wait for the Layout Library page to load
        measurements_page_url = 'https://layoutgenerator.up.railway.app/measure/'
        WebDriverWait(driver, 10).until(EC.url_to_be(measurements_page_url))

        '''
        Input Layout Data
        '''
        # Enter General Information
        layout_name_input = driver.find_element(By.ID, 'layout_name')
        layout_name_input.send_keys('Layout')
        neighborhood_input = driver.find_element(By.ID, 'neighborhood')
        neighborhood_input.send_keys('Neighborhood')
        building_input = driver.find_element(By.ID, 'building')
        building_input.send_keys('Building')
        room_name_input = driver.find_element(By.ID, 'room_name')
        room_name_input.send_keys('Room Name')
        date_input = driver.find_element(By.ID, 'date')
        today_date = datetime.today().strftime('%Y-%m-%d')
        driver.execute_script(f"document.getElementById('date').value = '{today_date}'")

        # Enter Measurement Input
        # Select the type dropdown in the first row and choose "Sensor"
        type_dropdown = driver.find_element(By.CSS_SELECTOR, 'select[name="type[]"]')
        type_dropdown.click()
        sensor_option = driver.find_element(By.XPATH, '//select[@name="type[]"]/option[@value="Sensor"]')
        sensor_option.click()

        # Wait for the descriptor field to be enabled after selecting the type
        descriptor_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="descriptor[]"]'))
        )
        descriptor_input.send_keys('Sens')

        # Enter x coordinate
        x_input = driver.find_element(By.CSS_SELECTOR, 'input[name="x[]"]')
        x_input.send_keys('25')

        # Enter y coordinate
        y_input = driver.find_element(By.CSS_SELECTOR, 'input[name="y[]"]')
        y_input.send_keys('25')

        # Enter scale value
        scale_input = driver.find_element(By.CSS_SELECTOR, 'input[name="scale[]"]')
        scale_input.send_keys('1')

        '''
        Save Changes/Convert Layout
        '''
        # Click the Save Layout button
        save_button = driver.find_element(By.ID, 'convert')
        save_button.click()

        # Wait for the URL to change to the export page (which will have a URL containing "/export/")
        WebDriverWait(driver, 10).until(
            lambda driver: driver.current_url.startswith('https://layoutgenerator.up.railway.app/export/')
        )

        time.sleep(5)

# 2. Refresh Layout Test
class Test13_RefreshLayoutTestCase(LiveServerTestCase):
    def test13_refresh_layout(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing2')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Measurements Page
        '''
        # Locate the "Measurements Page" navigation link and click it
        measurements_page_link = driver.find_element(By.LINK_TEXT, 'Measure')
        measurements_page_link.click()

        # Wait for the Layout Library page to load
        measurements_page_url = 'https://layoutgenerator.up.railway.app/measure/'
        WebDriverWait(driver, 10).until(EC.url_to_be(measurements_page_url))

        '''
        Input Layout Data
        '''
        # Enter General Information
        layout_name_input = driver.find_element(By.ID, 'layout_name')
        layout_name_input.send_keys('Layout')
        neighborhood_input = driver.find_element(By.ID, 'neighborhood')
        neighborhood_input.send_keys('Neighborhood')
        building_input = driver.find_element(By.ID, 'building')
        building_input.send_keys('Building')
        room_name_input = driver.find_element(By.ID, 'room_name')
        room_name_input.send_keys('Room Name')
        date_input = driver.find_element(By.ID, 'date')
        today_date = datetime.today().strftime('%Y-%m-%d')
        driver.execute_script(f"document.getElementById('date').value = '{today_date}'")

        # Enter Measurement Input
        # Select the type dropdown in the first row and choose "Sensor"
        type_dropdown = driver.find_element(By.CSS_SELECTOR, 'select[name="type[]"]')
        type_dropdown.click()
        sensor_option = driver.find_element(By.XPATH, '//select[@name="type[]"]/option[@value="Sensor"]')
        sensor_option.click()

        # Wait for the descriptor field to be enabled after selecting the type
        descriptor_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="descriptor[]"]'))
        )
        descriptor_input.send_keys('Sens')

        # Enter x coordinate
        x_input = driver.find_element(By.CSS_SELECTOR, 'input[name="x[]"]')
        x_input.send_keys('25')

        # Enter y coordinate
        y_input = driver.find_element(By.CSS_SELECTOR, 'input[name="y[]"]')
        y_input.send_keys('25')

        # Enter scale value
        scale_input = driver.find_element(By.CSS_SELECTOR, 'input[name="scale[]"]')
        scale_input.send_keys('1')

        '''
        Refresh Layout Preview
        '''
        # Click the Refresh Layout button
        refresh_button = driver.find_element(By.ID, 'refresh')
        driver.execute_script("arguments[0].scrollIntoView(true);", refresh_button)
        time.sleep(1)  # Allow the page to settle
        refresh_button.click()

        time.sleep(5)

# 3. View Layout in Browser Test
class Test14_ViewInBrowserTestCase(LiveServerTestCase):
    def test14_view_in_browser(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing2')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Measurements Page
        '''
        # Locate the "Measurements Page" navigation link and click it
        measurements_page_link = driver.find_element(By.LINK_TEXT, 'Measure')
        measurements_page_link.click()

        # Wait for the Layout Library page to load
        measurements_page_url = 'https://layoutgenerator.up.railway.app/measure/'
        WebDriverWait(driver, 10).until(EC.url_to_be(measurements_page_url))

        '''
        Input Layout Data
        '''
        # Enter General Information
        layout_name_input = driver.find_element(By.ID, 'layout_name')
        layout_name_input.send_keys('Layout')
        neighborhood_input = driver.find_element(By.ID, 'neighborhood')
        neighborhood_input.send_keys('Neighborhood')
        building_input = driver.find_element(By.ID, 'building')
        building_input.send_keys('Building')
        room_name_input = driver.find_element(By.ID, 'room_name')
        room_name_input.send_keys('Room Name')
        date_input = driver.find_element(By.ID, 'date')
        today_date = datetime.today().strftime('%Y-%m-%d')
        driver.execute_script(f"document.getElementById('date').value = '{today_date}'")

        # Enter Measurement Input
        # Select the type dropdown in the first row and choose "Sensor"
        type_dropdown = driver.find_element(By.CSS_SELECTOR, 'select[name="type[]"]')
        type_dropdown.click()
        sensor_option = driver.find_element(By.XPATH, '//select[@name="type[]"]/option[@value="Sensor"]')
        sensor_option.click()

        # Wait for the descriptor field to be enabled after selecting the type
        descriptor_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="descriptor[]"]'))
        )
        descriptor_input.send_keys('Sens')

        # Enter x coordinate
        x_input = driver.find_element(By.CSS_SELECTOR, 'input[name="x[]"]')
        x_input.send_keys('25')

        # Enter y coordinate
        y_input = driver.find_element(By.CSS_SELECTOR, 'input[name="y[]"]')
        y_input.send_keys('25')

        # Enter scale value
        scale_input = driver.find_element(By.CSS_SELECTOR, 'input[name="scale[]"]')
        scale_input.send_keys('1')

        '''
        Refresh Layout Preview
        '''
        # Click the Refresh Layout button
        refresh_button = driver.find_element(By.ID, 'refresh')
        driver.execute_script("arguments[0].scrollIntoView(true);", refresh_button)
        time.sleep(1)  # Allow the page to settle
        refresh_button.click()

        time.sleep(5)

        '''
        View Layout in Browser
        '''
        # Click 'View in browser' button
        view_in_browser_button = driver.find_element(By.CLASS_NAME, 'canvas-link')
        driver.execute_script("arguments[0].scrollIntoView(true);", view_in_browser_button)
        time.sleep(1)  # Allow the page to settle
        view_in_browser_button.click()

        time.sleep(5)


'''
Canvas Page Behavioral Tests
'''
# 1. Draw Line in the Canvas
class Test15_DrawLineTestCase(LiveServerTestCase):
    def test15_draw_line(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing3')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Canvas Page
        '''
        # Locate the "Canvas Page" navigation link and click it
        canvas_page_link = driver.find_element(By.LINK_TEXT, 'Draw')
        canvas_page_link.click()

        # Wait for the Layout Library page to load
        canvas_page_url = 'https://layoutgenerator.up.railway.app/canvas-page/'
        WebDriverWait(driver, 10).until(EC.url_to_be(canvas_page_url))
        
        '''
        Draw a Line on Canvas
        '''
        # Wait for canvas element to be visible
        canvas = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'canvas'))
        )
        
        # Select solid line type
        solid_line_button = driver.find_element(By.ID, 'solidLineButton')
        solid_line_button.click()
        
        # Give the page a moment to register the button click
        time.sleep(1)
        
        # Use a safer approach - directly click on the canvas instead of calculating offsets
        # First, get the canvas location and size
        canvas_location = canvas.location
        canvas_size = canvas.size
        
        # Calculate safe coordinates (20% and 80% of canvas dimensions)
        # This ensures we stay within bounds while still making a visible line
        start_x = int(canvas_size['width'] * 0.2)
        start_y = int(canvas_size['height'] * 0.2)
        end_x = int(canvas_size['width'] * 0.6)  # Move by 40% of width
        end_y = int(canvas_size['height'] * 0.6)  # Move by 40% of height
        
        # Use the direct approach to click on canvas and drag
        actions = ActionChains(driver)
        actions.move_to_element(canvas)  # First move to canvas element itself
        actions.move_by_offset(start_x - canvas_size['width']/2, start_y - canvas_size['height']/2)  # Move to start position
        actions.click_and_hold()
        actions.move_by_offset(end_x - start_x, end_y - start_y)  # Draw the line
        actions.release()
        actions.perform()
        
        time.sleep(5)

# 2. Drop Object in the Canvas
class Test16_DropObjectTestCase(LiveServerTestCase):
    def test16_drop_object(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing3')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Canvas Page
        '''
        # Locate the "Canvas Page" navigation link and click it
        canvas_page_link = driver.find_element(By.LINK_TEXT, 'Draw')
        canvas_page_link.click()

        # Wait for the Layout Library page to load
        canvas_page_url = 'https://layoutgenerator.up.railway.app/canvas-page/'
        WebDriverWait(driver, 10).until(EC.url_to_be(canvas_page_url))
        
        '''
        Drop an Object in Canvas
        '''
        # Get the source element (black circle object)
        source_element = driver.find_element(By.ID, 'circleButton')

        # Get the target canvas element
        canvas = driver.find_element(By.ID, 'canvas')

        # Create an ActionChains object
        actions = ActionChains(driver)

        # Drag and drop operation using ActionChains
        # Since native HTML5 drag and drop might not work perfectly with Selenium,
        # we can use the following workaround for better reliability:
        actions.click_and_hold(source_element)
        actions.move_to_element(canvas)
        actions.move_by_offset(50, 50)  # Move a bit within the canvas to ensure proper placement
        actions.release()
        actions.perform()
        
        time.sleep(5)

# 3. Convert Drawing to Layout
class Test17_ConvertDrawingTestCase(LiveServerTestCase):
    def test17_convert_drawing(self):
        '''
        Initialize WebDriver
        '''
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get('https://layoutgenerator.up.railway.app/auth-page/')

        '''
        Sign In
        '''
        # Locate the username and password input fields
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')

        # Enter testing credentials
        username_input.send_keys('testing3')
        password_input.send_keys('fp*%ELXf9A#y%*9&f9')

        # Locate the "Sign In" button and click it
        login_button = driver.find_element(By.ID, 'signinbutton')
        login_button.click()

        # Wait for the expected URL
        expected_url = 'https://layoutgenerator.up.railway.app/import/'
        WebDriverWait(driver, 10).until(EC.url_to_be(expected_url))

        '''
        Navigate to Canvas Page
        '''
        # Locate the "Canvas Page" navigation link and click it
        canvas_page_link = driver.find_element(By.LINK_TEXT, 'Draw')
        canvas_page_link.click()

        # Wait for the Layout Library page to load
        canvas_page_url = 'https://layoutgenerator.up.railway.app/canvas-page/'
        WebDriverWait(driver, 10).until(EC.url_to_be(canvas_page_url))

        '''
        Input Layout's General Information
        '''
        layout_name_input = driver.find_element(By.ID, 'layout_name')
        layout_name_input.send_keys('Layout')
        neighborhood_input = driver.find_element(By.ID, 'neighborhood')
        neighborhood_input.send_keys('Neighborhood')
        building_input = driver.find_element(By.ID, 'building')
        building_input.send_keys('Building')
        room_name_input = driver.find_element(By.ID, 'room_name')
        room_name_input.send_keys('Room Name')
        date_input = driver.find_element(By.ID, 'date')
        today_date = datetime.today().strftime('%Y-%m-%d')
        driver.execute_script(f"document.getElementById('date').value = '{today_date}'")

        time.sleep(5)

        '''
        Save Changes/Convert Layout
        '''
        # Click the Save Layout button
        save_button = driver.find_element(By.ID, 'convert')
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
        driver.execute_script("document.getElementById('convert').removeAttribute('disabled')")
        driver.execute_script("document.getElementById('convert').classList.remove('disabled')")
        time.sleep(1)  # Allow the page to settle
        save_button.click()
        
        time.sleep(5)

        '''
        Navigate to Layout Library
        '''
        # Locate the "Layout Library" navigation link and click it
        layout_library_link = driver.find_element(By.LINK_TEXT, 'Layout Library')
        driver.execute_script("arguments[0].scrollIntoView(true);", layout_library_link)
        time.sleep(1)  # Allow the page to settle
        layout_library_link.click()

        # Wait for the Layout Library page to load
        layout_library_url = 'https://layoutgenerator.up.railway.app/layout-library/'
        WebDriverWait(driver, 10).until(EC.url_to_be(layout_library_url))

        time.sleep(5)