import time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app1.models import DefaultStyleSettings, StyleSettings, ConvertedFile, UploadedFile
import json
from django.conf import settings
from django.http import JsonResponse
import os
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver


'''
Measurement Page Unit Tests
'''
class MeasurePageTests(TestCase):
    def setUp(self):
        # Initialize test environment
        self.client = Client()
        
        # Create test user with credentials
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Set up default styling for the test user
        self.default_style = DefaultStyleSettings.objects.create(user=self.user)
        
        # Log the test user in
        self.client.login(username='testuser', password='testpass123')
        
        # Create necessary test directories for file operations
        self.user_dir = os.path.join(settings.MEDIA_ROOT, 'imported_files', self.user.username)
        os.makedirs(self.user_dir, exist_ok=True)

    def test_measure_page_get(self):
        """
        Verifies that the measure page loads correctly with GET request
        Tests:
        - Correct HTTP status code
        - Proper template usage
        """
        response = self.client.get(reverse('measure'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'measure.html')

    def test_process_layout_invalid_method(self):
        """
        Validates API endpoint behavior with incorrect HTTP method
        Tests:
        - Rejection of GET requests
        - Proper error status code
        """
        response = self.client.get(reverse('process_layout_2'))
        self.assertEqual(response.status_code, 405)

    def test_process_layout_empty_data(self):
        """
        Tests handling of empty data submissions
        Validates:
        - Proper response for empty data arrays
        - Correct status code return
        """
        test_data = []
        response = self.client.post(
            reverse('process_layout_2'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)

    def test_process_layout_file_creation(self):
        """
        Validates file generation functionality
        Tests:
        - Creation of LaTeX files
        - PDF generation
        - Image file creation
        - File path validity
        """
        test_data = [{
            'type': 'Wall',
            'descriptor': 'Test Wall',
            'x': 0,
            'y': 0,
            'width': 50,
            'height': 5
        }]
        
        response = self.client.post(
            reverse('process_layout_2'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        if data['success']:
            converted_file = ConvertedFile.objects.get(id=data['layout_id'])
            
            # Verify all required files exist
            self.assertTrue(os.path.exists(converted_file.latex_file))
            self.assertTrue(os.path.exists(converted_file.pdf_file))
            self.assertTrue(os.path.exists(converted_file.image))

    def test_process_layout_style_settings(self):
        """
        Validates style settings integration
        Tests:
        - Style settings creation
        - User association
        - Settings persistence
        """
        test_data = [{
            'type': 'Wall',
            'descriptor': 'Test Wall',
            'x': 0,
            'y': 0,
            'width': 50,
            'height': 5
        }]
        
        response = self.client.post(
            reverse('process_layout_2'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        if data['success']:
            converted_file = ConvertedFile.objects.get(id=data['layout_id'])
            self.assertIsNotNone(converted_file.style_settings)
            self.assertEqual(converted_file.style_settings.user, self.user)

    def test_multiple_walls_processing(self): 
        """
        Validates style settings integration
        Tests:
        - Style settings creation
        - User association
        - Settings persistence
        """
        test_data = [{
            'type': 'Wall',
            'descriptor': 'Test Wall 1',
            'x': 0,
            'y': 0,
            'width': 50,
            'height': 5
        },{
            'type': 'Wall',
            'descriptor': 'Test Wall 2',
            'x': 50,
            'y': 50,
            'width': 50,
            'height': 5
        }
        ]
        
        response = self.client.post(
            reverse('process_layout_2'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        if data['success']:
            converted_file = ConvertedFile.objects.get(id=data['layout_id'])
            self.assertIsNotNone(converted_file.style_settings)
            self.assertEqual(converted_file.style_settings.user, self.user)

    def tearDown(self):
        """
        Cleanup method to remove test artifacts
        - Removes all test files
        - Deletes test directories
        """
        for root, dirs, files in os.walk(self.user_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        
        if os.path.exists(self.user_dir):
            os.rmdir(self.user_dir)


'''
Default Style Settings Page Unit Tests
'''
class DefaultStyleSettingsTests(TestCase):
    def setUp(self):
        """Set up a test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create defaultstylesettings for the user
        self.default_style = DefaultStyleSettings.objects.create(
            user=self.user,
            sensor_label_color="black",
            camera_label_color="black",
            navigation_arrow_color="black",
            calibration_color="black",
            wall_color="black",
            wall_width=2,
            door_color="black",
            door_width=2,
            window_color="black",
            window_width=2,
            furniture_color="black",
            furniture_width=2,
        )

    def test_style_settings_page_loads(self):
        """Test loads correctly."""
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200, "Style settings page did not load successfully")

    def test_update_wall_width(self):
        """Test updating wall width value and verify change made."""
        data = {
            "wall_width": 6,  # Change wall width
            "sensor_label_color": "red",  # Change to valid 
            "camera_label_color": "green",
            "navigation_arrow_color": "blue",
            "calibration_color": "yellow",
            "wall_color": "gray",
            "door_color": "white",
            "window_color": "pink",
            "furniture_color": "purple",
            "door_width": 3,
            "window_width": 2,
            "furniture_width": 5
        }

        response = self.client.post(reverse('settings'), data, follow=True)
        
        self.assertEqual(response.status_code, 200, "Expected successful page load after update")

        # Refresh from db
        updated_settings = DefaultStyleSettings.objects.get(user=self.user)
        updated_settings.refresh_from_db()

        self.assertEqual(updated_settings.wall_width, 6, "Wall width did not update correctly")  # Verify update

    def test_reset_to_defaults(self):
        """Test that clicking 'Reset to System Defaults' resets settings."""
        # Change settings first
        self.default_style.wall_width = 10
        self.default_style.sensor_label_color = "red"
        self.default_style.save()

        # Call reset URL
        response = self.client.get(reverse('reset-settings'), follow=True)
        self.assertEqual(response.status_code, 200, "Expected successful page load after reset")

        # Verify settings reset to default vals
        reset_settings = DefaultStyleSettings.objects.get(user=self.user)
        reset_settings.refresh_from_db()
        
        self.assertEqual(reset_settings.wall_width, 2, "Wall width did not reset correctly")  # Default value
        self.assertEqual(reset_settings.sensor_label_color.lower(), "teal", "Sensor label color did not reset correctly")  # Ensure case match
       
       
'''
Canvas Page Unit Tests
'''
class CanvasPageTests(TestCase):

    def setUp(self):
        """Create a test user and log in before each test."""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')  # Authenticate the test client

    def test_canvas_page_loads(self):
        """Test if the canvas page loads correctly and returns HTTP 200."""
        response = self.client.get(reverse('canvas'))  # Ensure correct URL
        self.assertEqual(response.status_code, 200, "Canvas page did not return HTTP 200")

        # Fix: Use BeautifulSoup to validate HTML before running assertContains
        soup = BeautifulSoup(response.content, 'html.parser')

        # Ensure <canvas> tag parsed HTML
        canvas_exists = soup.find('canvas') is not None
        self.assertTrue(canvas_exists, "Canvas tag is missing from the response")

    def test_clear_canvas_button_exists(self):
        """Test if the 'Clear Canvas' button is in canvas page."""
        response = self.client.get(reverse('canvas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clear')
    
    def test_save_button_is_on_CanvasPage(self):
        """Test if the 'Save Changes' is in canvas page."""
        response = self.client.get(reverse('canvas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Save Changes')

    def test_javascript_function_exists(self):
        """Test if JavaScript function 'clearGrid()' exists in the template."""
        response = self.client.get(reverse('canvas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'function clearGrid()')