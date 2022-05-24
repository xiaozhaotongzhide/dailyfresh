"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    # path('user/',include('user.urls','user')),
    # path('cart/',include('cart.urls','cart')),
    # path('order/',include('order.urls','order')),
    # 放到最后,最后匹配
    # path('',include('goods.urls','good')),
    url(r'user/', include(('user.urls', 'user'))),
    url(r'cart/', include(('cart.urls', 'cart'))),
    url(r'order/', include(('order.urls', 'order'))),
    url(r'search/', include('haystack.urls')), # 全文检索框架
    url(r'', include(('goods.urls', 'goods'))),
]
