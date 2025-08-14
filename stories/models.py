from django.db import models
from django.contrib.auth.models import User


class Story(models.Model):
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    story_text = models.TextField()
    character_description = models.TextField()
    background_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def first_image(self):
        """Get the first image associated with this story"""
        return self.images.first()

    @property
    def combined_image(self):
        """Get the combined image for this story"""
        return self.images.filter(image_type='combined').first()

    @property
    def character_image(self):
        """Get the character image for this story"""
        return self.images.filter(image_type='character').first()

    @property
    def background_image(self):
        """Get the background image for this story"""
        return self.images.filter(image_type='background').first()

    class Meta:
        ordering = ['-created_at']


class GeneratedImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='images')
    image_type = models.CharField(max_length=20, choices=[
        ('character', 'Character'),
        ('background', 'Background'),
        ('combined', 'Combined')
    ])
    image_file = models.ImageField(upload_to='generated_images/')
    prompt_used = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.story.title} - {self.image_type}"

    class Meta:
        ordering = ['-created_at']


class GenerationSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('generating_story', 'Generating Story'),
        ('generating_images', 'Generating Images'),
        ('merging_images', 'Merging Images'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    progress_percentage = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    story = models.OneToOneField(Story, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.status}"
