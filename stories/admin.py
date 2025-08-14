from django.contrib import admin
from .models import Story, GeneratedImage, GenerationSession


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'prompt', 'story_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'user', 'prompt')
        }),
        ('Generated Content', {
            'fields': ('story_text', 'character_description', 'background_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('story', 'image_type', 'created_at')
    list_filter = ('image_type', 'created_at')
    search_fields = ('story__title', 'prompt_used')
    readonly_fields = ('created_at',)


@admin.register(GenerationSession)
class GenerationSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'status', 'progress_percentage', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('session_id',)
    readonly_fields = ('created_at',)
