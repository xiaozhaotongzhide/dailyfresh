from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse
import re
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from user.models import User,Address
from goods.models import GoodsSKU
from order.models import OrderInfo,OrderGoods
from django.core.mail import send_mail
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
from celery_tasks.tasks import send_register_active_email
# 这个用户类无法满足使用
# from django.contrib.auth.models import User
# Create your views here.
def register(request):
    # 使用同一个页面,进行注册处理
    '''显示注册页面'''
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        '''进行注册处理'''
        # 1.接收数据
        username = request.POST['user_name']
        password = request.POST['pwd']
        email = request.POST['email']
        allow = request.POST['allow']
        # 2.数据校验
        print('1')
        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.save()
        # 4.返回应答,跳转到首页
        return redirect(reverse('goods:index'))

class RegisterView(View):
    '''注册类视图'''
    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')
    def post(self, request):
        '''进行注册'''
        '''进行注册处理'''
        # 1.接收数据
        username = request.POST['user_name']
        password = request.POST['pwd']
        email = request.POST['email']
        allow = request.POST['allow']
        # 2.数据校验
        print('1')
        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # 发送激活邮件
        # 激活链接中需要包含用户身份信息,并且要把身份信息加密处理

        # 加密用户的身份信息,生产激活token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        # 默认解码方式为utf8
        # 效果就是去掉url前面的b
        token = token.decode()
        # 发邮件
        # 这个是异步,可以大幅度提升服务器速度
        #send_register_active_email.delay(email, username ,token)
        # 发邮件
        subject = '天天生鲜欢迎信息'
        message = ''
        # 发件人
        sender = settings.EMAIL_FROM
        # 收件人
        receiver = [email]
        html_message = '<h1>%s, 欢迎您成为天天生鲜的注册会员</h1>请点击下面的链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
            username, token, token)
        send_mail(subject, message, sender, receiver, html_message=html_message)
        # 4.返回应答,跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密,获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 应答,跳转到登录页面
            return redirect(reverse('goods:index'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')

class LoginView(View):
    '''登录页面'''
    def get(self, request):
        '''显示登录页面'''
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('usernaem')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username':username, 'checked':checked})


    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'数据不完整'})

        # 业务处理,登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 用户已激活
                # 用户登录状态
                login(request, user)

                # 获取登录后要跳转的页面
                # 默认跳转到首页
                next = request.GET.get('next', reverse('goods:index'))
                response = redirect(next)
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                   response.set_cookie('username',username, max_age=7*24*3600)
                else:
                   response.delete_cookie('username')
                # 跳转到首页
                return response
            else:
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        # 返回应答

class LogoutView(View):
    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))
# /user
class UserInfoView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self, request):
        '''显示'''
        # page = 'user'
        # request.user
        # 如果用户未登录->Anonymoususer的实例
        # 如果登录了->user实例
        # user.is_authenticated 用户登录显示true

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)
        # 获取用户的历史浏览记录
        con = get_redis_connection('default')

        history_key = 'history_%d'%user.id

        # 获取用户最新浏览的五个商品id
        sku_ids = con.lrange(history_key,0,4)
        # 从数据中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        # 组织上下文
        context = {'page':'user',
                   'address':address,
                   'goods_li':goods_li}
        # 除了给模板传递模板遍历,django框架还把user对象传递给浏览器
        return render(request, 'user_center_info.html',context)

# /user/order
class UserOrderView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self, request, page):
        '''显示'''
        '''显示'''
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count*order_sku.price
                # 动态给order_sku增加属性amount,保存订单商品的小计
                order_sku.amount = amount

            # 动态给order增加属性，保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 2)

        # 处理页码
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)
        # 组织上下文
        context = {'order_page':order_page,
                   'pages':pages,
                   'page': 'order'}
        # 使用模板
        return render(request, 'user_center_order.html', context)

# /user/address
class UsersiteView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self, request):
        '''显示'''
        # page = 'address'
        # 获取用户的默认收货地址
        user = request.user
        # try:
        #     Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html',{'page':'address','address':address})
    def post(self, request):
        '''地址添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 校验数据

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 地址添加
        user = request.user

        # try:
        #     Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        # 添加新地址
        # 在这添加新地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 如果用户已经存在默认地址,添加的地址不作为默认地址,否则为地址
        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))