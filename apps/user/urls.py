from django.conf.urls import url
from user.views import RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,UsersiteView,LogoutView
urlpatterns = [
    # url(r'^register$', views.register, name='register'), #注册
    # url(r'^register_handle$', views.register_handle, name='register_handle'), #注册处理
    # 注册类,根据不同的函数请求,返回不同的方法
    url(r'^register$', RegisterView.as_view(),name='register'),
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),#用户激活
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^logout$',LogoutView.as_view(),name='logout'),

    url(r'^$',UserInfoView.as_view(),name='user'),#用户信息页
    url(r'^order/(?P<page>\d+)$',UserOrderView.as_view(),name='order'),#用户订单页
    url(r'^address$',UsersiteView.as_view(),name='address')
]
