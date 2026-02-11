try:
    from google import genai
    print("Success: from google import genai")
    print(dir(genai))
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
