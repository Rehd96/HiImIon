from django.contrib import admin
from .models import KittenProfile, KittenPost


@admin.register(KittenProfile)
class KittenProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age_text', 'gender', 'location', 'phone_number', 'is_adopted', 'updated_at')
    list_editable = ('phone_number', 'is_adopted')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(KittenPost)
class KittenPostAdmin(admin.ModelAdmin):
    list_display = ('title_or_tag', 'kitten', 'media_type', 'tag', 'likes', 'created_at')
    list_filter = ('tag', 'media_type', 'created_at')
    search_fields = ('title', 'caption')

    def title_or_tag(self, obj):
        return obj.title or obj.get_tag_display()
    title_or_tag.short_description = 'Titolo / Tag'
