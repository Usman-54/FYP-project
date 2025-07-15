from django.contrib import admin
from django.urls import path, reverse_lazy
from .import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('donation/', views.index, name='index'),
    # path('about/', views.about, name='about'),
    path('signup/', views.signup_donor, name='signup'),
    path('login/', views.login_views, name='login'),
    path('donor/',views.donor_login, name='donorlogin'),
    path('donor_dashboard/',views.donor_dashboard, name='donor_dashboard'),
    # Admin part urls ****************************************************************
    path('admin-signup/', views.admin_signup_view, name='admin_signup'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('submit-comment/', views.submit_comment, name='submit_comment'),
    path('donation_history/' ,views.donation_history, name= 'donation_history'),
    path('view_detail/<int:donation_id>/', views.view_detail, name='view_detail'),
    path('accepted_donation/', views.accepted_donation, name='accepted_donation'),
    path('donation_area/', views.donation_area, name='donation_area'),
    path('manage_area/', views.manage_area, name='manage_area'),

    path('payment_callback/', views.payment_callback, name='payment_callback'), #payment urls
    # path('delete-area/<int:area_id>/', views.delete_area, name='delete_area'),
    path('manage_donor/', views.manage_donor, name='manage_donor'),
    path('donor_detail/<int:donor_id>/', views.donor_detail, name='donor_detail'),
    # volunnteer pages urls##############################################################
    path('volunter_signup/', views.volunter_signup, name='volunter_signup'),
    path('volunteer/', views.volunteer_login, name='volunteer_login'),
    path('volunter_dashboard/', views.volunter_dashboard, name='volunter_dashboard'),
    path('new_volunter/', views.new_volunter, name='new_volunter'),
    path('volunter_detail/<int:volunteer_id>/', views.volunter_detail, name='volunter_detail'),
    path('approved_volunter/', views.approved_volunter, name='approved_volunter'),
    path('new_donation_request/', views.new_donation_request, name='new_donation_request'),
    path('volunter_donation_history/', views.vol_donation_histry, name='vol_donation_histry'),
    
    # common function ulrs *****************************************************************
    
     path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('volunteer_profile/', views.volunteer_profile, name='volunteer_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_beneficiaries/', views.add_beneficiaries, name='add_beneficiaries'),

    path('beneficiaries/', views.beneficiaries, name='beneficiaries'),
    path('delete/<str:model_name>/<int:item_id>/', views.delete_item, name='delete_item'),
    path('edit_item/<str:model_name>/<int:item_id>/', views.edit_item, name='edit_item'),
    # path('edit-area/<int:area_id>/', views.edit_area, name='edit_area'),
  
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',  # ✅ include folder
        email_template_name='registration/password_reset_email.html',  # ✅
        subject_template_name='registration/password_reset_subject.txt',  # ✅
        success_url=reverse_lazy('password_reset_done'),
        extra_email_context={
            'domain': '127.0.0.1:8000',
            'protocol': 'http'
        }
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset.html'  # ✅
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'  # ✅
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_confirm.html'  # ✅
    ), name='password_reset_complete'),
    path('logout/', views.Logout_view, name='logout'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)