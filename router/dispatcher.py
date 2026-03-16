from workers.openai import OpenAIWorker
from workers.huggingface import HuggingFaceLocalWorker
from core.logger import logger

class ModelRouter:
    def __init__(self):
        # Instantiate workers mapping
        self.workers = {
            "gpt4": OpenAIWorker(model_name="gpt-4"),
            "gpt-3.5-turbo": OpenAIWorker(model_name="gpt-3.5-turbo"),
            "llama3": HuggingFaceLocalWorker(model_name="llama3"),
        }

    def get_supported_models(self) -> list[str]:
        return list(self.workers.keys())

    async def dispatch(self, model: str, prompt: str) -> str:
        worker = self.workers.get(model)
        if not worker:
            raise ValueError(f"Model '{model}' is not supported. Supported models: {self.get_supported_models()}")
        
        logger.info(f"Dispatching request to {model}")
        return await worker.generate(prompt)

router = ModelRouter()
