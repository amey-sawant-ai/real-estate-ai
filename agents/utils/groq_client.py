import os
from groq import Groq
from cerebras.cloud.sdk import Cerebras

class LLMKeyManager:
    def __init__(self):
        self.keys = []
        # Support up to 10 keys for Groq
        for i in range(1, 11):
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key:
                self.keys.append({"provider": "groq", "key": key, "index": i - 1})
        
        # Fallback to the default key if no numbered keys exist
        if not [k for k in self.keys if k['provider'] == 'groq']:
            default_key = os.getenv("GROQ_API_KEY")
            if default_key:
                self.keys.append({"provider": "groq", "key": default_key, "index": 0})
                
        # Support up to 10 keys for Cerebras
        for i in range(1, 11):
            key = os.getenv(f"CEREBRAS_API_KEY_{i}")
            if key:
                self.keys.append({"provider": "cerebras", "key": key, "index": i - 1})
                
        self.current_index = 0

    def rotate(self):
        if not self.keys:
            return
        self.current_index = (self.current_index + 1) % len(self.keys)

    def safe_call(self, messages: list, system_prompt: str = None, model: str = None, use_small_model: bool = False, temperature: float = 0.3, **kwargs):
        if not self.keys:
            raise ValueError("No LLM API keys found in .env")

        # If system_prompt is explicitly provided, insert it at the beginning of the messages list
        if system_prompt and not any(m.get("role") == "system" for m in messages):
            messages = [{"role": "system", "content": system_prompt}] + messages

        attempts = 0
        total_keys = len(self.keys)
        
        while attempts < total_keys:
            current = self.keys[self.current_index]
            provider = current["provider"]
            key = current["key"]
            index_val = current["index"]
            
            try:
                print(f"[LLMManager] Using {provider} key index: {index_val}")
                
                if provider == "groq":
                    client = Groq(api_key=key)
                    actual_model = "llama-3.1-8b-instant" if use_small_model else "llama-3.3-70b-versatile"
                    completion = client.chat.completions.create(
                        model=actual_model,
                        messages=messages,
                        temperature=temperature,
                        **kwargs
                    )
                elif provider == "cerebras":
                    client = Cerebras(api_key=key)
                    actual_model = "llama3.1-8b" if use_small_model else "qwen-3-235b-a22b-instruct-2507"
                    completion = client.chat.completions.create(
                        model=actual_model,
                        messages=messages,
                        temperature=temperature,
                        **kwargs
                    )
                return completion.choices[0].message.content
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit or 429 errors
                if "429" in error_str or "rate limit" in error_str:
                    print(f"[LLMManager] Rate limit on {provider} key {index_val}, rotating...")
                    self.rotate()
                    attempts += 1
                else:
                    # Reraise immediately if it's not a rate limit issue
                    raise e
                    
        raise Exception("All LLM API keys exhausted due to rate limits.")

# Global instance to be imported and used by agents
# Keeping name as groq_manager to avoid touching all agent files
groq_manager = LLMKeyManager()
