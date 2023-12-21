from django.contrib import admin

from core.models import Config, Image, Item, Match, Notification


admin.site.site_header = "Site ADMIN"
admin.site.index_title = "Features"




class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state', "main_cat", "sub_cat", 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'state')
    ordering = ('-created_at',)
    # search_fields = ('email_char', 'task_id')
    filter_horizontal = ()

admin.site.register(Item, ItemAdmin)
admin.site.register(Image)
admin.site.register(Match)
admin.site.register(Config)
admin.site.register(Notification)




