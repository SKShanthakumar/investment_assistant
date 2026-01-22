import { useEffect, useRef, useState, type FormEvent } from "react";
import ChatInput from "./ChatInput";
import type { ChatMessage, ChatProps } from "../types/chat";
import ChatList from "./ChatList";
import axios from "axios";

export default function Chat({ thread, setThread }: ChatProps) {
  const [inputMessage, setInputMessage] = useState<string>("");
  const [approvalRequired, setApprovalRequired] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [research, setResearch] = useState<boolean>(false);
  const [chat, setChat] = useState<ChatMessage[]>([]);

  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchChat = async () => {
      let result = await axios.get(`${apiUrl}/chat/list/${thread}`)
      setChat(result.data.chat)
    }

    if (thread == null){
      setChat([]);  // null thread implies new chat
      return;
    }
    
    fetchChat();
  }, [thread])

  // for auto scroll
  const bottomRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  // Singleton event source for stream
  const eventSourceRef = useRef<EventSource | null>(null);

  const closeConnection = (es: EventSource): void => {
    es.close();
    eventSourceRef.current = null;
    setLoading(false);
    setResearch(false);
  }
  
  const handleSend = (e: FormEvent): void => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    setLoading(true);

    // 1. Add user message
    setChat((prev) => [
      ...prev,
      { role: "user", message: inputMessage },
      { role: "ai", message: "" }, // placeholder for streaming
    ]);

    // 2. Close any existing stream
    eventSourceRef.current?.close();

    // 3. Open new SSE stream
    const es = new EventSource(
      `${apiUrl}/chat?${thread != null? `thread_id=${thread}`:''}&prompt=${encodeURIComponent(inputMessage)}`
    );

    // 4. Receive streamed tokens
    es.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        setChat((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            ...next[next.length - 1],
            message: next[next.length - 1].message + data.content,
          };
          return next;
        });
      }

      else if (data.type === "stream_end") {
        setThread(data.thread_id)
        closeConnection(es);
        return;
      }

      else if (data.type === "approval_required"){
        setApprovalRequired(true);
        setThread(data.thread_id);

        closeConnection(es);
        return;
      }
    };

    es.onerror = () => {
      console.log('error');
      closeConnection(es);
    };

    setInputMessage("");
  };

  const handleApproval = (action: boolean): void => {
    setApprovalRequired(false);
    if (!action){
      setChat((prev) => [
        ...prev,
        { role: "user", message: 'Reject' },
      ]);
      return
    }

    setLoading(true);
    setResearch(true);
    
    // 1. Add user message
    setChat((prev) => [
      ...prev,
      { role: "user", message: 'Approve' },
      { role: "ai", message: "" }, // placeholder for streaming
    ]);

    // 2. Close any existing stream
    eventSourceRef.current?.close();

    // 3. Open new SSE stream
    const es = new EventSource(
      `${apiUrl}/chat/approve?thread_id=${thread}&action=1`
    );

    // 4. Receive streamed tokens
    es.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        setChat((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            ...next[next.length - 1],
            message: next[next.length - 1].message + data.content,
          };
          return next;
        });
      }

      else if (data.type === "done" && data.node != 'final_report') {
        setChat((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            ...next[next.length - 1],
            message: next[next.length - 1].message + '\n\n---\n\n',
          };
          return next;
        });
      }

      else if (data.type === "stream_end") {
        closeConnection(es);
        return;
      }
    };

    es.onerror = () => {
      console.log('error');
      closeConnection(es);
    };
  }

  const updateInput = (value: string) => setInputMessage(value);


  return (
    <div className="h-screen flex-1 flex flex-col p-5">
      <div className={`flex-1 min-h-0 overflow-y-auto ${chat.length == 0? 'flex items-center justify-center': ''}`}>
        <ChatList
          chat={chat}
          approval_required={approvalRequired}
          handle_approval={handleApproval}
          loading={loading}
          research={research}
          />
        <div ref={bottomRef} />
      </div>

      <ChatInput
        onSubmit={handleSend}
        inputHandler={updateInput}
        inputMessage={inputMessage}
      />
    </div>
  );
}
