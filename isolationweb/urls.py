"""isolationweb URL Configuration

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
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from webmanager.views import users
from django.conf.urls.static import static 
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    # all things auth
    path('signup', users.signup, name='signup'),
    path('accounts/login', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout', auth_views.LogoutView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('webmanager.urls')),

    path('faq/', TemplateView.as_view(template_name="faq.html"), name='faq'),
    path('terms/', TemplateView.as_view(template_name="terms.html"), name='terms'),
    path('privacy/', TemplateView.as_view(template_name="privacy.html"), name='privacy'),
    path('web/', TemplateView.as_view(template_name="web.html"), name='web'),
    path('d3web/', TemplateView.as_view(template_name="d3-web.html"), name="d3web")
] +  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
