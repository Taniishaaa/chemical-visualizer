from django.urls import path
from . import views

urlpatterns = [
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('history/', views.last_uploads, name='last_uploads'),
    path('report/<int:record_id>/', views.generate_report, name='generate_report'),
]
