# 🔧 Prompt Engineering Documentation

## Overview

This document details the sophisticated prompt engineering strategies used in Story Agent to create coherent, engaging narratives with visual descriptions optimized for image generation.

## Multi-Agent Prompt Architecture

### 1. Story Generation Agent

**Template Structure:**
```python
story_template = """
Create an engaging short story based on the following prompt:
{user_prompt}

Please write a complete story with a clear beginning, middle, and end. 
Make it creative and engaging, approximately 300-500 words.

Story:
"""
```

**Design Rationale:**
- Clear instruction hierarchy with specific word count guidance
- Emphasis on narrative structure (beginning, middle, end)
- Creative freedom within structured constraints
- Template variable for dynamic user input integration

### 2. Character Description Agent

**Template Structure:**
```python
character_template = """
Based on this story, create a detailed visual description of the main character:

Story: {story}

Please describe the character's physical appearance, clothing, and distinctive features 
in vivid detail for image generation. Focus on visual elements only.
Keep the description under 150 words.

Character Description:
"""
```

**Visual Optimization Features:**
- Focus on purely visual elements (appearance, clothing, accessories)
- Exclusion of personality traits or emotions
- Optimized word count for Stable Diffusion processing
- Context-aware description based on story narrative

### 3. Background Description Agent

**Template Structure:**
```python
background_template = """
Based on this story, create a detailed visual description of the main setting/background:

Story: {story}

Please describe the environment, scenery, and setting in vivid detail for image generation. 
Include details about lighting, atmosphere, and visual elements.
Keep the description under 150 words.

Background Description:
"""
```

**Environmental Focus:**
- Atmospheric details (lighting, weather, mood)
- Spatial descriptions (indoor/outdoor, scale, layout)
- Visual elements that complement the narrative
- Optimized for diffusion model understanding

## Context Chaining Strategy

### Sequential Information Flow
1. **User Prompt** → **Story Generation**
2. **Generated Story** → **Character Description**
3. **Generated Story** → **Background Description**
4. **Descriptions** → **Image Generation**

### Context Preservation
- Each agent receives the complete story context
- Visual descriptions maintain narrative consistency
- Error handling prevents context loss during chaining
- Validation checkpoints ensure quality at each stage

## Prompt Optimization Techniques

### 1. Constraint Specification
- Explicit word count limits prevent excessive generation
- Format specifications ensure consistent output structure
- Clear instruction hierarchy guides model behavior

### 2. Domain-Specific Language
- Visual terminology optimized for image generation models
- Narrative structure keywords for story coherence
- Atmospheric descriptors for environmental consistency

### 3. Template Validation
- Input sanitization prevents prompt injection
- Output validation ensures format compliance
- Error recovery mechanisms handle generation failures

## Sample Prompt Chains

### Example 1: Fantasy Adventure
**User Input:** "A brave knight discovers a magical forest"

**Generated Story Chain:**
```
Story: "Sir Edward ventured into the enchanted woods..."
↓
Character: "A tall knight in gleaming silver armor with blue plume..."
↓
Background: "Ancient forest with glowing mushrooms and ethereal mist..."
```

### Example 2: Sci-Fi Mystery
**User Input:** "A detective investigates strange signals from space"

**Generated Story Chain:**
```
Story: "Detective Morgan received the transmission at midnight..."
↓
Character: "A sharp-eyed detective in dark coat with scanning device..."
↓
Background: "Futuristic city skyline with radio telescopes and neon lights..."
```

## Quality Metrics

### Narrative Coherence
- Beginning-middle-end structure maintained: ✅
- Character consistency throughout: ✅
- Setting consistency maintained: ✅

### Visual Description Quality
- Detailed appearance descriptions: ✅
- Atmospheric environment details: ✅
- Image-generation optimized language: ✅

### Template Effectiveness
- Consistent output format: ✅
- Appropriate content length: ✅
- Context preservation: ✅

## Future Enhancements

### Planned Improvements
1. **Dynamic Templates**: Adaptive prompts based on genre detection
2. **Style Transfer**: Genre-specific prompt variations
3. **Multilingual Support**: Template translations for global use
4. **Advanced Chaining**: Recursive refinement loops

### Experimentation Areas
- Emotional tone specification
- Cultural context adaptation
- Interactive prompt refinement
- Multi-character story support

---

*This documentation is regularly updated as prompt engineering techniques evolve.*