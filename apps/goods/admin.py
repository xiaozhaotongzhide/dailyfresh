from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType,IndexPromotionBanner,IndexGoodsBanner,IndexTypeGoodsBanner
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        # 清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        # 清除首页的缓存数据
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)