import os
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from django.conf import settings


class StoryGenerationService:
    def __init__(self):
        self.llm = OllamaLLM(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL
        )
        
    def create_story_chain(self):
        story_template = """
        Create an engaging short story based on the following prompt:
        {user_prompt}
        
        Please write a complete story with a clear beginning, middle, and end. 
        Make it creative and engaging, approximately 300-500 words.
        
        Story:
        """
        
        story_prompt = PromptTemplate(
            input_variables=["user_prompt"],
            template=story_template
        )
        
        return story_prompt | self.llm
    
    def create_character_description_chain(self):
        character_template = """
        Based on this story, create a detailed visual description of the main character:
        
        Story: {story}
        
        Please describe the character's physical appearance, clothing, and distinctive features 
        in vivid detail for image generation. Focus on visual elements only.
        Keep the description under 150 words.
        
        Character Description:
        """
        
        character_prompt = PromptTemplate(
            input_variables=["story"],
            template=character_template
        )
        
        return character_prompt | self.llm
    
    def create_background_description_chain(self):
        background_template = """
        Based on this story, create a detailed visual description of the main setting/background:
        
        Story: {story}
        
        Please describe the environment, scenery, and setting in vivid detail for image generation. 
        Include details about lighting, atmosphere, and visual elements.
        Keep the description under 150 words.
        
        Background Description:
        """
        
        background_prompt = PromptTemplate(
            input_variables=["story"],
            template=background_template
        )
        
        return background_prompt | self.llm
    
    def generate_story(self, user_prompt):
        """Generate a story based on user prompt"""
        story_chain = self.create_story_chain()
        return story_chain.invoke({"user_prompt": user_prompt})
    
    def generate_character_description(self, story):
        """Generate character description based on story"""
        character_chain = self.create_character_description_chain()
        return character_chain.invoke({"story": story})
    
    def generate_background_description(self, story):
        """Generate background description based on story"""
        background_chain = self.create_background_description_chain()
        return background_chain.invoke({"story": story})


class ImageGenerationService:
    def __init__(self):
        # Initialize diffusion pipeline
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
        except ImportError:
            self.pipe = None
            print("Warning: Diffusers not available. Image generation will be disabled.")
    
    def generate_image(self, prompt, filename):
        """Generate image from text prompt"""
        if not self.pipe:
            return None
            
        try:
            # Generate image
            image = self.pipe(
                prompt,
                num_inference_steps=20,
                height=512,
                width=512
            ).images[0]
            
            # Save image
            image.save(filename)
            return filename
        except Exception as e:
            print(f"Error generating image: {e}")
            return None


class ImageMergeService:
    @staticmethod
    def merge_images(character_path, background_path, output_path):
        """Merge character and background images"""
        try:
            from PIL import Image
            import cv2
            import numpy as np
            
            # Load images
            character_img = Image.open(character_path).convert("RGBA")
            background_img = Image.open(background_path).convert("RGB")
            
            # Resize images to match
            target_size = settings.IMAGE_MERGE_SIZE
            character_img = character_img.resize((target_size[0]//2, target_size[1]))
            background_img = background_img.resize(target_size)
            
            # Convert to numpy arrays
            char_array = np.array(character_img)
            bg_array = np.array(background_img)
            
            # Create combined image
            combined = Image.new("RGB", target_size)
            combined.paste(background_img, (0, 0))
            
            # Paste character on the right side
            if char_array.shape[2] == 4:  # Has alpha channel
                combined.paste(character_img, (target_size[0]//2, 0), character_img)
            else:
                combined.paste(character_img, (target_size[0]//2, 0))
            
            combined.save(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error merging images: {e}")
            return None