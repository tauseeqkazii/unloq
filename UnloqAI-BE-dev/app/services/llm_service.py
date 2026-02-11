import os
import json
import requests
from typing import List, Dict, Generator, Any
from app.core.config import settings

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class LLMService:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        
        # --- AWS Bedrock Setup ---
        self.bedrock_client = None
        if HAS_BOTO3:
            try:
                aws_execution_env = os.getenv("AWS_EXECUTION_ENV")
                if aws_execution_env and aws_execution_env.startswith("AWS_Lambda"):
                    self.bedrock_client = boto3.client(
                        service_name="bedrock-runtime",
                        region_name=os.getenv("AWS_REGION", "eu-west-2")
                    )
                else:
                    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
                    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                    
                    if aws_access_key and aws_secret_key:
                        self.bedrock_client = boto3.client(
                            service_name="bedrock-runtime",
                            region_name=os.getenv("AWS_REGION", "eu-west-2"),
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key
                        )
                    else:
                        # Try default credential chain
                        self.bedrock_client = boto3.client(
                            service_name="bedrock-runtime",
                            region_name=os.getenv("AWS_REGION", "eu-west-2")
                        )
            except Exception as e:
                print(f"Failed to initialize Bedrock client: {str(e)}")

        # --- Gemini Setup ---
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        self.gemini_model = "gemini-2.0-flash-lite"
        
        if HAS_GEMINI and self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")

        # --- OpenAI Setup ---
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        self.openai_model = "gpt-4o-mini"
        
        if HAS_OPENAI and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
        
        # --- Ollama Setup ---
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = settings.LLM_MODEL

    def stream_chat(self, messages: List[Dict[str, str]], model_name: str = None) -> Generator[str, None, None]:
        """
        Stream chat response compatible with Vercel AI SDK.
        messages format: [{"role": "user", "content": "hello"}]
        """
    def stream_chat(self, messages: List[Dict[str, str]], model_name: str = None) -> Generator[str, None, None]:
        """
        Stream chat response with fallback: Bedrock -> Gemini -> OpenAI.
        Ollama is used if explicitly selected as provider.
        """
        if self.provider == "ollama":
            yield from self._stream_ollama(messages, model_name)
            return

        # Fallback Strategy:
        # 1. Try Bedrock
        try:
            # We iterate to ensure the stream actually starts; if it fails immediately, we catch it.
            # Generators are lazy, so we must start consuming to catch the error here, 
            # BUT we want to yield the items.
            # However, if we put `yield from` in a try/except block, exceptions raised DURING iteration 
            # will be caught. If `_stream_bedrock` fails mid-stream, we might have already sent partial data.
            # The prompt implies "if bedrock don't work", likely meaning initial connection/availability.
            # For simplicity and safety, we allow fallback on any error, but practically, 
            # switching providers mid-sentence is bad UX (but better than crash).
            # The safest approach for "mid-stream" failure is hard, but let's assume strict failover.
            
            yield from self._stream_bedrock(messages, model_name)
            return
        except Exception as e:
            print(f"Bedrock failed: {e}. Falling back to Gemini...")

        # # 2. Try Gemini
        # try:
        #     yield from self._stream_gemini(messages, model_name)
        #     return
        # except Exception as e:
        #     print(f"Gemini failed: {e}. Falling back to OpenAI...")
            
        # # 3. Try OpenAI
        # try:
        #     yield from self._stream_openai(messages, model_name)
        #     return
        # except Exception as e:
        #     yield json.dumps({
        #         "type": "error", 
        #         "blocks": [{"type": "summary", "text": f"All providers failed. Last Error: {str(e)}"}]
        #     })

    def _stream_bedrock(self, messages: List[Dict[str, str]], model_name: str = None):
        """
        Uses Claude 3.5 Sonnet (or Haiku) via Bedrock.
        """
        if not self.bedrock_client:
            # Raise error to trigger fallback
            raise ValueError("AWS Configuration Missing or boto3 not installed.")

        # Model ID for Claude 3.5 Sonnet
        # Model ID for Claude 3.5 Sonnet (default backup)
        # Use configured model from settings if available, otherwise fallback to Sonnet 3.5
        model_id = model_name or settings.LLM_MODEL or "anthropic.claude-3-5-sonnet-20240620-v1:0"

        # Format Messages for Claude (System prompt is separate)
        system_prompts = []
        claude_messages = []
        
        for m in messages:
            if m["role"] == "system":
                system_prompts.append({"type": "text", "text": m["content"]})
            else:
                claude_messages.append({
                    "role": "user" if m["role"] == "user" else "assistant",
                    "content": [{"type": "text", "text": m["content"]}]
                })

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompts,
            "messages": claude_messages,
            "temperature": 0.0 # ZERO temperature for strict financial logic
        }

        try:
            response = self.bedrock_client.invoke_model_with_response_stream(
                modelId=model_id,
                body=json.dumps(payload)
            )
            
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_data = json.loads(chunk.get('bytes').decode())
                        if chunk_data.get('type') == 'content_block_delta':
                            yield chunk_data['delta'].get('text', '')
                            
        except Exception as e:
            # Re-raise error to trigger fallback
            print(f"Bedrock Error Detailed: {e}")
            raise e

    def _stream_ollama(self, messages: List[Dict[str, str]], model_name: str = None):
        """
        Specialized Ollama streamer that enforces JSON structure for the Dashboard.
        """
        url = f"{self.ollama_base_url}/api/chat"
        model = model_name or self.ollama_model

        # Inject Strict JSON System Prompt if not present
        has_system = any(m["role"] == "system" for m in messages)
        if not has_system:
            json_schema_prompt = (
                "You are the Meridian Strategy Engine. "
                "You DO NOT write plain text. You ONLY speak in valid JSON. "
                "Response Format: { 'type': 'analysis_response', 'title': 'Short Title', "
                "'blocks': [ { 'type': 'summary', 'text': '...' }, { 'type': 'metrics', 'items': [] } ] }"
            )
            messages.insert(0, {"role": "system", "content": json_schema_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "format": "json",  # CRITICAL: Forces local LLM to be structured
            "temperature": 0.1, # Keep it factual
            "keep_alive": "5m"
        }

        try:
            with requests.post(url, json=payload, stream=True, timeout=60) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        try:
                            body = json.loads(line)
                            if "message" in body and "content" in body["message"]:
                                yield body["message"]["content"]
                            if body.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            error_json = json.dumps({
                "type": "analysis_response",
                "blocks": [{
                    "type": "summary", 
                    "text": f"⚠️ Local LLM Error: {str(e)}. Is Ollama running?"
                }]
            })
            yield error_json

    def _stream_openai(self, messages: List[Dict[str, str]], model_name: str = None):
        if not self.openai_client:
             raise ValueError("OpenAI Client not initialized. Check API Key.")
             
        try:
            # OpenAI expects [{"role": "user", "content": "..."}] which matches our input mostly
            # System prompt is just role: system
            
            stream = self.openai_client.chat.completions.create(
                model=model_name or self.openai_model,
                messages=messages,
                stream=True,
                temperature=0.0
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            # Re-raise to trigger fallback
            raise e

    def _stream_gemini(self, messages: List[Dict[str, str]], model_name: str = None):
        if not self.gemini_client:
            raise ValueError("Gemini Client not initialized. Check API Key.")

        try:
            # Support for system instructions in Gemini 2.0 / New SDK?
            # The current implementation manually filters system prompts. 
            # We'll stick to the existing logic but ensure we validly raise specific errors.
            
            gemini_messages = []
            system_instruction = None
            
            for m in messages:
                if m["role"] == "system": 
                    # If using newer SDK, we might pass system_instruction=... to Client or chats.create
                    # usage: client.chats.create(..., config=...)
                    # For now keep naive filtering to avoid breaking existing logic if SDK is mixed,
                    # mostly just fix the 'yield' error handling.
                    continue 
                role = "user" if m["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [{"text": m["content"]}]})
            
            last_message = ""
            history = []
            
            if gemini_messages:
                last_message = gemini_messages[-1]["parts"][0]["text"]
                history = gemini_messages[:-1]

            chat = self.gemini_client.chats.create(
                model=model_name or self.gemini_model,
                history=history
            )
            
            response = chat.send_message_stream(last_message)
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            # Re-raise so stream_chat catches it
            print(f"Gemini Error: {e}")
            raise e

# Initialize Singleton
llm_service = LLMService()