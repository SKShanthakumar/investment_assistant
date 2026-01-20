export interface SidebarProps {
  thread: string | null
  handleClick: (thread_id: string | null) => void
}

export interface ChatHistory {
  thread_id: string
  title: string
}