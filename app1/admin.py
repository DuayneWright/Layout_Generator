from django.contrib import admin

from .models import UploadedFile, ConvertedFile, DefaultStyleSettings, StyleSettings, Layout, Measurement

# register UploadedFile with admin view
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    pass

# register ConvertedFile with admin view
@admin.register(ConvertedFile)
class ConvertedFileAdmin(admin.ModelAdmin):
    pass

# register DefaultStyleSettings with admin view
@admin.register(DefaultStyleSettings)
class DefaultSSAdmin(admin.ModelAdmin):
    pass

# register StyleSettings with admin view
@admin.register(StyleSettings)
class SSAdmin(admin.ModelAdmin):
    pass

# register Layout with admin view
@admin.register(Layout)
class LayoutAdmin(admin.ModelAdmin):
    pass

# register Measurement with admin view
@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    pass