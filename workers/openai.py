import openai
from workers.base import BaseWorker
from core.config import settings
from core.logger import logger

class OpenAIWorker(BaseWorker):
    def __init__(self, model_name: str = "gpt-4"):
        self.model_name = model_name
        # Using async client
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 256),
                temperature=kwargs.get("temperature", 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAIWorker error for model {self.model_name}: {e}")
            raise
