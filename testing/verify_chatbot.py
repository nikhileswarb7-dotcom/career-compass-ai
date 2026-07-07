# Verification Test for AI Coach Chatbot and Gemini loading
# CareerCompass AI

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine.nlp.nlp_classifier import classify_and_respond, load_env_keys

def verify_chatbot():
    print("\nCareerCompass AI - Chatbot Verification")
    print("=" * 60)

    # 1. Load keys and print if GEMINI_API_KEY is found
    load_env_keys()
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"Loaded GEMINI_API_KEY from environment/dotenv: {api_key is not None}")
    if api_key:
        print(f"Key preview: {api_key[:6]}...{api_key[-4:] if len(api_key) > 4 else ''}")
    else:
        print("WARNING: GEMINI_API_KEY is not defined in your .env file!")

    # 2. Test classify_and_respond
    print("\nTesting chatbot classification and response...")
    prompt = "What dynamic programming pattern should I focus on for Blinkit?"
    print(f"User Prompt: '{prompt}'")
    
    response = classify_and_respond(
        prompt,
        dream_company="Blinkit",
        active_stage="Stage 1: Core Alignment"
    )
    print("-" * 60)
    print(f"Coach Response:\n{response}")
    print("-" * 60)

    assert len(response) > 0
    print("[PASS] Chatbot responded successfully!")

if __name__ == "__main__":
    verify_chatbot()
