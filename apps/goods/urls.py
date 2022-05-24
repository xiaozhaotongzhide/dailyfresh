from django.conf.urls import url
from goods.views import IndexView,Detailview,ListView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'), # 首页
    url(r'^goods/(?P<goods_id>\d+)$', Detailview.as_view(), name='detail'), #详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list')
]
