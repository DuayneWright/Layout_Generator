from django.db import models
from django.contrib.auth.models import User
from layoutGenerator import settings
import os
import uuid
from django.utils import timezone
from django.urls import (
    reverse,
)  # Generate URLs of individual objects through reversing URL patterns

# Create your models here.

# User model is predefined by Django, containing all necessary fields

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from datetime import datetime
from django.utils import timezone

def get_user_subfolder(instance, filename):
    # Returns the path to a user's specific subfolder in 'imported_files'
    return f'imported_files/{instance.user.username}/{filename}'


# Represents an uploaded file, storing a predefined file imported by the user to be converted into a LaTeX / PDF file
class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Identifier of user who uploaded file
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp indicating when file was uploaded

    # Original file uploaded by user
    file = models.FileField(
        upload_to=get_user_subfolder,
        default="placeholder.txt",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["xlsx", "json", "csv", "xls"])
        ],
    )

    file_name = models.CharField(max_length=255, default="")

    file_path = models.CharField(
        max_length=255, blank=True
    )  # Path to uploaded file on server

    def save(self, *args, **kwargs):
        # Set default value for file_name to the uploaded file's name
        if not self.file_name:
            self.file_name = self.file.name.replace(" ", "_")

        # Create a subdirectory for user in 'imported_files' if it does not exist
        user_folder = os.path.join(settings.MEDIA_ROOT, 'imported_files', self.user.username)
        os.makedirs(user_folder, exist_ok=True)

        super(UploadedFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.file_name


# Represents the settings for styling associated with an individual layout
class StyleSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, default="name")

    FONT_CHOICES = [
        ('Computer Modern', 'Default (Computer Modern)'),
        ('Times New Roman', 'Times New Roman'),
        ('Arial', 'Arial'),
    ]
    
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('green!60!black', 'Dark Green'),
        ('blue', 'Blue'),
        ('blue!75!black', 'Dark Blue'),
        ('cyan', 'Cyan'),
        ('magenta', 'Magenta'),
        ('yellow', 'Yellow'),
        ('black', 'Black'),
        ('gray', 'Gray'),
        ('white', 'White'),
        ('darkgray', 'Dark Gray'),
        ('lightgray', 'Light Gray'),
        ('brown', 'Brown'),
        ('lime', 'Lime'),
        ('olive', 'Olive'),
        ('orange', 'Orange'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('teal', 'Teal'),
        ('violet', 'Violet'),
    ]

    # Text labels
    font_type = models.CharField(max_length=32, default='Computer Modern', choices=FONT_CHOICES) # Font type
    font_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)

    # Colors using predefied latex values
    wall_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    door_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    furniture_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    window_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    sensor_label_color = models.CharField(max_length=32, default='teal', choices=COLOR_CHOICES)
    camera_label_color = models.CharField(max_length=32, default='blue!75!black', choices=COLOR_CHOICES)
    navigation_arrow_color = models.CharField(max_length=32, default='green!60!black', choices=COLOR_CHOICES)
    calibration_color = models.CharField(max_length=32, default='violet', choices=COLOR_CHOICES)

    # Boundary widths
    wall_width = models.IntegerField(default=2)
    door_width = models.IntegerField(default=1)
    furniture_width = models.DecimalField(max_digits=3, decimal_places=1, default=0.5)
    window_width = models.IntegerField(default=1)

    # Metadata styling
    meta_title = models.CharField(max_length=64, default="Layout", blank=False)
    meta_date = models.DateField(default=timezone.now)
    meta_location = models.TextField(max_length=256, default="Address", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    ORIENTATION_CHOICES = [
        ('portrait', "Portrait"),
        ('landscape', "Landscape"),
    ]

    # Orientation of PDF - portrait or landscape
    orientation = models.CharField(max_length=32, default = 'portrait', choices=ORIENTATION_CHOICES)
    class Meta:
        unique_together = ['user', 'name']


# Stores default style settings for users, providing defaults for each layout they generate
class DefaultStyleSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    FONT_CHOICES = [
        ('Computer Modern', 'Default (Computer Modern)'),
        ('Times New Roman', 'Times New Roman'),
        ('Arial', 'Arial'),
    ]
    
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('green!60!black', 'Dark Green'),
        ('blue', 'Blue'),
        ('blue!75!black', 'Dark Blue'),
        ('cyan', 'Cyan'),
        ('magenta', 'Magenta'),
        ('yellow', 'Yellow'),
        ('black', 'Black'),
        ('gray', 'Gray'),
        ('white', 'White'),
        ('darkgray', 'Dark Gray'),
        ('lightgray', 'Light Gray'),
        ('brown', 'Brown'),
        ('lime', 'Lime'),
        ('olive', 'Olive'),
        ('orange', 'Orange'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('teal', 'Teal'),
        ('violet', 'Violet'),
    ]

    # Text labels
    font_type = models.CharField(max_length=32, default='Computer Modern', choices=FONT_CHOICES) # Font type
    font_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)

    # Colors using predefied latex values
    wall_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    door_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    furniture_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    window_color = models.CharField(max_length=32, default='black', choices=COLOR_CHOICES)
    sensor_label_color = models.CharField(max_length=32, default='teal', choices=COLOR_CHOICES)
    camera_label_color = models.CharField(max_length=32, default='blue!75!black', choices=COLOR_CHOICES)
    navigation_arrow_color = models.CharField(max_length=32, default='green!60!black', choices=COLOR_CHOICES)
    calibration_color = models.CharField(max_length=32, default='violet', choices=COLOR_CHOICES)

    # Boundary widths
    wall_width = models.IntegerField(default=2)
    door_width = models.IntegerField(default=1)
    furniture_width = models.DecimalField(max_digits=3, decimal_places=1, default=0.5)
    window_width = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    # called when user resets style settings back to default
    @classmethod
    def reset_to_defaults(cls, user):
        # Define your default values here
        default_values = {
            'wall_color': 'black',
            'door_color': 'black',
            'furniture_color': 'black',
            'window_color': 'black',
            'sensor_label_color': 'teal',
            'camera_label_color': 'blue!75!black',
            'navigation_arrow_color': 'green!60!black',
            'calibration_color': 'violet',
            'wall_width': 2,
            'door_width': 1,
            'furniture_width': 0.5,
            'window_width': 1
        }
        
        style_settings_instance, _ = cls.objects.get_or_create(user=user)
        
        for field, value in default_values.items():
            setattr(style_settings_instance, field, value)
        style_settings_instance.save()


from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    folder_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=500)
    parent_directory = models.CharField(max_length=255, blank=True, null=True)
    full_path = models.CharField(max_length=500, blank=True, null=True)
    folders = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    files = models.ManyToManyField(UploadedFile)

    def save(self, *args, **kwargs):
        # Normalize the parent_directory (remove leading/trailing slashes)
        if self.parent_directory:
            self.parent_directory = self.parent_directory.strip('/')
            self.full_path = f"{self.parent_directory}/{self.folder_name}"
        else:
            self.full_path = self.folder_name
        
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'full_path']

# Stores generated LaTeX code and reference to original file
class ConvertedFile(models.Model):
    file_name = models.CharField(max_length=255, default="name") # Stores the PREFIX (without extension)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)   # Automatically updated to current date and time when saved
    file_path = models.CharField(max_length=255, default="NONE")
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True)
    temporary = models.BooleanField(default=False)


    # link to associated StyleSettings
    style_settings = models.ForeignKey(StyleSettings, on_delete=models.CASCADE,
                                       null=True)

    # Link to associated UploadedFile
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, null=True)

    # Reference to latex file in form 'uploads/imported_files/<username>/file_name.tex'
    latex_file = models.CharField(max_length=255,
                                  default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.tex'))

    # Reference to PDF file in form 'uploads/imported_files/<username>/file_name.pdf
    pdf_file = models.CharField(max_length=255,
                                default= os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.pdf'))
    
    # Reference to PNG in form 'uploads/imported_files/<username>/file_name.png
    image = models.CharField(max_length=255,
                             default = os.path.join(settings.MEDIA_ROOT,'conversion_output', 'output.png'))

    layout = models.ForeignKey('Layout', on_delete=models.CASCADE, null=True, blank=True) # Link to Layout 
    
    # Csv and json download links
    csv_file = models.CharField(max_length=255, null=True, blank=True)
    json_file = models.CharField(max_length=255, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.uploaded_file.file_name

        if not self.created_at:
            self.created_at = timezone.now()
        self.last_modified = timezone.now()

        # Store relative paths for web serving
        user_relative_path = f'imported_files/{self.user.username}'
        self.latex_file = f'{user_relative_path}/{self.file_name}.tex'
        self.pdf_file = f'{user_relative_path}/{self.file_name}.pdf'
        self.image = f'{user_relative_path}/{self.file_name}.png'
        
        # Store absolute path for file operations
        user_directory = os.path.join(settings.MEDIA_ROOT, 'imported_files', self.user.username)
        self.file_path = os.path.join(user_directory, f"{self.file_name}.xlsx")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name
    
    def convert_to_latex(self):
        try:
            # Retrieve the user's default style settings
            default_style_settings = DefaultStyleSettings.objects.get(user=self.user)
            
            # Call the conversion function with the default style settings
            latex_code = conversion(self.file, default_style_settings)
            
            # Return or save the LaTeX code as needed
        except DefaultStyleSettings.DoesNotExist:
            # Handle case where default style settings are not found
            print("Default style settings not found for the user.")

    # retrieve all labels associated with file
    def get_labels(self):
        return self.label_set.all()


# Stores the x and y coordinates of a label
class Label(models.Model):
        LABEL_LOCATIONS = [
            ('above', 'Above'),
            ('below', 'Below'),
            ('left', 'Left'),
            ('right', 'Right')
        ]

        file = models.ForeignKey(ConvertedFile, on_delete=models.CASCADE)
        name = models.CharField(max_length=100)
        location = models.CharField(max_length=5, default="above", choices=LABEL_LOCATIONS)
        type = models.CharField(max_length=20, default="Sensor")


# Store General Information about Layout
class Layout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    file = models.ForeignKey(ConvertedFile, on_delete=models.CASCADE, null=True, blank=True, related_name='layout_reference') # Link to file
    neighborhood = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    step = models.IntegerField(default=24)
    orientation = models.CharField(max_length=10, choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')], default='portrait')

    def __str__(self):
        return f"{self.neighborhood} - {self.building} - {self.room_name}"
    

# Layout's Measurements
class Measurement(models.Model):
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # General fields
    layout = models.ForeignKey('Layout', on_delete=models.CASCADE, related_name='measurements') # Link to Layout 
    TYPE_CHOICES = [
        ('Wall', 'Wall'),
        ('Door', 'Door'),
        ('Window', 'Window'),
        ('Furniture', 'Furniture'),
        ('Calibration', 'Calibration'),
        ('Camera', 'Camera'),
        ('Room Navigation', 'Room Navigation'),
        ('Sensor', 'Sensor'),
    ]
    DIRECTION_CHOICES = [
        ('Left', 'Left'),
        ('Right', 'Right'),
        ('Up', 'Up'),
        ('Down', 'Down'),
    ]
    FURNITURE_CHOICES = [
        ('Rectangle', 'Rectangle'),
        ('Circle', 'Circle'),
    ]
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    descriptor = models.CharField(max_length=255, null=True, blank=True)
    x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    radius = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scale = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rotation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    furniture_type = models.CharField(max_length=100, choices=FURNITURE_CHOICES, null=True, blank=True)
    room_navigation_direction = models.CharField(max_length=100, choices=DIRECTION_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.descriptor}"


# Layout's Version History
class LayoutHistory(models.Model):
    ACTION_CHOICES = [
        ('RENAME', 'Renamed'),
        ('EDIT', 'Edited'),
        ('MOVE', 'Moved'),
        ('CONVERT', 'Converted')
    ]
    
    layout = models.ForeignKey(ConvertedFile, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_value = models.CharField(max_length=255, blank=True)  # Store old name/path
    new_value = models.CharField(max_length=255)  # Store new name/path
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-timestamp']


# Canvas Content
class CanvasLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Canvas Layout by {self.user.username} (updated: {self.updated_at})"