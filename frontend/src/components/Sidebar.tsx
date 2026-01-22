import { useEffect, useState } from "react";
import type { ChatHistory, SidebarProps } from "../types/sidebar";
import axios from "axios";

export default function SideBar({ handleClick, thread }: SidebarProps){
    const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
    const apiUrl = import.meta.env.VITE_API_URL;

    useEffect(() => {
        const fetchChat = async () => {
            let result = await axios.get(`${apiUrl}/chat/history`)
            setChatHistory(result.data.history)
        }

        fetchChat();
    }, [thread])

    const applyHighlight = (thread_id: string) => thread_id === thread? 'bg-white/20 font-semibold': ''
    const renderChatHistory = chatHistory.map(chat => <button className={`text-left cursor-pointer px-4 hover:bg-white/10 duration-200 rounded-lg py-2 truncate ${applyHighlight(chat.thread_id)}`} onClick={e => handleClick(chat.thread_id)}>{chat.title}</button>)

    return (
        <div className="bg-white/10 p-2 border border-white/20 shadow-lg w-64 h-[95vh] m-4 rounded-xl flex flex-col justify-between">
            <div>
                <img src="logo.png" className="w-3/5 mx-auto my-4" />
                <div className="flex flex-col text-white">
                    {renderChatHistory}
                </div>
            </div>
            <button onClick={e => handleClick(null)} className="bg-white/10 text-white/80 cursor-pointer hover:bg-white/20 duration-200 text-sm rounded-lg py-2 flex items-center justify-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                </svg>
                New Chat
            </button>
        </div>
    )
}