from django.urls import path,include
from django.contrib.auth import views as auth_views

from . import views,views_webhook

app_name = 'ocado'
urlpatterns = [
    # ex: /dashboard/
    path('', views.dashboard, name='dashboard'),
    path('export_csv.csv', views.exportcsv, name='exportcsv'),
    path('remove_api_call', views.remove_api_call, name='remove_api_call'),
    path('<int:api_call_id>/bug_report/', views.bug_report, name='bug_report'),
    path('ocado_logout', views.ocado_logout, name='ocado_logout'),
    path('client_api', views.client_api, name='client_api'),
    path('<int:api_call_id>/client_api/', views.client_api_id, name='client_api_id'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('webhook/', views_webhook.webhook, name='webhook'),
    
]


