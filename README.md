# 📚 AI Story Generator with Image Creation

A Django-powered web application that uses LangChain and Ollama to generate creative stories, then creates character and background images using Stable Diffusion, and finally merges them into combined scenes.

## 🌟 Features

- **Story Generation**: Uses LangChain with Ollama LLMs to create engaging stories
- **Character Descriptions**: AI-powered character descriptions for image generation
- **Background Descriptions**: AI-powered environment descriptions
- **Image Generation**: Uses Stable Diffusion/Flux.1 for creating visual content
- **Image Merging**: Combines character and background images using Pillow/OpenCV
- **Web Interface**: Beautiful Django web interface with real-time progress tracking
- **Progress Tracking**: Real-time updates on generation progress
- **Gallery**: View all generated stories and their images

## 🚀 Architecture

```
User Input (Story Prompt)
    ↓
LangChain + Ollama (Story Generation)
    ↓
LangChain (Character & Background Descriptions)
    ↓
Stable Diffusion/Flux.1 (Image Generation)
    ↓
Pillow/OpenCV (Image Merging)
    ↓
Django Web Interface (Display Results)
```

## 📋 Prerequisites

1. **Python 3.8+**
2. **Ollama** - Install from [https://ollama.ai/](https://ollama.ai/)
3. **CUDA-compatible GPU** (recommended for image generation)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd story_agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install and setup Ollama**
```bash
# Install Ollama (follow instructions at https://ollama.ai/)
# Pull a language model (e.g., llama2)
ollama pull llama2
```

5. **Configure Django settings**
Edit `story_generator/settings.py` if needed:
```python
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"  # Change to your preferred model
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser** (optional)
```bash
python manage.py createsuperuser
```

## 🎮 Usage

1. **Start Ollama server**
```bash
ollama serve
```

2. **Start Django development server**
```bash
python manage.py runserver
```

3. **Open your browser** and navigate to `http://localhost:8000`

4. **Generate stories**:
   - Enter a creative story prompt
   - Click "Generate Story & Images"
   - Watch the real-time progress
   - View your generated story with images!

## 📁 Project Structure

```
story_agent/
├── manage.py
├── requirements.txt
├── README.md
├── story_generator/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py
├── stories/                 # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # Web views
│   ├── urls.py             # App URLs
│   ├── services.py         # LangChain & Image services
│   ├── admin.py            # Django admin
│   └── templates/          # HTML templates
│       └── stories/
│           ├── base.html
│           ├── home.html
│           ├── story_detail.html
│           └── story_list.html
├── static/                 # CSS, JS, images
├── media/                  # Generated images
└── db.sqlite3             # SQLite database
```

## 🧩 Core Components

### 1. Story Generation Service (`stories/services.py`)
- **StoryGenerationService**: Uses LangChain with Ollama for text generation
- **ImageGenerationService**: Handles Stable Diffusion image creation
- **ImageMergeService**: Merges character and background images

### 2. Django Models (`stories/models.py`)
- **Story**: Stores generated stories and descriptions
- **GeneratedImage**: Manages character, background, and combined images
- **GenerationSession**: Tracks generation progress

### 3. Web Interface
- **Home Page**: Story prompt input with real-time progress
- **Story Detail**: View complete story with all images
- **Story List**: Gallery of all generated stories

## 🎨 Customization

### LLM Models
Change the model in `settings.py`:
```python
OLLAMA_MODEL = "codellama"  # or "mistral", "neural-chat", etc.
```

### Image Generation
Modify image generation settings in `settings.py`:
```python
MAX_IMAGE_SIZE = (1024, 1024)
IMAGE_MERGE_SIZE = (1024, 512)
```

### Prompts
Edit prompts in `stories/services.py` to customize story generation style.

## 🐛 Troubleshooting

### Common Issues

1. **Ollama connection error**
   - Ensure Ollama is running: `ollama serve`
   - Check if model is installed: `ollama list`

2. **CUDA out of memory**
   - Reduce image size in settings
   - Use CPU for image generation (slower but works)

3. **Missing images**
   - Check media directory permissions
   - Ensure Stable Diffusion dependencies are installed

4. **Slow generation**
   - Use smaller/faster models
   - Enable GPU acceleration
   - Reduce image resolution

## 📊 Performance Tips

- Use GPU acceleration for faster image generation
- Choose smaller language models for faster text generation
- Implement Redis caching for production use
- Use background task queues (Celery) for heavy operations

## 🚀 Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Configure proper static file serving
3. Set `DEBUG = False`
4. Use environment variables for sensitive settings
5. Implement proper logging and monitoring
6. Use Gunicorn or uWSGI as WSGI server
7. Set up Redis for session storage and caching

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain team for the amazing framework
- Ollama team for local LLM serving
- Hugging Face for Stable Diffusion models
- Django community for the web framework

---

**Happy Story Generation! 📖✨**