import type { FormEvent } from "react";

export type Role = "user" | "ai";

export interface ChatMessage {
    role: Role
    message: string
}

export interface ChatProps {
  thread: string | null
  setThread: (thread_id: string) => void
}

export interface ChatInputProps {
  onSubmit: (e: FormEvent) => void;
  inputHandler: (value: string) => void
  inputMessage: string
}

export interface ChatListProps {
  chat: ChatMessage[]
  approval_required: boolean
  handle_approval: (action: boolean) => void
  loading: boolean
  research: boolean
}
