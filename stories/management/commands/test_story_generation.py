from django.core.management.base import BaseCommand
from stories.services import StoryGenerationService
import os


class Command(BaseCommand):
    help = 'Test story generation with LangChain and Ollama'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prompt',
            type=str,
            default="A brave knight discovers a magical forest",
            help='Story prompt to test with'
        )

    def handle(self, *args, **options):
        prompt = options['prompt']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing story generation with prompt: "{prompt}"')
        )
        
        try:
            # Initialize story service
            story_service = StoryGenerationService()
            
            self.stdout.write('Generating story...')
            story = story_service.generate_story(prompt)
            
            self.stdout.write(self.style.SUCCESS('✓ Story generated successfully!'))
            self.stdout.write(f'\nGenerated Story:\n{"-" * 50}')
            self.stdout.write(story)
            
            self.stdout.write(f'\n{"-" * 50}')
            self.stdout.write('Generating character description...')
            character_desc = story_service.generate_character_description(story)
            
            self.stdout.write(self.style.SUCCESS('✓ Character description generated!'))
            self.stdout.write(f'\nCharacter Description:\n{character_desc}')
            
            self.stdout.write(f'\n{"-" * 50}')
            self.stdout.write('Generating background description...')
            background_desc = story_service.generate_background_description(story)
            
            self.stdout.write(self.style.SUCCESS('✓ Background description generated!'))
            self.stdout.write(f'\nBackground Description:\n{background_desc}')
            
            self.stdout.write(f'\n{"-" * 50}')
            self.stdout.write(
                self.style.SUCCESS('🎉 All text generation tests passed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during story generation: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Make sure Ollama is running with: ollama serve')
            )