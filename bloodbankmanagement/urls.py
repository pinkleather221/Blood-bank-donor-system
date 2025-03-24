"""bloodbankmanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LogoutView,LoginView
from donor import views as donor_views
from blood import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name=''),#blood bank overvie
    # chatbot mod 1
    path('chat/', views.chat_endpoint, name='chat_endpoint'),
    path('', views.chat_page, name=''),  # or whatever URL you prefer


    path('donor/',include('donor.urls')),
    path('', donor_views.donor_view, name='donor_views'),

    path('patient/',include('patient.urls')),

     #added this
   


    path('admin-emails/', views.admin_emails, name='admin_emails'),
    path('compose-email/', views.compose_email, name='compose_email'),
    path('send-email/', views.send_email, name='send_email'),
    path('load-template/', views.load_template, name='load_template'),

    # path('',views.home_view,name=''),we removed this sline because we think it is notr serving any purpose
     #mod 3


    
    path('logout', LogoutView.as_view(template_name='blood/logout.html'),name='logout'),

    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('adminlogin', LoginView.as_view(template_name='blood/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('admin-blood', views.admin_blood_view,name='admin-blood'),
    path('admin-donor', views.admin_donor_view,name='admin-donor'),
    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('update-donor/<int:pk>', views.update_donor_view,name='update-donor'),
    path('delete-donor/<int:pk>', views.delete_donor_view,name='delete-donor'),
    path('admin-request', views.admin_request_view,name='admin-request'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('delete-patient/<int:pk>', views.delete_patient_view,name='delete-patient'),
    path('admin-donation', views.admin_donation_view,name='admin-donation'),
    path('approve-donation/<int:pk>', views.approve_donation_view,name='approve-donation'),
    path('reject-donation/<int:pk>', views.reject_donation_view,name='reject-donation'),
    path('admin-request-history', views.admin_request_history_view,name='admin-request-history'),
    path('update-approve-status/<int:pk>', views.update_approve_status_view,name='update-approve-status'),
    path('update-reject-status/<int:pk>', views.update_reject_status_view,name='update-reject-status'),
   
]
