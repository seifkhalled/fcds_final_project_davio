from groq import Groq
from ai.config import AIConfig
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=AIConfig.GROQ_API_KEY)
        self.model = AIConfig.LLM_MODEL
        self.temperature = AIConfig.LLM_TEMPERATURE
        self.max_tokens = AIConfig.LLM_MAX_TOKENS

    def chat(self, system_prompt, user_prompt, max_tokens=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        usage = response.usage
        print(f"\n{'='*50}")
        print(f"LLM Token Usage ({self.model})")
        print(f"  Input tokens:  {usage.prompt_tokens}")
        print(f"  Output tokens: {usage.completion_tokens}")
        print(f"  Total tokens:  {usage.total_tokens}")
        print(f"{'='*50}\n")

        return LLMResponse(
            content=response.choices[0].message.content,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )
