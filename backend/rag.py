import os
import re
import asyncio
import logging
from openai import OpenAI
from backend.config import OPENROUTER_API_KEY, FREE_MODELS
from backend.vectorstore import VectorStore
from backend.prompts import SYSTEM_PROMPT, get_casual_prompt, get_full_prompt

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def clean_source_name(name: str) -> str:
    try:
        name = os.path.basename(name)
        name = name.replace(".txt", "")
        name = re.sub(r'\b\d{4}\b', '', name)
        name = name.replace("_", " ").replace("-", " ")
        name = re.sub(r'^[\d\s\-]+', '', name)
        name = re.sub(r'\s{2,}', ' ', name)
        return name.strip()
    except Exception:
        return name.strip()

def is_casual_message(text: str) -> bool:
    casual_keywords = [
        "hi","hello","hey","hiya","howdy",
        "good morning","good night","good evening",
        "good afternoon","how are you","how r you",
        "whats up","what's up","sup",
        "who are you","what is your name",
        "which model","what model","which ai",
        "what are you","are you gpt","are you ai",
        "who made you","who created you",
        "tell me about yourself","introduce yourself",
        "what can you do","what version",
        "thank you","thanks","thank u","thx",
        "bye","goodbye","see you","cya",
        "you are great","you are amazing","awesome",
        "that was helpful","i understand","i get it",
        "tell me a joke","joke please",
        "i am stuck","i am confused","i am frustrated",
        "i am bored","i give up","i am nervous",
        "motivate me","encourage me","i am tired",
        "can we take a break","nice","cool",
        "ok","okay","sure","great",
        "i am ready","lets start","let us start",
        "let's go","lets go","begin","start"
    ]
    text_lower = text.lower().strip()
    if len(text_lower.split()) <= 6:
        for kw in casual_keywords:
            if kw in text_lower:
                return True
    for kw in casual_keywords:
        if text_lower == kw or text_lower.startswith(kw + " "):
            return True
    return False

async def call_with_fallback_async(messages, max_tokens, temperature):
    last_error = None
    loop = asyncio.get_event_loop()
    for model in FREE_MODELS:
        try:
            logger.info(f"Trying model: {model}")
            response = await loop.run_in_executor(
                None,
                lambda m=model: client.chat.completions.create(
                    model=m,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            logger.info(f"Success with model: {model}")
            return response
        except Exception as e:
            err = str(e)
            logger.warning(f"Failed {model}: {err[:60]}")
            last_error = err
            await asyncio.sleep(0.5)
            continue
    class MockMessage:
        content = "This is a mock response from Mentora AI! Your OpenRouter API key is missing or invalid, but the UI is fully functional and successfully communicated with the backend."
    class MockChoice:
        message = MockMessage()
    class MockResponse:
        choices = [MockChoice()]
    logger.warning("All models failed. Returning mock response for UI testing.")
    return MockResponse()

async def ask_ai_pipeline(student_question: str):
    is_casual = is_casual_message(student_question)
    
    if is_casual:
        logger.info("Conversation mode...")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_casual_prompt(student_question)}
        ]
        response = await call_with_fallback_async(messages, max_tokens=200, temperature=0.9)
        mode = "conversation"
        sources = []
    else:
        logger.info("Teaching mode... retrieving context")
        context, raw_sources = VectorStore.retrieve(student_question, top_k=5)
        clean_sources = list(set([clean_source_name(s) for s in raw_sources])) if raw_sources else []
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_full_prompt(student_question, context)}
        ]
        response = await call_with_fallback_async(messages, max_tokens=1200, temperature=0.7)
        mode = "teaching"
        sources = clean_sources

    response_text = response.choices[0].message.content
    
    return {
        "answer": response_text.strip(),
        "mode": mode,
        "sources": sources
    }
