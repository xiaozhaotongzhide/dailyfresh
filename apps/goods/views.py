from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
from goods.models import GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache
from order.models import OrderGoods
from django.core.paginator import Paginator
# Create your views here.

# class Test(object):
#     def __init__(self):
#         self.name = 'abc'
#
# t = Test()
# t.age = 10
# print(t.age)


# http://127.0.0.1:8000
# 首页
class IndexView(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')
        if context is None:
            print('设置缓存')
            # 如果没缓存值在数据库在获得值
            # 获取商品的种类信息
            types = GoodsType.objects.all()

            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取首页促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取首页分类商品展示信息
            for type in types: # GoodsType
                # 获取type种类首页分类商品的图片展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类商品的文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                
                type.image_banners = image_banners
                type.title_banners = title_banners


            # 设置缓存
            context = {'types':types,
                       'goods_banners':goods_banners,
                       'promotion_banners':promotion_banners,
                       }
            # 第一个是缓存名称,第二个是缓存的值,第三个是缓存的时间
            cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count = cart_count)

        # 使用模板
        return render(request, 'index.html', context)


# /goods/商品id
# 详情页
class Detailview(View):
    '''详情页'''
    def get(self, request, goods_id):
        '''显示详情页'''
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取同一个SPU的其他规格
        same_spu_skus = GoodsSKU.objects.filter(goods = sku.goods).exclude(id = goods_id)

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d'%user.id
            # 移除列表的goods_id
            conn.lrem(history_key, 0,goods_id)
            # 把goods_id插入列表左侧
            conn.lpush(history_key,goods_id)
            # 只保存用户最近浏览的最近五条数据
            conn.ltrim(history_key, 0, 4)
        # 组织模板上下文
        context = {'sku': sku, 'types': types,
                   'sku_orders': sku_orders,
                   'new_skus': new_skus,
                   'same_spu_skus':same_spu_skus,
                   'cart_count': cart_count}
        # 使用模板
        return render(request, 'detail.html', context)


# /list/种类id/页码?sort=排序方式
# 列表页
class ListView(View):
    '''列表页'''# 种类id 页码 排序方式
    # /list/种类id/页码/排序方式
    def get(self, request, type_id, page):
        '''显示列表页'''
        # 先获取种类的信息
        try:
            type = GoodsType.objects.get(id = type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))

        # 获取排列方式# 获取分类商品的信息
        # sort = default 按照默认id排序
        # sort = price 按照商品价格排序
        # sort = hot 按照商品销量排序
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus, 5)

        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1
        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {'type':type, 'types':types,
                   'skus_page':skus_page,
                   'new_skus':new_skus,
                   'cart_count':cart_count,
                   'sort':sort}
        return render(request, 'list.html', context)


