import { useState } from "react";
import Chat from "./components/Chat";
import SideBar from "./components/Sidebar";

function App() {
  const [thread, setThread] = useState<string | null>(null);
  const updateThread = (thread_id: string | null) => setThread(thread_id)

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#050816]">
      {/* Main color wash */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0B3C5D]/40 via-[#1E1B4B]/40 to-[#3B0764]/40"></div>
      {/* Blue glow top-left */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,rgba(56,189,248,0.35),transparent_45%)]"></div>

      {/* Content */}
      <div className="relative z-10 flex">
        <SideBar thread={thread} handleClick={updateThread} />
        <Chat thread={thread} setThread={updateThread} />
      </div>
    </div>
  );
}

export default App;
