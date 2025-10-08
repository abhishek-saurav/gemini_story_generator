print("project starting...")

from google import genai
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key: 
    raise ValueError("API key not found") 

client = genai.Client(api_key= api_key) 

def create_advanced_prompt(style): 

    base_prompt = f"""
    ** your persona: ** You are a friendly and engaging storyteller. Your goal is to tell a story that ais fun and easy. 
    **Your main goal** write a story in simple, clear and modern english.
    ** Your task: create one single story that connects all the provided images in order.
    **style requriements**: the story must fit the '{style}' genre. 
    """

    return base_prompt


# function -- image , style -- > story 

def generate_story_from_images(images, style): 

    response = client.models.generate_content(
        model= 'gemini-2.5-flash-lite', 
        contents= [images, create_advanced_prompt(style)]
    )
    
    return response.text


# function -- story -- out: audio file 

def narrate_story(story_text): 
    try: 
        tts = gTTS(text= story_text, lang= 'en', slow= False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp) # converts the text to speech file 
        audio_fp.seek(0) # file will play from start 

        return audio_fp
    
    except Exception as e: 
        return f"An unexpected error has occured during the API call"