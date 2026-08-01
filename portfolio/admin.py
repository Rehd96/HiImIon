from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    """Fallback only — the real analytics live at /panel/."""

    list_display = ('created_at', 'path', 'status', 'latency_ms', 'is_bot')
    list_filter = ('is_bot', 'status', 'project_slug')
    search_fields = ('path', 'ip', 'user_agent', 'referer')
    date_hierarchy = 'created_at'
    readonly_fields = [field.name for field in PageView._meta.fields]

    def has_add_permission(self, request):
        return False
