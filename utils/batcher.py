import asyncio
from typing import Callable, Any
from core.logger import logger

class AsyncBatcher:
    """
    Batches individual requests into a single list and processes them together.
    """
    def __init__(self, process_batch_fn: Callable, max_batch_size: int = 5, timeout_ms: float = 100):
        self.process_batch_fn = process_batch_fn
        self.max_batch_size = max_batch_size
        self.timeout = timeout_ms / 1000.0
        self.queue = asyncio.Queue()
        self.task = None

    def start(self):
        if self.task is None:
            self.task = asyncio.create_task(self._batch_loop())
            logger.info("Batcher background task started.")

    async def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None

    async def process(self, item: Any) -> Any:
        future = asyncio.Future()
        await self.queue.put((item, future))
        return await future

    async def _batch_loop(self):
        while True:
            batch = []
            try:
                # Wait for at least one item
                item, future = await self.queue.get()
                batch.append((item, future))
                
                # Fetch up to max_batch_size - 1 more items without blocking
                while len(batch) < self.max_batch_size:
                    try:
                        next_item = await asyncio.wait_for(self.queue.get(), timeout=self.timeout)
                        batch.append(next_item)
                    except asyncio.TimeoutError:
                        break
                    except asyncio.QueueEmpty:
                        break

                if batch:
                    # Extract items
                    items = [b[0] for b in batch]
                    futures = [b[1] for b in batch]
                    
                    try:
                        # Process batch
                        results = await self.process_batch_fn(items)
                        
                        # Return results to futures
                        for i, res in enumerate(results):
                            if not futures[i].done():
                                futures[i].set_result(res)
                    except Exception as e:
                        logger.error(f"Batch processing error: {e}")
                        for f in futures:
                            if not f.done():
                                f.set_exception(e)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batcher loop error: {e}")
