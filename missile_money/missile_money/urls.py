"""
URL configuration for missile_money project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView
from main import views
from django.conf import settings
from django.conf.urls.static import static


"""
If you add a feature to this website you need to add a url pattern here
an entry in the 'urlpatterns' list should contain:
    the endpoint to reach out to which is the name of the html for the page in the templates directory
    The second argument should be the name of the function as wrote in the views.py file that will return the redirect to the page
    The final argument should be the name of the url call for internal tracking only and refrencing the call to this url
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('transaction/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transaction/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('reports/', views.view_reports, name='view_reports'),
    path('send_payment/', views.send_payment, name='send_payment'),
    path('getting-started/', views.start_guide, name='start_guide'),
    path('savings-goal/', views.savings_goal, name='savings_goal'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)