import type { ChatListProps } from "../types/chat";
import ReactMarkdown from 'react-markdown';
import remarkGfm from "remark-gfm";

export default function ChatList({ chat, approval_required, handle_approval, loading, research }: ChatListProps){
    if (chat.length == 0){
        return (
            <div className="text-center text-white">
                <p className="text-3xl mb-4">Hi, I’m StoxAI</p>
                <p className="text-sm">I help you research stocks before you invest.</p>
                <p className="text-sm">Ask me about any company and I’ll break it down with deep analysis and SWOT insights.</p>
                <p className="italic mt-4">Try asking: “Should I invest in NVIDIA?”</p>
            </div>
        )
    }
    return(
        <div className="space-y-6 text-white">
            {chat.map((msg, idx) => {
                if (msg.role === 'user')
                    return <div key={idx} className="bg-white/10 border border-white/20 shadow-lg w-2/3 ml-auto rounded-xl py-2 px-4">{msg.message}</div>
                return <ReactMarkdown key={idx} remarkPlugins={[remarkGfm]}>{msg.message}</ReactMarkdown>
            })}
            { approval_required? (
                <div>
                    <button onClick={(e) => handle_approval(true)} className="bg-white w-20 rounded-lg py-2 text-black text-sm cursor-pointer shadow-xl hover:bg-white/80 duration-200 me-2">
                        Approve
                    </button>
                    <button onClick={(e) => handle_approval(false)} className="bg-white/20 w-20 rounded-lg py-2 border border-white/40 text-sm cursor-pointer shadow-xl hover:bg-white/40 duration-200">
                        Reject
                    </button>
                </div>
            ): null }
            { loading? (
                <div className="flex items-center gap-1">
                    <span className="animate-pulse">{ research? 'Conducting deep research, please hold on...' : 'Thinking'}...</span>
                </div>
            ): null}
        </div>
    )
}