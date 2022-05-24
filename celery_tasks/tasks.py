# 使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
# 创建一个Celery实例对象
app = Celery('celery_tasks.tasks', broker='redis://172.0.0.1:6379/1')

# 定义任务函数
@app.task
def send_register_active_email(to_email , username, token):
    '''发送激活邮件'''
    # 发邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    # 发件人
    sender = settings.EMAIL_FROM
    # 收件人
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜的注册会员</h1>请点击下面的链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    # 4.返回应答,跳转到首页