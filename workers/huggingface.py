from workers.base import BaseWorker
from core.logger import logger
from utils.batcher import AsyncBatcher
import asyncio

class HuggingFaceLocalWorker(BaseWorker):
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        
        # Initialize batcher to process multiple prompts at once
        self.batcher = AsyncBatcher(
            process_batch_fn=self._process_batch,
            max_batch_size=5,
            timeout_ms=500  # wait up to 500ms to form a batch
        )
        # Background task for batching started when the first request comes or at startup
        self.batcher.start()
        
        logger.info(f"Initialized Dummy Local HuggingFace worker for {model_name} with Batching enabled")

    async def _process_batch(self, prompts: list[str]) -> list[str]:
        logger.info(f"HuggingFaceLocalWorker batch processing {len(prompts)} prompts...")
        await asyncio.sleep(1.5)  # Simulate batch inference delay
        
        # Return a result for each prompt
        return [f"[Simulated Local {self.model_name} Response] You requested: '{p}'" for p in prompts]

    async def generate(self, prompt: str, **kwargs) -> str:
        # Enqueue the prompt into the batcher and wait for the result
        return await self.batcher.process(prompt)
