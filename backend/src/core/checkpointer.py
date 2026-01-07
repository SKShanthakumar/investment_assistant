from langgraph.checkpoint.memory import MemorySaver
from investment_assistant.core.settings import settings

postgres_checkpointer = AsyncPostgresSaver.from_conn_string(
    settings.DB_URI
)
# postgres_checkpointer = MemorySaver()