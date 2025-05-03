from django.shortcuts import render, redirect
from .models import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages, admin
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import get_valid_filename
from shutil import copyfile
from django.conf import settings
from django.core.files.storage import default_storage

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import UploadedFile, ConvertedFile, StyleSettings, DefaultStyleSettings, Label
from django.shortcuts import HttpResponse
from django.http import HttpResponseNotFound
import zipfile
import app1.latex_conversion as lc
import app1.edit_latex_conversion as elc
import six
from django.http import HttpResponseRedirect

# Modules for handling file validation:
from django.http import HttpResponseBadRequest
from django.http import JsonResponse

# Sending email for password reset
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db import transaction
import logging
logger = logging.getLogger(__name__)

import shutil

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

#access current date
from datetime import date

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

token_generator = TokenGenerator()

# %******************** Home Page ****************************%

# Home page view of the website, where users can upload a file
@login_required(login_url="auth-page")
def ImportPage(request):

    # Ensure request is a POST and that a file was uploaded:
    if request.method == "POST" and request.FILES:
        uploaded_file_path = None # Define uploaded filepath
        # Ensure atomicity
        try:
            with transaction.atomic():

                # get uploaded file from POST request
                uploaded_file = request.FILES["uploaded_file"]
                username = request.user.username

                # Get file extension of uploaded file
                file_extension = uploaded_file.name.split('.')[-1] 
                valid_extensions = ['xlsx', 'json', 'csv']
     
                # Create variable for uploaded file path --> "uploads/imported_files/<username>"
                uploaded_files_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username)

                # Determine if a file with the same prefix already exists by searching for it within uploads/imported_files/<username>
                uploaded_filename = get_valid_filename(uploaded_file.name)
                prefix , _ = os.path.splitext(uploaded_filename)  # getting prefix
                converted_filename = f"{prefix}.xlsx"   # appending .xlsx
                duplicate_file_path = os.path.join(uploaded_files_path, converted_filename)  # create file path of duplicate file

                # Ensure file ends with a valid extension
                if file_extension not in valid_extensions:
                    messages.info(request, "Invalid file format. Please upload a file with valid extension (xlsx, json, or csv).")
                # Ensure that an existing file does not exist with the same prefix
                elif os.path.exists(duplicate_file_path):
                    messages.info(request, "File with the same name already exists. Please choose a different file name.")
                else:
                    # file validation & file duplication checks both passed

                    # Rename file to have no spaces
                    uploaded_file.name = get_valid_filename(uploaded_file.name)

                    # Create an UploadedFile instance with base fileS
                    uploaded_file_instance = UploadedFile(
                        file=uploaded_file,
                        user=request.user,
                        )

                    # Define path to uploaded JSON/CSV file - /uploads/imported_files/<filename>
                    uploaded_filename = uploaded_file_instance.file.name
                    uploaded_file_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, uploaded_filename)

                    # Save UploadedFile instance to server
                    uploaded_file_instance.file_name = uploaded_filename
                    uploaded_file_instance.save()

                    # Rename file
                    prefix_filename, _ = os.path.splitext(uploaded_filename)
                    converted_filename = f"{prefix_filename}.xlsx"

                    # Convert file from CSV/JSON to Excel
                    if file_extension != 'xlsx':
                        if file_extension == "csv":
                            # Read CSV into a dataframe
                            df = pd.read_csv(uploaded_file_path)

                        if file_extension == "json":
                            try:
                                # Read JSON into a dataframe
                                df = pd.read_json(uploaded_file_path)
                            except ValueError as e:
                                print("Error: File is not valid JSON")
                                messages.error(request, "Uploaded file does not follow valid JSON syntax. Please ensure that all input is derived from valid JavaScript object notation.")
                                uploaded_csvjson_filepath = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, uploaded_filename)
                                default_storage.delete(uploaded_csvjson_filepath)
                                os.remove(uploaded_file_instance.file_path)
                                uploaded_file_instance.delete()
                                return redirect("import")

                        # Create new Excel workbook at /uploads/imported_files/<filename>.xlsx, relative to MEDIA_ROOT
                        excel_filepath = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, converted_filename)
                        df.to_excel(excel_filepath, index=False)
                        
                        # Update UploadedFile with new converted Excel File
                        with open(excel_filepath, 'rb') as excel_file:
                            # Create ContentFile to hold contents of Excel file
                            excel_content = ContentFile(excel_file.read())
                            
                            # Update UploadedFile instance with:
                            uploaded_file_instance.file_name = converted_filename   # Add .xlsx
                            uploaded_file_instance.file = excel_content # Update file with Excel file contens
                            uploaded_file_instance.file_path = excel_filepath   # Add filepath: uploads/imported_files/<file>.xlsx

                        # Updated path to Excel file
                        uploaded_file_path = excel_filepath
                        uploaded_file_instance.save()

                        # Delete CSV/JSON file
                        uploaded_csvjson_filepath = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, uploaded_filename)
                        default_storage.delete(uploaded_csvjson_filepath)

                    else:
                        # Read JSON into a dataframe
                        df = pd.read_excel(uploaded_file_path)

                        uploaded_file_instance.file_path = uploaded_file_path
                        uploaded_file_instance.save()

                    # Query for DefaultStyleSettings based on user preferences
                    default_styling = DefaultStyleSettings.objects.filter(user=request.user).first()

                    # Check if a StyleSettings object already exists for this user and layout
                    layout_style, created = StyleSettings.objects.update_or_create(
                        user=request.user,
                        name=converted_filename,
                        defaults={
                            'wall_color': default_styling.wall_color,
                            'door_color': default_styling.door_color,
                            'furniture_color': default_styling.furniture_color,
                            'window_color': default_styling.window_color,
                            'navigation_arrow_color': default_styling.navigation_arrow_color,
                            'sensor_label_color': default_styling.sensor_label_color,
                            'camera_label_color': default_styling.camera_label_color,
                            'calibration_color': default_styling.calibration_color,
                            'wall_width': default_styling.wall_width,
                            'door_width': default_styling.door_width,
                            'furniture_width': default_styling.furniture_width,
                            'window_width': default_styling.window_width,
                            'orientation': "portrait"
                        }
                    )

                    if not created:
                        # If the StyleSettings object already existed, update its fields with new values
                        layout_style.wall_color = default_styling.wall_color
                        layout_style.door_color = default_styling.door_color
                        layout_style.furniture_color = default_styling.furniture_color
                        layout_style.window_color = default_styling.window_color
                        layout_style.navigation_arrow_color = default_styling.navigation_arrow_color
                        layout_style.sensor_label_color = default_styling.sensor_label_color
                        layout_style.camera_label_color = default_styling.camera_label_color
                        layout_style.calibration_color = default_styling.calibration_color
                        layout_style.wall_width = default_styling.wall_width
                        layout_style.door_width = default_styling.door_width
                        layout_style.furniture_width = default_styling.furniture_width
                        layout_style.window_width = default_styling.window_width
                        layout_style.orientation = "portrait"
                        layout_style.save()

                    labels_placeholder = None
                    # Call conversion code on file from /uploads/imported_files/<filename>
                    result = lc.conversion(uploaded_file_path, layout_style)
                    success = result['success']
                    error_message = result['message']
                    if not success:
                        try:
                            # Display error message
                            messages.error(request, error_message)
                            print(messages.error)
                            # Delete uploaded file and associated instance
                            os.remove(uploaded_file_instance.file_path)
                            uploaded_file_instance.delete()
                            print("redirecting to import:")
                            return redirect("import")
                        except Exception as e:
                            logger.error("Error occurred while deleting file: %s", e)
                            messages.error(request, "An error occurred while deleting the file.")
    
                    # Place .pdf, .png, and .tex files into user's subfolder at /uploads/imported_files/<username>/
                    prefix_filename, _ = os.path.splitext(uploaded_file_instance.file_name)
                    
                    source_tex_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
                    source_pdf_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
                    source_png_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
                    destination_tex_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.tex")
                    destination_pdf_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.pdf")
                    destination_png_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.png")

                    copyfile(source_tex_path, destination_tex_path)
                    copyfile(source_pdf_path, destination_pdf_path)
                    copyfile(source_png_path, destination_png_path)
                    
                    # Make ConvertedFile to link UploadedFile with output
                    converted_file = ConvertedFile(
                        file_name=prefix_filename, # *NOTE* stores prefix WITHOUT extension
                        user = request.user,
                        file_path = uploaded_file_instance.file_path,
                        uploaded_file = uploaded_file_instance,
                        latex_file = destination_tex_path,
                        pdf_file = destination_pdf_path,
                        style_settings = layout_style,
                        image = destination_png_path,
                        csv_file = uploaded_file_instance.file_path,
                        json_file = uploaded_file_instance.file_path,
                    )
                    converted_file.full_clean()
                    converted_file.save(force_insert=True)

                    # Create Layout instance
                    layout = Layout.objects.create(
                        user=request.user,
                        file=converted_file,
                        neighborhood=df.iloc[1, 1],
                        building=df.iloc[2, 1],
                        room_name=df.iloc[3, 1],
                        date=pd.to_datetime(df.iloc[4, 1]).date(),
                        step=df.iloc[5, 13],  # X Axis row at 13th column
                        orientation=df.iloc[0, 1]
                    )

                    # Update ConvertedFile with the created layout
                    converted_file.layout = layout
                    converted_file.save()

                    for index, row in df.iloc[7:].iterrows():  # Skip first 7 rows to start from the measurements
                        # Replace NaN values with 0
                        measurement = Measurement.objects.create(
                            layout=layout,
                            type=row.get('Type', '') or '',
                            descriptor=row.get('Descriptor', '') or ' ',
                            x=row['X'] if pd.notna(row['X']) else 0,
                            y=row['Y'] if pd.notna(row['Y']) else 0,
                            width=row['width'] if pd.notna(row['width']) else 0,
                            length=row['length'] if pd.notna(row['length']) else 0,
                            radius=row['radius'] if pd.notna(row['radius']) else 0,
                            scale=row['scale'] if pd.notna(row['scale']) else 1,
                            rotation=row['rotation'] if pd.notna(row['rotation']) else 0,
                            furniture_type=row['furniture_type'].capitalize() if pd.notna(row['furniture_type']) else None,
                            room_navigation_direction=row['room_navigation_direction'] if pd.notna(row['room_navigation_direction']) else None
                        )
                        print("\n", row['Type'], row['Descriptor'], row['X'], row['Y'], row['width'], row['length'], row['radius'], row['scale'], row['rotation'], row['furniture_type'], row['room_navigation_direction'])

                    # Create Labels
                    labels = parse_excel_file(converted_file)
                    for label in labels:
                        Label.objects.create(
                            file=converted_file, 
                            name=label['name'], 
                            type=label['type']
                        )
                
                    return redirect("export-layout", layout_id=converted_file.id)
                    
        except Exception as e:
            logger.error("Error occurred during import: %s", e)
            print(e)
            if uploaded_file_path:
                try:
                    os.remove(uploaded_file_path)
                except Exception as delete_error:
                    logger.error("Error occurred while deleting file: %s", delete_error)
            # messages.error(request, "The uploaded file could not be parsed. See provided sample format.")
            return redirect("import")

    return render(request, 'import.html')

# Parse through Excel file to identify labels
def parse_excel_file(converted_file):
    """
    Helper function for ImportPage view that parses the file uploaded by the user and identifies objects that have labels

    Parameters:
        converted_file: ConvertedFile object containing reference to Excel file 
    Returns:
        labels: List of label objects containing a name + type for each label
    """
    # read excel file into df
    df = pd.read_excel(converted_file.file_path)
    # convert df to lowercase first col/row
    df.columns = df.columns.str.lower()
    df['type'] = df['type'].str.lower()

    labels = []

    # iterate over rows in dataframe to extract labels
    for index, row in df.iterrows():
        if row['type'] in ['camera', 'sensor', 'calibration']:
            # extract data for the label
            label_data = {
                'name': row['descriptor'],
                'type': row['type']
            }

            labels.append(label_data)

    return labels

# Download sample Excel file for formating
from django.http import FileResponse
def download_sample_excel(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_excel_format.xlsx')
    response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=example_excel_format.xlsx'
    return response

# Download sample CSV file for formating
def download_sample_csv(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_csv_format.csv')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=example_csv_format.csv'
    return response

#  Download sample JSON file for formating
def download_sample_json(request):
    file_path = os.path.join('uploads', 'sample_files', 'example_json_format.json')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename=example_json_format.json'
    return response

# %******************** Export File Page ****************************%

from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from pathlib import Path
import logging
import zipfile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

def get_safe_file_path(file_path, username):
    """
    Safely resolve and validate file path within user's directory
    """
    try:
        # Convert to Path object
        path = Path(file_path)
        
        # Get the base media root
        media_root = Path(settings.MEDIA_ROOT)
        
        # Expected user directory
        user_dir = media_root / 'imported_files' / username
        
        # If path is absolute, convert to relative to MEDIA_ROOT
        if path.is_absolute():
            try:
                path = path.relative_to(media_root)
            except ValueError:
                logger.error(f"File path {path} is not within MEDIA_ROOT")
                return None
        
        # Construct full path
        full_path = media_root / path
        
        # Resolve to absolute path, removing any '..' etc
        absolute_path = full_path.resolve()
        
        # Verify path is within user's directory
        if not str(absolute_path).startswith(str(user_dir)):
            logger.error(f"Path {absolute_path} is outside of user directory {user_dir}")
            return None
            
        return absolute_path
        
    except Exception as e:
        logger.error(f"Error processing file path {file_path}: {str(e)}")
        return None

# Allows user to download the generated PDF of the current layout
def download_pdf(request, layout_id):
    """Download PDF file with user-specific path handling"""
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    
    # Verify user has permission to access this file
    if layout.user != request.user:
        return HttpResponse("Permission denied", status=403)
    
    file_path = get_safe_file_path(layout.pdf_file, request.user.username)
    
    if not file_path:
        logger.error(f"Invalid PDF file path for layout {layout_id}")
        return HttpResponse("Invalid file path", status=400)
        
    if not file_path.exists():
        logger.error(f"PDF file not found for layout {layout_id}: {file_path}")
        return HttpResponse("File not found", status=404)
    
    try:
        return FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=file_path.name
        )
    except Exception as e:
        logger.error(f"Error serving PDF file {file_path}: {str(e)}")
        return HttpResponse("Error accessing file", status=500)

# Allows user to download the generated LaTex code of the current layout
def download_tex(request, layout_id):
    """Download LaTeX file with user-specific path handling"""
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    
    # Verify user has permission to access this file
    if layout.user != request.user:
        return HttpResponse("Permission denied", status=403)
    
    file_path = get_safe_file_path(layout.latex_file, request.user.username)
    
    if not file_path:
        logger.error(f"Invalid LaTeX file path for layout {layout_id}")
        return HttpResponse("Invalid file path", status=400)
        
    if not file_path.exists():
        logger.error(f"LaTeX file not found for layout {layout_id}: {file_path}")
        return HttpResponse("File not found", status=404)
    
    try:
        return FileResponse(
            open(file_path, 'rb'),
            content_type='application/x-tex',
            as_attachment=True,
            filename=file_path.name
        )
    except Exception as e:
        logger.error(f"Error serving LaTeX file {file_path}: {str(e)}")
        return HttpResponse("Error accessing file", status=500)

# Allows user to download the generated PDF and LaTeX code in a zipped file of the current layout
def download_zip(request, layout_id):
    """Download ZIP with user-specific path handling"""
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    
    # Verify user has permission to access this file
    if layout.user != request.user:
        return HttpResponse("Permission denied", status=403)
    
    pdf_path = get_safe_file_path(layout.pdf_file, request.user.username)
    tex_path = get_safe_file_path(layout.latex_file, request.user.username)
    excel_path = get_safe_file_path(layout.file_path, request.user.username)
    csv_path = get_safe_file_path(layout.csv_file, request.user.username)
    json_path = get_safe_file_path(layout.json_file, request.user.username)
    
    print(f"File paths - PDF: {pdf_path}, TEX: {tex_path}, Excel: {excel_path}, CSV: {csv_path}, JSON: {json_path}")
    
    user_dir = Path(settings.MEDIA_ROOT) / 'imported_files' / request.user.username
    
    # validate whether they exist for the later checks to be valid. 
    if csv_path and not str(csv_path).lower().endswith('.csv'):
        csv_path = None
    if json_path and not str(json_path).lower().endswith('.json'):
        json_path = None
    if excel_path and not any(str(excel_path).lower().endswith(ext) for ext in ['.xlsx', '.xls']):
        excel_path = None

    # Get base filename from the pdf_path
    base_filename = None
    if pdf_path and pdf_path.exists():
        base_filename = pdf_path.stem
    elif tex_path and tex_path.exists():
        base_filename = tex_path.stem
    elif excel_path and excel_path.exists():
        base_filename = excel_path.stem
    elif csv_path and csv_path.exists():
        base_filename = csv_path.stem
    elif json_path and json_path.exists():
        base_filename = json_path.stem

    # Generate missing file formats 
    if excel_path and excel_path.exists():
        # Generate CSV if missing
        if not (csv_path and csv_path.exists()):
            csv_path = user_dir / f"{base_filename}.csv"
            df = pd.read_excel(excel_path)
            df.to_csv(csv_path, index=False)
            layout.csv_file = f"imported_files/{request.user.username}/{base_filename}.csv"
            layout.save()
            
        # Generate JSON if missing
        if not (json_path and json_path.exists()):
            json_path = user_dir / f"{base_filename}.json"
            df = pd.read_excel(excel_path)
            df.to_json(json_path, orient='records')
            layout.json_file = f"imported_files/{request.user.username}/{base_filename}.json"
            layout.save()
            
    # If we have CSV but not Excel or JSON
    elif csv_path and csv_path.exists():
        # Generate Excel if missing
        if not (excel_path and excel_path.exists()):
            excel_path = user_dir / f"{base_filename}.xlsx"
            df = pd.read_csv(csv_path)
            df.to_excel(excel_path, index=False)
            layout.file_path = f"imported_files/{request.user.username}/{base_filename}.xlsx"
            layout.save()
            
        # Generate JSON if missing
        if not (json_path and json_path.exists()):
            json_path = user_dir / f"{base_filename}.json"
            df = pd.read_csv(csv_path)
            df.to_json(json_path, orient='records')
            layout.json_file = f"imported_files/{request.user.username}/{base_filename}.json"
            layout.save()
            
    # If we have JSON but not Excel or CSV
    elif json_path and json_path.exists():
        # Generate Excel if missing
        if not (excel_path and excel_path.exists()):
            excel_path = user_dir / f"{base_filename}.xlsx"
            with open(json_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df.to_excel(excel_path, index=False)
            layout.file_path = f"imported_files/{request.user.username}/{base_filename}.xlsx"
            layout.save()
            
        # Generate CSV if missing
        if not (csv_path and csv_path.exists()):
            csv_path = user_dir / f"{base_filename}.csv"
            with open(json_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
            layout.csv_file = f"imported_files/{request.user.username}/{base_filename}.csv"
            layout.save()
    
    files_to_zip = []
    if pdf_path and pdf_path.exists():
        files_to_zip.append((pdf_path, pdf_path.name))
    if tex_path and tex_path.exists():
        files_to_zip.append((tex_path, tex_path.name))
    if excel_path and excel_path.exists():
        files_to_zip.append((excel_path, excel_path.name))
    if csv_path and csv_path.exists():
        files_to_zip.append((csv_path, csv_path.name))
    if json_path and json_path.exists():
        files_to_zip.append((json_path, json_path.name))
    
    if not files_to_zip:
        logger.error(f"No valid files found for layout {layout_id}")
        return HttpResponse("No files available to download", status=404)
    
    # Need to have checks for csv/excel/JSON uploaded files so that it can generate the missing 
    # files from that check. With this, every type of zip file can have all the types of files rather
    # than just some. 
    try:
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={pdf_path.stem}.zip'
        
        with zipfile.ZipFile(response, 'w') as zipf:
            for file_path, arcname in files_to_zip:
                zipf.write(file_path, arcname)
        return response
    except Exception as e:
        logger.error(f"Error creating zip file for layout {layout_id}: {str(e)}")
        return HttpResponse("Error creating zip file", status=500)

from .forms import UpdateFileNameForm
from shutil import move

# Export page, accessed after a user clicks 'convert' on a layout or selects a layout from the library
@login_required(login_url="auth-page")
def ExportPage(request, layout_id):
    # Retreive layout based on layout id
    layout = ConvertedFile.objects.get(id=layout_id)

    # POST request = user attempting to rename the file
    if request.method == 'POST':
        # Initialize the form for updating file name
        update_file_name_form = UpdateFileNameForm(request.POST, instance=layout)
        if update_file_name_form.is_valid():
            # Update the layout's filename
            new_file_name = update_file_name_form.cleaned_data['new_file_name']
            old_file_name = layout.file_name
            layout.file_name = new_file_name
            # Update the layout's file path to have the new file name
            new_file_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username, new_file_name)
            layout.file_path = f"{new_file_path}.xlsx"
            layout.save()

            # rename associated files in user's uploaded file directory to have new file name
            user_directory = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username)
            for file_extension in ['.pdf', '.tex', '.png', '.xlsx', '.csv', '.json']:
                old_file_path = os.path.join(user_directory, f"{old_file_name}{file_extension}")
                new_file_path = os.path.join(user_directory, f"{new_file_name}{file_extension}")
                if os.path.exists(old_file_path):
                    move(old_file_path, new_file_path)
                
            # Log the change
            LayoutHistory.objects.create(
                layout=layout,
                action='RENAME',
                old_value=old_file_name,
                new_value=new_file_name,
                user=request.user
            )
            
            return redirect('export-layout', layout.id)
        else:
            # Error message is handled within update file name form validation
            pass
    
    # GET request: initialize the filename form on page
    else:
        update_file_name_form = UpdateFileNameForm(instance=layout, initial={'new_file_name': layout.file_name})

    context = {
        'layout': layout,
        'update_file_name_form': update_file_name_form,
    }
    return render(request, 'export.html', context)

# Support view for serving images through Django instead of directly through file system
def serve_image(request, image_path):
    # Ensure the image path is relative to MEDIA_ROOT
    absolute_path = os.path.join(settings.MEDIA_ROOT, image_path.lstrip('/'))
    
    try:
        with open(absolute_path, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type='image/png')
    except FileNotFoundError:
        return HttpResponseNotFound("Image not found")
    
def my_view(request):
    image_url = f"{settings.MEDIA_URL}conversion_output/output.png"
    context = {'layout': {'image': image_url}}
    return render(request, 'measure.html', context)

# %******************** Edit Layout Style Page ****************************%

from .forms import UpdateStyleSettingsForm
from django.shortcuts import render, get_object_or_404, redirect

from .forms import UpdateStyleSettingsForm, LabelForm
from django.shortcuts import render, get_object_or_404, redirect
from django import forms

# Allows user to update the styling of a specific layout
@login_required
def EditLayoutStylePage(request, layout_id):
    layout = get_object_or_404(ConvertedFile, id=layout_id)
    style_settings_instance = layout.style_settings
    labels = layout.get_labels()
    excel_file_path = layout.file_path

    # Helper function to get display name for a color value
    def get_color_display_name(color_value):
        for value, display in style_settings_instance.COLOR_CHOICES:
            if value == color_value:
                return display
        return color_value  # Fallback if not found

    if request.method == "POST":
        # Refresh action
        if 'refresh' in request.POST:
            logger.info("Refresh action triggered")
            
            form = UpdateStyleSettingsForm(request.POST, instance=style_settings_instance)
            orientation = request.POST.get('orientation')
            style_settings_instance.orientation = orientation
            style_settings_instance.save()
            label_forms = [LabelForm(request.POST, prefix=str(label.id)) for label in labels]

            if form.is_valid() and all(label_form.is_valid() for label_form in label_forms):
                for label, label_form in zip(labels, label_forms):
                    label.location = label_form.cleaned_data['location']

                result = elc.conversion(excel_file_path, style_settings_instance, labels)

                username = request.user.username

                # Copy files to user's folder for refresh preview
                source_tex_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
                source_pdf_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
                source_png_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
                
                # Create relative paths for storage in the database
                relative_path = f'imported_files/{username}/refresh_image'
                
                # Create absolute paths for file operations
                destination_tex_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, 'refresh_image.tex')
                destination_pdf_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, 'refresh_image.pdf')
                destination_png_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, 'refresh_image.png')

                # Perform file operations with absolute paths
                copyfile(source_tex_path, destination_tex_path)
                copyfile(source_pdf_path, destination_pdf_path)
                copyfile(source_png_path, destination_png_path)           

                # Store relative paths in the layout object
                layout.latex_file = f'{relative_path}.tex'
                layout.image = f'{relative_path}.png'
                layout.pdf_file = f'{relative_path}.pdf'

                context = {
                    'layout': layout,
                    'form': form,
                    'labels': labels,
                    'label_data': zip(labels, label_forms),
                    'orientation_form': forms.CharField(initial=orientation, widget=forms.HiddenInput()),
                    'orientation_value': orientation,
                }
                return render(request, "edit-style.html", context)

            else:
                form_errors = form.errors.as_data()
                label_form_errors = [label_form.errors.as_data() for label_form in label_forms]
                print("Form errors:", form_errors)
                print("Label form errors:", label_form_errors)

        else:
            # Regular form submission 
            form = UpdateStyleSettingsForm(request.POST, instance=style_settings_instance)
            orientation = request.POST.get('orientation')

            # Store old values before making changes
            old_values = {
                'orientation': style_settings_instance.orientation,
                'wall_color': style_settings_instance.wall_color,
                'door_color': style_settings_instance.door_color,
                'furniture_color': style_settings_instance.furniture_color,
                'window_color': style_settings_instance.window_color,
                'sensor_label_color': style_settings_instance.sensor_label_color,
                'camera_label_color': style_settings_instance.camera_label_color,
                'navigation_arrow_color': style_settings_instance.navigation_arrow_color,
                'calibration_color': style_settings_instance.calibration_color,
                'wall_width': style_settings_instance.wall_width,
                'door_width': style_settings_instance.door_width,
                'furniture_width': style_settings_instance.furniture_width,
                'window_width': style_settings_instance.window_width,
                'labels': {label.id: label.location for label in labels}
            }

            style_settings_instance.orientation = orientation
            style_settings_instance.save()

            label_forms = [LabelForm(request.POST, prefix=str(label.id)) for label in labels]

            if form.is_valid() and all(label_form.is_valid() for label_form in label_forms):
                form.save()

                # Track all changes
                changes = []

                # Get orientation display names
                orientation_dict = dict(style_settings_instance.ORIENTATION_CHOICES)
                old_orientation_display = orientation_dict.get(old_values['orientation'], old_values['orientation'])
                new_orientation_display = orientation_dict.get(orientation, orientation)

                gen_info = Layout.objects.filter(file=layout, user=request.user).first()
                if gen_info:
                    # Save the original orientation value, not the display name
                    gen_info.orientation = orientation  # Use the value, not the display name
                    gen_info.save()

                # Check for orientation changes
                if old_values['orientation'] != orientation:
                    changes.append(f"Orientation changed from {old_orientation_display} to {new_orientation_display}")
                
                # Check for color changes
                color_fields = [
                    ('wall_color', 'Wall color'),
                    ('door_color', 'Door color'),
                    ('furniture_color', 'Furniture color'),
                    ('window_color', 'Window color'),
                    ('sensor_label_color', 'Sensor label color'),
                    ('camera_label_color', 'Camera label color'),
                    ('navigation_arrow_color', 'Navigation arrow color'),
                    ('calibration_color', 'Calibration color')
                ]
                
                for field, display_name in color_fields:
                    old_color = old_values[field]
                    new_color = form.cleaned_data.get(field)
                    if old_color != new_color:
                        old_color_display = get_color_display_name(old_color)
                        new_color_display = get_color_display_name(new_color)
                        changes.append(f"{display_name} changed from {old_color_display} to {new_color_display}")
                
                # Check for width changes
                width_fields = [
                    ('wall_width', 'Wall width'),
                    ('door_width', 'Door width'),
                    ('furniture_width', 'Furniture width'),
                    ('window_width', 'Window width')
                ]
                
                for field, display_name in width_fields:
                    if old_values[field] != form.cleaned_data.get(field):
                        changes.append(f"{display_name} changed from {old_values[field]} to {form.cleaned_data.get(field)}")
                
                # Track label location changes
                for label, label_form in zip(labels, label_forms):
                    new_location = label_form.cleaned_data['location']
                    if old_values['labels'][label.id] != new_location:
                        changes.append(f"Label '{label.name}' location changed from {old_values['labels'][label.id]} to {new_location}")
                    label.location = new_location
                    label.save()

                # If no changes were detected, add a generic message
                if not changes:
                    changes.append("No significant changes detected")

                # Create the change history with detailed changes
                LayoutHistory.objects.create(
                    layout=layout,
                    action='EDIT',
                    old_value='Previous Version',
                    new_value='\n'.join(changes),
                    user=request.user
                )

                result = elc.conversion(excel_file_path, style_settings_instance, labels)

                prefix_filename, _ = os.path.splitext(layout.file_name)
                username = request.user.username

                default_storage.delete(layout.latex_file)
                default_storage.delete(layout.pdf_file)
                default_storage.delete(layout.image)

                source_tex_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
                source_pdf_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
                source_png_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
                destination_tex_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.tex")
                destination_pdf_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.pdf")
                destination_png_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', username, f"{prefix_filename}.png")

                copyfile(source_tex_path, destination_tex_path)
                copyfile(source_pdf_path, destination_pdf_path)
                copyfile(source_png_path, destination_png_path)           

                layout.latex_file = destination_tex_path
                layout.image = destination_png_path
                layout.pdf_file = destination_pdf_path
                layout.save()

                return redirect('edit-layout', layout_id=layout_id)
            
            else:
                form_errors = form.errors.as_data()
                label_form_errors = [label_form.errors.as_data() for label_form in label_forms]
                print("Form errors:", form_errors)
                print("Label form errors:", label_form_errors)

    # GET request handling
    form = UpdateStyleSettingsForm(instance=style_settings_instance)
    orientation_initial = style_settings_instance.orientation
    orientation_form = forms.CharField(initial=orientation_initial, widget=forms.HiddenInput())
    label_forms = [LabelForm(prefix=str(label.id), initial={'location': label.location}) for label in labels]
    context = {
        'layout': layout,
        'form': form,
        'labels': labels,
        'label_data': zip(labels, label_forms),
        'orientation_form': orientation_form,
        'orientation_value': style_settings_instance.orientation,
    }

    return render(request, "edit-style.html", context)

# %******************** Layout Library Page ****************************%

from django.shortcuts import render
from .models import ConvertedFile, Folder
from django.http import JsonResponse
import json

# Allows a user to view all of their uploaded layouts
@login_required(login_url="auth-page")
def LayoutLibraryPage(request, folder_path=None):
    # Normalize folder_path
    if folder_path:
        folder_path = folder_path.strip('/')
    else:
        folder_path = ''
    
    # Get folders
    folders = Folder.objects.filter(user=request.user)
    
    # Current directory should match the database format
    current_directory = folder_path
    
    # Get current folder
    current_folder = folders.filter(full_path__icontains=folder_path).first() if folder_path else None
    
    filter_value = request.GET.get('filter')
    user_layouts = get_user_layouts(request, filter_value, current_directory)

    if request.method == 'POST':
        return handle_folder_creation(request)

    return render_layout_library(
        request=request,
        folders=folders,
        user_layouts=user_layouts,
        filter_value=filter_value,
        current_directory=current_directory,
        folder=current_folder
    )
def get_user_layouts(request, filter_value, current_directory):
    user_layouts = ConvertedFile.objects.filter(user=request.user, temporary=False)

    # Apply search
    search_query = request.GET.get('search')

    if current_directory:
        # Only include nested layouts under the current directory
        user_layouts = user_layouts.filter(folder__full_path=current_directory.strip('/'))
    elif not search_query:
        # Only exclude subfolders if NOT searching
        user_layouts = user_layouts.filter(folder__isnull=True)

    if search_query:
        user_layouts = user_layouts.filter(file_name__icontains=search_query)

    # Apply sorting
    if filter_value == 'alphabeticalAZ':
        return user_layouts.order_by('file_name')
    elif filter_value == 'alphabeticalZA':
        return user_layouts.order_by('-file_name')
    elif filter_value == 'oldest':
        return user_layouts.order_by('last_modified')

    return user_layouts.order_by('-last_modified')


# Renders the contents into the layout library
def render_layout_library(request, folders, user_layouts, filter_value, current_directory, folder=None):
    directory_path = [d for d in current_directory.split('/') if d]
    all_folders = folders.filter(user=request.user)
    breadcrumb_paths = []
    
    for i in range(len(directory_path)):
        trimmed_path = '/'.join(directory_path[:i+1])
        breadcrumb_paths.append((directory_path[i], trimmed_path))

    context = {
        'all_folders': folders.filter(user=request.user),
        'layouts': user_layouts,
        'current_folder': folder,
        'filter_value': filter_value,
        'current_directory': current_directory,
        'folders': folders.filter(parent_directory=current_directory),
        'directory_path': directory_path,
        'breadcrumb_paths': breadcrumb_paths,
    }
    return render(request, 'layout-library.html', context)

# Allows the user to create a new folder
def handle_folder_creation(request):
    try:
        data = json.loads(request.body)
        folder_name = data.get('folder_name')
        parent_directory = data.get('parent_directory', '').strip('/')
        if not folder_name:
            return JsonResponse({'success': False, 'error': 'Folder name is required'}, status=400)
        with transaction.atomic():
            # Build the physical folder path
            user_folder = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username)
            
            # Build folder path without leading/trailing slashes
            if parent_directory:
                folder_path = os.path.join(user_folder, parent_directory, folder_name)
                full_path = f"{parent_directory}/{folder_name}"
            else:
                folder_path = os.path.join(user_folder, folder_name)
                full_path = folder_name
                
            # Check if folder already exists in the EXACT location
            if Folder.objects.filter(user=request.user, full_path=full_path).exists():
                return JsonResponse({
                    'success': False, 
                    'error': f'A folder named "{folder_name}" already exists in this location'
                }, status=400)
                
            # NEW CHECK: Check if the folder name exists ANYWHERE in the user's library
            if Folder.objects.filter(user=request.user, folder_name=folder_name).exists():
                return JsonResponse({
                    'success': False, 
                    'error': f'A folder named "{folder_name}" already exists in your library. Please choose a different name.'
                }, status=400)
                
            # Create physical directory
            os.makedirs(folder_path, exist_ok=True)
            # Create folder record
            Folder.objects.create(
                folder_name=folder_name,
                user=request.user,
                path=folder_path,
                parent_directory=parent_directory,
                full_path=full_path,
                folders=None
            )
            return JsonResponse({
                'success': True,
                'folderName': folder_name,
                'fullPath': full_path
            })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error("Error occurred during folder creation: %s", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Allows a user to delete a layout from their library
@login_required(login_url="auth-page")
def delete_layout_test(request, layout_id):
    try:
        layout = ConvertedFile.objects.get(id=layout_id, user=request.user)  # Ensure the user can only delete their own layouts
        
        # Delete all associated files with the layout
        if layout.file_path:
            default_storage.delete(layout.file_path)
        if layout.latex_file:
            default_storage.delete(layout.latex_file)
        if layout.pdf_file:
            default_storage.delete(layout.pdf_file)
        if layout.image:
            default_storage.delete(layout.image)
        if layout.csv_file:
            default_storage.delete(layout.csv_file)
        if layout.json_file:
            default_storage.delete(layout.json_file)
        
        # Delete related objects (e.g., labels, measurements, history) if applicable
        Label.objects.filter(file=layout).delete()
        Measurement.objects.filter(layout=layout.layout).delete()
        LayoutHistory.objects.filter(layout=layout).delete()
        
        # Delete the layout instance
        layout.delete()
        print("Layout and all associated data deleted.")
    except ConvertedFile.DoesNotExist:
        messages.error(request, "Layout not found.")
    except Exception as e:
        messages.error(request, "Error deleting layout: %s" % e)
    return HttpResponseRedirect(reverse('layout-library'))

# Allows a user to delete all layouts from their library
@login_required(login_url="auth-page")
def delete_all_layout_test(request):
    try:
        layouts = ConvertedFile.objects.filter(user=request.user)  # Get all layouts for the current user
        for layout in layouts:
            # Delete associated files
            if layout.file_path:
                default_storage.delete(layout.file_path)
            if layout.latex_file:
                default_storage.delete(layout.latex_file)
            if layout.csv_file:
                default_storage.delete(layout.csv_file)
            if layout.json_file:
                default_storage.delete(layout.json_file)
            if layout.pdf_file:
                default_storage.delete(layout.pdf_file)
            if layout.image:
                default_storage.delete(layout.image)
            # Delete layout instance
            layout.delete()
        messages.success(request, "All layouts deleted successfully.")
    except Exception as e:
        messages.error(request, "Error deleting layouts: %s" % e)
    return HttpResponseRedirect(reverse('layout-library'))

from django.db.models import Q

# Allows a user to delete a created folder and all of its contents
@login_required(login_url="auth-page")
def delete_folder(request, folder_id):
    if request.method == 'POST':
        try:
            # Get the folder and verify it exists
            folder = Folder.objects.get(id=folder_id)
            folder_path = folder.full_path
            
            # Get all subfolders - including the folder itself
            subfolders = Folder.objects.filter(
                Q(full_path__startswith=f"{folder_path}/") |
                Q(id=folder_id)
            )
            
            # Get all layouts in these folders
            layouts = ConvertedFile.objects.filter(folder__in=subfolders)
            
            # Delete all layouts and their associated files
            for layout in layouts.distinct():
                default_storage.delete(layout.file_path)
                default_storage.delete(layout.latex_file)
                default_storage.delete(layout.pdf_file)
                default_storage.delete(layout.image)
                
                # Delete the layout record
                layout.delete()
            
            # Delete the folder structure recursively from the filesystem
            folder_filesystem_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username, folder_path)
            if os.path.exists(folder_filesystem_path):
                try:
                    # Use shutil.rmtree instead of os.rmdir to recursively delete directories
                    import shutil
                    shutil.rmtree(folder_filesystem_path)
                except OSError as e:
                    logger.error(f"Error deleting folder from filesystem: {str(e)}")
                    messages.error(request, f"Error deleting folder from filesystem: {str(e)}")
            
            # Delete all subfolder records from the database
            # Sort in reverse order of path length to delete deepest folders first
            sorted_subfolders = sorted(subfolders, key=lambda x: len(x.full_path), reverse=True)
            for subfolder in sorted_subfolders:
                try:
                    subfolder.delete()
                except Exception as e:
                    logger.error(f"Error deleting subfolder from database: {str(e)}")
            
            messages.success(request, f'Folder "{folder.folder_name}" and all its contents were successfully deleted.')
            
        except Folder.DoesNotExist:
            messages.error(request, 'Folder not found.')
        except PermissionError as e:
            messages.error(request, f'Permission denied when deleting files: {str(e)}')
        except OSError as e:
            messages.error(request, f'Error deleting files: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error deleting folder: {str(e)}')
    
    return redirect(reverse('layout-library'))

# Allows a user to rename a layout in their layout library
@login_required(login_url="auth-page")
def rename_layout(request, layout_id):
    if request.method == 'POST':
        new_file_name = request.POST.get('new_name').strip()
        try:
            layout = get_object_or_404(ConvertedFile, id=layout_id, user=request.user)
            old_file_name = layout.file_name
            current_folder = layout.folder

            # Validate the new filename
            if not new_file_name:
                messages.error(request, 'File name cannot be blank.')
                return redirect('layout-library')
            
            # Replace spaces with underscores
            new_file_name = new_file_name.replace(' ', '_')
            
            # Check for special characters other than underscore and hyphen
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', new_file_name):
                messages.error(request, 'File name can only contain letters, numbers, underscores, and hyphens.')
                return redirect('layout-library')
            
            # Extract filename prefix by removing any extensions
            if '.' in new_file_name:
                new_file_name = new_file_name.split('.')[0]
            
            # Check for duplicate names in the same folder context
            duplicate_exists = ConvertedFile.objects.filter(
                user=request.user,
                folder=current_folder,
                file_name=new_file_name
            ).exclude(id=layout_id).exists()

            if duplicate_exists:
                messages.error(request, 'File name must not match an existing file in your library.')
                return redirect('layout-library')

            # Update database records
            layout.file_name = new_file_name
            user_directory = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username)
            relative_image_path = f'imported_files/{request.user.username}/{new_file_name}.png'
            layout.image = relative_image_path
            
            # Update file paths
            layout.latex_file = os.path.join(user_directory, f"{new_file_name}.tex")
            layout.pdf_file = os.path.join(user_directory, f"{new_file_name}.pdf")
            layout.file_path = os.path.join(user_directory, f"{new_file_name}.xlsx")
            layout.csv_file = os.path.join(user_directory, f"{new_file_name}.csv")
            layout.json_file = os.path.join(user_directory, f"{new_file_name}.json")
            
            # Attempt to rename actual files first
            try:
                for file_extension in ['.pdf', '.tex', '.png', '.xlsx', '.json', '.csv']:
                    old_file_path = os.path.join(user_directory, f"{old_file_name}{file_extension}")
                    new_file_path = os.path.join(user_directory, f"{new_file_name}{file_extension}")
                    if os.path.exists(old_file_path):
                        # Check if destination file already exists
                        if os.path.exists(new_file_path):
                            messages.error(request, 'File name must not match an existing file in your library.')
                            return redirect('layout-library')
                        move(old_file_path, new_file_path)
            except OSError as e:
                messages.error(request, f'Error renaming files: {str(e)}')
                return redirect('layout-library')

            # If file operations succeeded, save the database changes
            layout.save()
            
            # Log the change
            LayoutHistory.objects.create(
                layout=layout,
                action='RENAME',
                old_value=old_file_name,
                new_value=new_file_name,
                user=request.user
            )
            
            messages.success(request, f'Layout successfully renamed to {new_file_name}')
            
        except ConvertedFile.DoesNotExist:
            messages.error(request, 'Layout not found')
        except Exception as e:
            messages.error(request, f'Error renaming layout: {str(e)}')
            
    return redirect('layout-library')

# Allows a user to rename a folder in their layout library
@login_required(login_url="auth-page")
def rename_folder(request, folder_id):
    if request.method == 'POST':
        new_name = request.POST.get('new_folder_name').strip()

        if not new_name:
            messages.error(request, 'Folder name cannot be empty')
            return redirect('layout-library')

        try:
            # Get the folder to rename
            folder = Folder.objects.get(id=folder_id, user=request.user)
            old_relative_path = folder.full_path  # Current relative path

            # Convert to absolute paths
            user_base_path = os.path.join(settings.MEDIA_ROOT, 'imported_files', request.user.username)
            old_abs_path = os.path.join(user_base_path, old_relative_path)

            # Construct new paths
            new_relative_path = os.path.join(os.path.dirname(old_relative_path), new_name)
            new_abs_path = os.path.join(user_base_path, new_relative_path)

            # Ensure the folder name is unique across all folders in the user's directory
            if Folder.objects.filter(user=request.user, folder_name=new_name).exists():
                messages.error(request, f'A folder named "{new_name}" already exists in your directory')
                return redirect('layout-library')

            # Check if the physical folder exists before renaming
            if os.path.exists(old_abs_path):
                try:
                    os.rename(old_abs_path, new_abs_path)  # Rename the actual folder on disk
                except OSError as e:
                    messages.error(request, f'Error renaming folder on disk: {str(e)}')
                    return redirect('layout-library')
            else:
                messages.error(request, f'Folder "{old_abs_path}" does not exist on disk')
                return redirect('layout-library')

            # Update folder record with new name and path
            folder.folder_name = new_name
            folder.full_path = new_relative_path

            # Update all subfolders to reflect the new parent path
            subfolders = Folder.objects.filter(user=request.user, full_path__startswith=old_relative_path)
            for subfolder in subfolders:
                updated_path = subfolder.full_path.replace(old_relative_path, new_relative_path, 1)
                subfolder.full_path = updated_path
                subfolder.path = os.path.join(user_base_path, updated_path)
                subfolder.folder_name = os.path.basename(updated_path)
                subfolder.parent_directory = os.path.dirname(updated_path)
                subfolder.save()

            # Update all related file paths in the `ConvertedFile` model
            layouts = ConvertedFile.objects.filter(folder__full_path__startswith=old_relative_path)
            for layout in layouts:
                if layout.file_path != "NONE":
                    layout.file_path = layout.file_path.replace(old_relative_path, new_relative_path)
                if layout.latex_file:
                    layout.latex_file = layout.latex_file.replace(old_relative_path, new_relative_path)
                if layout.pdf_file:
                    layout.pdf_file = layout.pdf_file.replace(old_relative_path, new_relative_path)
                if layout.image:
                    layout.image = layout.image.replace(old_relative_path, new_relative_path)
                layout.save()

            # Save the main folder update
            folder.save()
            messages.success(request, f'Folder successfully renamed to "{new_name}"')

        except Folder.DoesNotExist:
            messages.error(request, 'Folder not found')
        except PermissionError as e:
            messages.error(request, f'Permission denied when renaming folder: {str(e)}')
        except OSError as e:
            messages.error(request, f'Error renaming folder: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error processing folder rename: {str(e)}')

    return redirect('layout-library')

# Allows a user to move a layout in their layout library
@login_required(login_url="auth-page")
def move_layout(request, layout_id):
    if request.method == 'POST':
        new_folder = request.POST.get('newDirectory')
        try:
            # Get the layout and confirm the user owns it
            layout = ConvertedFile.objects.get(id=layout_id, user=request.user)
            store_folder = layout.folder.full_path if layout.folder else 'root'
            layout.folder = Folder.objects.get(full_path=new_folder, user=request.user) if new_folder else None
            
            # Retrieve the current folder path and the new folder instance
            if not layout.folder:
                old_folder = ''
            else:
                old_folder = layout.folder.full_path

            # Move files to the new directory if they exist and if the paths are different
            if os.path.exists(old_folder) and old_folder != new_folder:
                os.rename(old_folder, new_folder)
                layout.file_path = new_folder
            
            # Log the change in history
            LayoutHistory.objects.create(
                layout=layout,
                action='MOVE',
                old_value=store_folder,
                new_value=new_folder if new_folder else 'root',
                user=request.user
            )

            # Save the layout with updated paths
            layout.save()
            
            messages.success(request, f'Layout moved to {new_folder if new_folder else "root"}')
            
        except ConvertedFile.DoesNotExist:
            messages.error(request, 'Layout not found')
        except Folder.DoesNotExist:
            messages.error(request, 'Destination folder not found')
        except OSError as e:
            messages.error(request, f'Error moving files: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error moving layout: {str(e)}')
    
    if new_folder:
        return redirect('layout-library-folder', folder_path=new_folder)
    return redirect('layout-library')

from .models import LayoutHistory

# Allows a user to view a layout's version history
@login_required(login_url="auth-page")
def layout_history(request, layout_id):
    try:
        layout = get_object_or_404(ConvertedFile, id=layout_id, user=request.user)
        history = LayoutHistory.objects.filter(layout=layout)
        
        history_data = [{
            'action': entry.action,
            'old_value': entry.old_value,
            'new_value': entry.new_value,
            'timestamp': entry.timestamp.strftime("%b %d, %Y %H:%M"),
            'username': entry.user.username
        } for entry in history]
        
        return JsonResponse({
            'success': True,
            'layout_name': layout.file_name,
            'history': history_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# %******************** Settings Page ****************************%

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from .forms import AccountSettingsForm, UpdateDefaultStyleSettingsForm

# Allows the user to change their default style settings
@login_required(login_url="auth-page")
def DefaultStyleSettingsPage(request):
    """View for updating user default style settings."""
    # Make sure to get the latest data from the database
    style_settings_instance = DefaultStyleSettings.objects.get(user=request.user)

    if request.method == 'POST':
        form = UpdateDefaultStyleSettingsForm(request.POST, instance=style_settings_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Style settings have been updated.")
            return redirect('settings')
    else:
        form = UpdateDefaultStyleSettingsForm(instance=style_settings_instance)

    return render(request, "default-style-settings.html", {'form': form})

# Allows user to reset their default style settings to the system default
@login_required(login_url="auth-page")
def reset_default_settings(request):
    """ Reset user default style settings to system defaults """
    DefaultStyleSettings.objects.filter(user=request.user).update(
        sensor_label_color="teal",
        camera_label_color="blue!75!black",
        navigation_arrow_color="green!60!black",
        calibration_color="violet",
        wall_color="black",
        wall_width=2,
        door_color="black",
        door_width=1,
        window_color="black",
        window_width=1,
        furniture_color="black",
        furniture_width=0.5,
    )

    messages.success(request, "Default style settings have been restored.")
    return redirect('settings')  # ✅ Redirect after reset

from django.contrib.auth import update_session_auth_hash
from .forms import AccountSettingsForm

# Allows the user to update their email or password
@login_required(login_url="auth-page")
def AccountSettingsPage(request):
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            if old_password and new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            messages.success(request, 'Account settings updated successfully.')
    else:
        form = AccountSettingsForm(instance=user)
    return render(request, 'account-settings.html', {'form': form})

import re

# %******************** Authentication Page ****************************%

def AuthPage(request):
    if request.method == 'POST':
        if 'signup' in request.POST:
            # Handle registration
            uname = request.POST.get('username')
            email = request.POST.get('email').lower()
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

            # Check if any field is empty
            if not uname or not email or not pass1 or not pass2:
                return JsonResponse({'success': False, 'message': 'All fields are required.'})
            elif User.objects.filter(username=uname).exists():
                return JsonResponse({'success': False, 'message': 'Username is already in use.'})
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email is already in use.'})
            elif not re.fullmatch(regex, email):
                return JsonResponse({'success': False, 'message': 'Invalid email format.'})
            elif len(pass1) < 8:
                return JsonResponse({'success': False, 'message': "Password must contain at least 8 characters."})
            elif pass1.isdigit():
                return JsonResponse({'success': False, 'message': "Password cannot be entirely numeric."})
            elif pass1 != pass2:
                return JsonResponse({'success': False, 'message': "Passwords do not match!"})
            else:
                # Create a new user
                my_user = User.objects.create_user(username=uname, email=email, password=pass1)
                my_user.save()
                # create new default style settings
                default_style_settings = DefaultStyleSettings(user=my_user)
                default_style_settings.save()
                return JsonResponse({'success': True, 'message': 'Registration successful! You can now log in.'})

        elif 'signin' in request.POST:
            # Handle login
            username = request.POST.get("username")
            password = request.POST.get('pass')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('import')  # Change 'import' to your actual import view name
            else:
                messages.warning(request, "Username or password is incorrect!")

    return render(request, "auth_page.html")  # Use the same template for both actions

# %******************** Logout Page ****************************%

def LogoutPage(request):
    logout(request)

    return render(request, 'logout.html')

# %******************** Measurement Pages ****************************%

# Allows user to add in measurement values to an expandable table 
# Starts off blank, as user creates layout from scratch
@login_required(login_url="auth-page")
def MeasurePage(request):
    if request.method == 'POST':
        pass
    return render(request, 'measure.html')

# Allows the user to modify an existing layout
@login_required(login_url="auth-page")
def EditMeasurePage(request, layout_id):
    # Retrieve Converted File based on layout id
    converted_file = ConvertedFile.objects.get(id=layout_id)
    print("ID:", layout_id)

    # Retrieve the Layout with the corresponding ConvertedFile
    try:
        gen_info = Layout.objects.get(file=layout_id)
    except Layout.DoesNotExist:
        messages.error(request, "Only layouts created within the application can be modified in the measurement page.")
        # Redirect to edit-layout if gen_info is null
        return redirect('edit-layout', layout_id)

    # Retrieve the Layout's measurements
    measurements = Measurement.objects.filter(layout=gen_info)

    context = {
        'layout': converted_file,
        'gen_info': gen_info,
        'measurements': measurements
    }

    return render(request, 'edit-measure.html', context)

# Process Layout | Refresh
def process_layout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
        
    try:

        fulldata = json.loads(request.body)
        data = fulldata.get('layoutData')
        layout_id = fulldata.get('layoutId')
        username = request.user.username
        user_dir = os.path.join(settings.MEDIA_ROOT, 'imported_files', username)
        os.makedirs(user_dir, exist_ok=True)
        # Handles empty data 
        if not data:
            return JsonResponse({'success': True, 'message': 'No data to process'}, status=200)
            
        # Get or update existing style settings
        default_styling = DefaultStyleSettings.objects.get(user=request.user)


        # Use a fixed temp filename 
        base_filename = f'refresh_image'
        excel_filename = f'{base_filename}.xlsx'
        
        user_dir = os.path.join(settings.MEDIA_ROOT, 'imported_files', username)
        os.makedirs(user_dir, exist_ok=True)
        excel_file_path = os.path.join(user_dir, excel_filename)

        # Save data to Excel
        df = pd.DataFrame(data)
        df.to_excel(excel_file_path, engine='openpyxl', index=False)

        # Get or update the single style settings instance
        default_styling = DefaultStyleSettings.objects.filter(user=request.user).first()

        # Check for existing layout based on unique identifiers
        existing_layout = Layout.objects.filter(file=layout_id).first()  
              
        # Store layout history if layout exists
        existing_styles = None
        if existing_layout:
            # Get associated ConvertedFile for the layout
            existing_converted_file = ConvertedFile.objects.filter(layout=existing_layout).first()

            # Store existing layout styles
            existing_styles = existing_converted_file.style_settings

        # Create or update StyleSettings
        layout_style, _ = StyleSettings.objects.update_or_create(
            user=request.user,
            name=base_filename,
            defaults={
                'wall_color': existing_styles.wall_color if existing_styles else default_styling.wall_color,
                'door_color': existing_styles.door_color if existing_styles else default_styling.door_color,
                'furniture_color': existing_styles.furniture_color if existing_styles else default_styling.furniture_color,
                'window_color': existing_styles.window_color if existing_styles else default_styling.window_color,
                'navigation_arrow_color': existing_styles.navigation_arrow_color if existing_styles else default_styling.navigation_arrow_color,
                'sensor_label_color': existing_styles.sensor_label_color if existing_styles else default_styling.sensor_label_color,
                'camera_label_color': existing_styles.camera_label_color if existing_styles else default_styling.camera_label_color,
                'calibration_color': existing_styles.calibration_color if existing_styles else default_styling.calibration_color,
                'wall_width': existing_styles.wall_width if existing_styles else default_styling.wall_width,
                'door_width': existing_styles.door_width if existing_styles else default_styling.door_width,
                'furniture_width': existing_styles.furniture_width if existing_styles else default_styling.furniture_width,
                'window_width': existing_styles.window_width if existing_styles else default_styling.window_width,
                'orientation': existing_styles.orientation if existing_styles else "portrait"
            }
        )

        # Process conversion
        result = lc.conversion(excel_file_path, layout_style)
        
        if result['success']:
            uploaded_file_instance = UploadedFile.objects.create(
            file_name=excel_filename,
            file_path=excel_file_path,
            user=request.user
)
            # Update or create the single converted file instance
            converted_file, _ = ConvertedFile.objects.get_or_create(
                user=request.user,
                uploaded_file=uploaded_file_instance,
                defaults={
                    'file_name': base_filename,
                    'file_path': excel_file_path,
                    'latex_file': os.path.join(user_dir, f'{base_filename}.tex'),
                    'pdf_file': os.path.join(user_dir, f'{base_filename}.pdf'),
                    'image': os.path.join(user_dir, f'{base_filename}.png'),
                    'style_settings': layout_style,
                    'temporary': True,
                }
            )
           
            return JsonResponse({
                'success': True,
                'message': 'Layout generated successfully',
                'layout_id': converted_file.id
            })  
            
        return JsonResponse({
            'success': False, 
            'error': result['message']
        }, status=200)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

from django.utils import timezone
from django.db import models
import os
from pathlib import Path

def process_layout_2(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
        
    try:
        fulldata = json.loads(request.body)
        data = fulldata.get('layoutData')
        layout_id = fulldata.get('layoutId')
        layout_name = fulldata.get('layoutName')
        username = request.user.username

        canvas = fulldata.get('canvas', False)

        # Ensure atomicity
        with transaction.atomic():
            # Get default styling
            default_styling = DefaultStyleSettings.objects.get(user=request.user)
            
            # Check for existing layout based on unique identifiers
            existing_layout = Layout.objects.filter(file=layout_id).first()
            
            # Initialize variables
            existing_converted_file = None
            existing_styles = None
            original_filename = layout_name
            original_folder = None
            base_filename = None
            
            # Store layout history if layout exists
            layout_history_records = []
            if existing_layout:
                try:
                    # Get associated ConvertedFile for the layout
                    existing_converted_file = ConvertedFile.objects.filter(layout=existing_layout).first()
                    
                    if existing_converted_file:
                        # Save the original folder to reuse it
                        original_folder_path = existing_converted_file.folder.full_path if existing_converted_file.folder else None
                        if original_folder_path:
                            original_folder = Folder.objects.get(full_path=original_folder_path, user=request.user)
                        # Strip any extension for base filename
                        base_filename = os.path.splitext(original_filename)[0]
                        
                        # Store existing layout styles
                        existing_styles = existing_converted_file.style_settings
                        
                        # Retrieve and save all layout history records
                        layout_history_records = list(LayoutHistory.objects.filter(layout=existing_converted_file))

                        # Improved file deletion logic
                        try:
                            # Get the base filename without extension
                            old_prefix_filename = existing_converted_file.file_name
                            old_user_dir = os.path.dirname(existing_converted_file.file_path)
                            
                            # List all possible file extensions that need to be cleaned up
                            extensions = ['.xlsx', '.csv', '.json', '.tex', '.pdf', '.png']
                            
                            # Build a complete list of all files to check and delete
                            files_to_check = []
                            for ext in extensions:
                                file_path = os.path.join(old_user_dir, f"{old_prefix_filename}{ext}")
                                files_to_check.append(file_path)
                            
                            # Also add any directly referenced files from the database object
                            direct_references = [
                                existing_converted_file.file_path,
                                existing_converted_file.latex_file,
                                existing_converted_file.pdf_file,
                                existing_converted_file.image,
                                existing_converted_file.csv_file,
                                existing_converted_file.json_file
                            ]
                            
                            # Add any non-duplicate paths to the list
                            for path in direct_references:
                                if path and path not in files_to_check:
                                    files_to_check.append(path)
                                    
                            # Convert MEDIA_ROOT to a Path object for comparison
                            media_root_path = Path(settings.MEDIA_ROOT).resolve()
                            
                            for file_path in files_to_check:
                                if not file_path:
                                    continue
                                    
                                try:
                                    # Resolve path, but catch any symlink or permission issues
                                    file_abs_path = Path(file_path).resolve(strict=True)
                                    
                                    # Verify file is within MEDIA_ROOT before deletion
                                    if media_root_path in file_abs_path.parents or media_root_path == file_abs_path:
                                        try:
                                            if os.path.exists(file_path):
                                                os.remove(file_path)
                                                logger.info(f"Deleted file {file_path}")
                                            else:
                                                logger.info(f"File not found: {file_path}")
                                        except (OSError, PermissionError) as e:
                                            logger.warning(f"Could not delete file {file_path}: {str(e)}")
                                    else:
                                        logger.warning(f"Attempted to delete file outside MEDIA_ROOT: {file_path}")
                                except (RuntimeError, ValueError, OSError) as e:
                                    logger.warning(f"Error validating path {file_path}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error during file deletion: {str(e)}")
                    
                    # Delete database records - use transaction to ensure consistency
                    with transaction.atomic():
                        Measurement.objects.filter(layout=existing_layout).delete()
                        ConvertedFile.objects.filter(layout=existing_layout).delete()
                        existing_layout.delete()
                        
                    logger.info(f"Successfully deleted layout {existing_layout.id} and associated files")
                    
                except Exception as e:
                    logger.error(f"Error during layout deletion: {str(e)}")
                    # Re-raise or handle based on your application's needs
                    raise
            
            # For new layouts, handle unnamed_layout naming
            if not base_filename:
                base_name = layout_name
                counter = 0
                while True:
                    if counter == 0:
                        base_filename = base_name
                    else:
                        base_filename = f"{base_name}({counter})"
                    
                    # Check if file exists with this name
                    if not ConvertedFile.objects.filter(
                        user=request.user,
                        file_name=base_filename
                    ).exists():
                        break
                    counter += 1
            
            converted_filename = f'{base_filename}.xlsx'
            
            # Create user directory if not exists
            user_dir = os.path.join(settings.MEDIA_ROOT, 'imported_files', username)
            os.makedirs(user_dir, exist_ok=True)
            
            # Full path for files
            excel_file_path = os.path.join(user_dir, converted_filename)
            csv_path = os.path.join(user_dir, f"{base_filename}.csv")
            json_path = os.path.join(user_dir, f"{base_filename}.json")
            
            # Save data to Excel, CSV, and JSON
            df = pd.DataFrame(data)
            df.to_excel(excel_file_path, engine='openpyxl', index=False)
            df.to_csv(csv_path, index=False)
            df.to_json(json_path, orient='records')

            # Convert date to YYYY-MM-DD format
            date_str = df.iloc[4, 1]
            date_obj = pd.to_datetime(date_str, errors='coerce').date()

            # Create or update StyleSettings
            layout_style, _ = StyleSettings.objects.update_or_create(
                user=request.user,
                name=converted_filename,
                defaults={
                    'wall_color': existing_styles.wall_color if existing_styles else default_styling.wall_color,
                    'door_color': existing_styles.door_color if existing_styles else default_styling.door_color,
                    'furniture_color': existing_styles.furniture_color if existing_styles else default_styling.furniture_color,
                    'window_color': existing_styles.window_color if existing_styles else default_styling.window_color,
                    'navigation_arrow_color': existing_styles.navigation_arrow_color if existing_styles else default_styling.navigation_arrow_color,
                    'sensor_label_color': existing_styles.sensor_label_color if existing_styles else default_styling.sensor_label_color,
                    'camera_label_color': existing_styles.camera_label_color if existing_styles else default_styling.camera_label_color,
                    'calibration_color': existing_styles.calibration_color if existing_styles else default_styling.calibration_color,
                    'wall_width': existing_styles.wall_width if existing_styles else default_styling.wall_width,
                    'door_width': existing_styles.door_width if existing_styles else default_styling.door_width,
                    'furniture_width': existing_styles.furniture_width if existing_styles else default_styling.furniture_width,
                    'window_width': existing_styles.window_width if existing_styles else default_styling.window_width,
                    'orientation': existing_styles.orientation if existing_styles else "portrait"
                }
            )
            
            # Run conversion
            print(excel_file_path, layout_style)
            result = lc.conversion(excel_file_path, layout_style, canvas)
            
            if not result['success']:
                messages.error(request, result['message'])
                return redirect("import")
            
            uploaded_file_instance = UploadedFile.objects.create(
                user=request.user,
                file_name=converted_filename,
                file_path=excel_file_path
            )
            
            # Prepare file paths for output files
            prefix_filename, _ = os.path.splitext(converted_filename)
            source_tex_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.tex')
            source_pdf_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.pdf')
            source_png_path = os.path.join(settings.MEDIA_ROOT, 'conversion_output', 'output.png')
            destination_tex_path = os.path.join(user_dir, f"{prefix_filename}.tex")
            destination_pdf_path = os.path.join(user_dir, f"{prefix_filename}.pdf")
            destination_png_path = os.path.join(user_dir, f"{prefix_filename}.png")
            
            # Copy output files
            copyfile(source_tex_path, destination_tex_path)
            copyfile(source_pdf_path, destination_pdf_path)
            copyfile(source_png_path, destination_png_path)
            
            # Create ConvertedFile
            converted_file = ConvertedFile.objects.create(
                file_name=prefix_filename,
                user=request.user,
                file_path=excel_file_path,
                folder=original_folder,
                uploaded_file=uploaded_file_instance,
                latex_file=destination_tex_path,
                pdf_file=destination_pdf_path,
                style_settings=layout_style,
                image=destination_png_path,
                csv_file=csv_path,    
                json_file=json_path
            )
            converted_file.full_clean()
            converted_file.save()

            # Create Layout instance
            layout = Layout.objects.create(
                user=request.user,
                file=converted_file,
                neighborhood=df.iloc[1, 1],
                building=df.iloc[2, 1],
                room_name=df.iloc[3, 1],
                date=pd.to_datetime(df.iloc[4, 1]).date(),
                step=df.iloc[5, 13],  # X Axis row at 13th column
                orientation=df.iloc[0, 1]
            )

            print("STEP:", layout.step)

            # Update ConvertedFile with the created layout
            converted_file.layout = layout
            converted_file.save()
            
            # Transfer layout history records with preserved timestamps
            if layout_history_records:
                # Temporarily disable auto_now_add for timestamp field
                original_auto_now_add = LayoutHistory._meta.get_field('timestamp').auto_now_add
                LayoutHistory._meta.get_field('timestamp').auto_now_add = False
                
                try:
                    # Create new history records with original timestamps
                    new_history_records = []
                    for record in layout_history_records:
                        new_history = LayoutHistory(
                            layout=converted_file,
                            action=record.action,
                            old_value=record.old_value,
                            new_value=record.new_value,
                            user=record.user,
                            timestamp=record.timestamp  # Preserve original timestamp
                        )
                        new_history_records.append(new_history)
                    
                    # Bulk create the records
                    LayoutHistory.objects.bulk_create(new_history_records)
                    
                finally:
                    # Restore auto_now_add setting
                    LayoutHistory._meta.get_field('timestamp').auto_now_add = original_auto_now_add
            
            # Add a new history record for this update if existing_layout existed
            if existing_layout:
                LayoutHistory.objects.create(
                    layout=converted_file,
                    action='CONVERT',
                    old_value='Reconverted from existing layout',
                    new_value=f'Created new version on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    user=request.user
                )

            for index, row in df.iloc[7:].iterrows():  # Skip first 7 rows to start from the measurements
                measurement = Measurement.objects.create(
                    layout=layout,
                    type=row['Type'],
                    descriptor=row['Descriptor'],
                    x=row['X'],
                    y=row['Y'],
                    width=row['width'],
                    length=row['length'],
                    radius=row['radius'],
                    scale=row['scale'],
                    rotation=row['rotation'],
                    furniture_type=row['furniture_type'],
                    room_navigation_direction=row['room_navigation_direction']
                )
                print("\n", row['Type'], row['Descriptor'], row['X'], row['Y'], row['width'], row['length'], row['radius'], row['scale'], row['rotation'], row['furniture_type'], row['room_navigation_direction'])

            # Create Labels
            labels = parse_excel_file(converted_file)
            for label in labels:
                Label.objects.create(
                    file=converted_file, 
                    name=label['name'], 
                    type=label['type']
                )
            
            # Redirect to export-layout
            return JsonResponse({
                'success': True,
                'layout_id': converted_file.id,
                'redirect_url': reverse('export-layout', kwargs={'layout_id': converted_file.id})
            })
    
    except Exception as e:
        logger.error(f"Error in process_layout_2: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

from .models import Layout, Measurement

# Layout's General Information
@login_required
def layout_form(request):
    if request.method == 'POST':
        # Check if there's a redirect URL from the hidden input
        redirect_url = request.POST.get('redirect_url')

        # Prioritize the redirect URL from the hidden input
        if redirect_url:
            return redirect(redirect_url)
        
        # Fallback redirect if no specific URL is provided
        return redirect('measure')
    
    return render(request, 'measure.html')

# %******************** Canvas Page ****************************%

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .models import CanvasLayout

# Allows user to add lines and objects onto canvas page
@login_required(login_url="auth-page")
def CanvasPage(request):
    if request.method == 'POST':
        pass
    # Precompute grid coordinates for 100 cells
    cell_coords = [{'x': i // 10, 'y': i % 10} for i in range(100)]
    context = {
        'cell_coords': cell_coords
    }
    return render(request, 'canvas-page.html', context)

@require_POST
@login_required(login_url="auth-page")
def save_canvas(request):
    try:
        # Check content type and read JSON safely
        if request.content_type == "application/json":
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid content type. Expected application/json.'}, status=400)

        if not data:
            return JsonResponse({'success': False, 'error': 'Empty data received'}, status=400)

        # Get or create canvas layout for the user
        canvas_layout, created = CanvasLayout.objects.get_or_create(
            user=request.user,
            defaults={'data': data}
        )
        
        # Update if it already exists
        if not created:
            canvas_layout.data = data
            canvas_layout.save()
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
@login_required(login_url="auth-page")
def load_canvas(request):
    try:
        # Get the latest canvas layout for the user
        canvas_layout = CanvasLayout.objects.filter(user=request.user).first()
        
        if canvas_layout:
            return JsonResponse({
                'success': True, 
                'canvasData': json.dumps(canvas_layout.data)
            })
        else:
            return JsonResponse({'success': True, 'canvasData': None})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# %******************** Export Layout ****************************%
def convert_excel_to_formats(excel_path):
    # Read Excel file
    df = pd.read_excel(excel_path)
    
    # Get file prefix for new files
    prefix, _ = os.path.splitext(excel_path)
    
    # Convert to CSV
    csv_path = f"{prefix}.csv"
    df.to_csv(csv_path, index=False)
    
    # Convert to JSON
    json_path = f"{prefix}.json"
    df.to_json(json_path, orient='records')
    
    return csv_path, json_path

# Download csv and json files on demand rather than generating them with each convert request
def download_csv(request, layout_id):
    converted_file = get_object_or_404(ConvertedFile, id=layout_id)
    
    # Read the Excel file
    df = pd.read_excel(converted_file.file_path)
    
    # Create response object with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{converted_file.file_name}.csv"'
    
    # Convert to CSV
    df.to_csv(path_or_buf=response, index=False)
    return response

def download_json(request, layout_id):
    converted_file = get_object_or_404(ConvertedFile, id=layout_id)
    
    # Read the Excel file
    df = pd.read_excel(converted_file.file_path)
    
    # Create response object with JSON content
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{converted_file.file_name}.json"'
    
    # Convert to JSON
    df.to_json(path_or_buf=response, orient='records')
    return response