from pydantic import BaseModel

class BaseChat(BaseModel):
    thread_id: str

class Chat(BaseChat):
    prompt: str

class Approve(BaseChat):
    action: bool