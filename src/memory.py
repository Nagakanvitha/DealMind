import os
import asyncio
import threading
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight


# Always load the .env belonging to this project
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)


class MemoryService:

    def __init__(self):
        self.api_url = os.getenv(
            "HINDSIGHT_API_URL",
            "https://api.hindsight.vectorize.io"
        ).rstrip("/")

        self.api_key = os.getenv(
            "HINDSIGHT_API_KEY",
            ""
        ).strip()

        self.bank_id = os.getenv(
            "HINDSIGHT_BANK_ID",
            "dealmind-demo"
        ).strip()

    def _run_async(self, operation):
        """
        Run one Hindsight async operation in its own event loop.
        A fresh Hindsight client is created inside that loop.
        This avoids Streamlit/event-loop conflicts.
        """

        result = {}
        error = {}

        def worker():

            async def task():

                client = Hindsight(
                    base_url=self.api_url,
                    api_key=self.api_key
                )

                try:
                    result["data"] = await operation(client)

                except Exception as e:
                    error["exception"] = e

                finally:
                    await client.aclose()

            try:
                asyncio.run(task())

            except Exception as e:
                error["exception"] = e

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        if "exception" in error:
            raise error["exception"]

        return result.get("data")

    def ensure_bank(self):
        """
        Create the DealMind memory bank if it does not already exist.
        """

        try:

            def operation(client):
                return client.aretain(
                    bank_id=self.bank_id,
                    content=(
                        "DealMind memory bank initialized for sales "
                        "intelligence involving customer conversations, "
                        "objections, stakeholders, competitors, "
                        "commitments and preferences."
                    ),
                    context="DealMind initialization",
                    tags=["dealmind", "sales-memory"]
                )

            return self._run_async(operation)

        except Exception:
            return None

    def retain(self, content, context=""):

        def operation(client):
            return client.aretain(
                bank_id=self.bank_id,
                content=content,
                context=context,
                tags=["dealmind", "sales-memory"]
            )

        return self._run_async(operation)

    def recall(self, query, limit=6):

        def operation(client):
            return client.arecall(
                bank_id=self.bank_id,
                query=query,
                budget="mid",
                max_tokens=4096
            )

        response = self._run_async(operation)

        memories = []

        for item in getattr(response, "results", [])[:limit]:

            memories.append({
                "text": getattr(item, "text", ""),
                "type": getattr(item, "type", "unknown"),
                "context": getattr(item, "context", "")
            })

        return memories