import os
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib import messages
from .models import Story, GeneratedImage, GenerationSession
from .services import StoryGenerationService, ImageGenerationService, ImageMergeService
import json


def home(request):
    """Home page with story generation form"""
    recent_stories = Story.objects.all()[:5]
    return render(request, 'stories/home.html', {'recent_stories': recent_stories})


def story_detail(request, story_id):
    """Display a specific story with its images"""
    story = get_object_or_404(Story, id=story_id)
    images = story.images.all()
    return render(request, 'stories/story_detail.html', {
        'story': story,
        'images': images
    })


@csrf_exempt
def generate_story_ajax(request):
    """AJAX endpoint to generate story and images"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)
        
        # Create generation session
        session_id = str(uuid.uuid4())
        session = GenerationSession.objects.create(
            session_id=session_id,
            status='pending'
        )
        
        # Start generation process
        generate_story_content(session, user_prompt)
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'message': 'Story generation started'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def generate_story_content(session, user_prompt):
    """Generate story content and images"""
    try:
        # Update session status
        session.status = 'generating_story'
        session.progress_percentage = 10
        session.save()
        
        # Initialize services
        story_service = StoryGenerationService()
        image_service = ImageGenerationService()
        merge_service = ImageMergeService()
        
        # Generate story
        story_text = story_service.generate_story(user_prompt)
        
        # Create story object
        story = Story.objects.create(
            title=f"Story from: {user_prompt[:50]}...",
            prompt=user_prompt,
            story_text=story_text,
            character_description="",
            background_description=""
        )
        
        session.story = story
        session.progress_percentage = 30
        session.save()
        
        # Generate character description
        character_desc = story_service.generate_character_description(story_text)
        story.character_description = character_desc
        
        # Generate background description
        background_desc = story_service.generate_background_description(story_text)
        story.background_description = background_desc
        story.save()
        
        session.status = 'generating_images'
        session.progress_percentage = 50
        session.save()
        
        # Create media directories if they don't exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'generated_images')
        os.makedirs(media_dir, exist_ok=True)
        
        # Generate character image
        char_filename = f"character_{story.id}_{uuid.uuid4().hex[:8]}.png"
        char_path = os.path.join(media_dir, char_filename)
        
        if image_service.generate_image(character_desc, char_path):
            GeneratedImage.objects.create(
                story=story,
                image_type='character',
                image_file=f'generated_images/{char_filename}',
                prompt_used=character_desc
            )
        
        session.progress_percentage = 70
        session.save()
        
        # Generate background image
        bg_filename = f"background_{story.id}_{uuid.uuid4().hex[:8]}.png"
        bg_path = os.path.join(media_dir, bg_filename)
        
        if image_service.generate_image(background_desc, bg_path):
            GeneratedImage.objects.create(
                story=story,
                image_type='background',
                image_file=f'generated_images/{bg_filename}',
                prompt_used=background_desc
            )
        
        session.status = 'merging_images'
        session.progress_percentage = 85
        session.save()
        
        # Merge images if both exist
        if os.path.exists(char_path) and os.path.exists(bg_path):
            combined_filename = f"combined_{story.id}_{uuid.uuid4().hex[:8]}.png"
            combined_path = os.path.join(media_dir, combined_filename)
            
            if merge_service.merge_images(char_path, bg_path, combined_path):
                GeneratedImage.objects.create(
                    story=story,
                    image_type='combined',
                    image_file=f'generated_images/{combined_filename}',
                    prompt_used=f"Character: {character_desc}\nBackground: {background_desc}"
                )
        
        # Complete session
        session.status = 'completed'
        session.progress_percentage = 100
        session.save()
        
    except Exception as e:
        session.status = 'failed'
        session.error_message = str(e)
        session.save()


def check_generation_status(request, session_id):
    """Check the status of a generation session"""
    try:
        session = get_object_or_404(GenerationSession, session_id=session_id)
        
        response_data = {
            'status': session.status,
            'progress': session.progress_percentage,
            'error': session.error_message
        }
        
        if session.status == 'completed' and session.story:
            response_data['story_id'] = session.story.id
            response_data['redirect_url'] = f'/story/{session.story.id}/'
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def story_list(request):
    """List all generated stories"""
    stories = Story.objects.all()
    return render(request, 'stories/story_list.html', {'stories': stories})
