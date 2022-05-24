from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
from fdfs_client.client import get_tracker_conf
class FDFSStorage(Storage):
    '''fast dfs文件存储类'''
    '''fast dfs文件存储类'''
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = get_tracker_conf(r'C:\Users\86157\Desktop\pytest\Django框架\天天生鲜\dailyfresh\utils\fdfs\client.conf')
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url
    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass
    def _save(self, name, content):
        '''保存文件时使用'''
        # name:你选择上传文件的名字

        # content:包含上传文件内容的file对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到
        res = client.upload_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到fast dfs失败')
        # 获取返回的文件id
        filename = res.get('Remote file_id')
        return filename

    def exists(self,name):
        '''判断文件名是否可以'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return self.base_url+name