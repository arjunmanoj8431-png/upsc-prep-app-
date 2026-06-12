```react
import React, { useState, useEffect, useRef } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, doc, setDoc, updateDoc, addDoc, onSnapshot } from 'firebase/firestore';
import { MessageSquare, MoreVertical, Search, Send, User, ArrowLeft, Plus } from 'lucide-react';

// --- FIREBASE INITIALIZATION ---
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-chat-app';

export default function App() {
  const [user, setUser] = useState(null);
  const [customUserId, setCustomUserId] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  
  const [newMessage, setNewMessage] = useState('');
  const [newContactId, setNewContactId] = useState('');
  const [showNewChatInput, setShowNewChatInput] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [isMobileChatOpen, setIsMobileChatOpen] = useState(false);
  
  const messagesEndRef = useRef(null);

  // --- AUTHENTICATION ---
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Auth error:", err);
      }
    };
    initAuth();

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      // Try to recover session from localStorage (only for the custom user ID string)
      const savedUserId = localStorage.getItem('chatAppUserId');
      if (savedUserId && currentUser) {
        setCustomUserId(savedUserId);
        setIsLoggedIn(true);
      }
    });
    return () => unsubscribe();
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    const cleanId = customUserId.trim().toLowerCase();
    if (cleanId && user) {
      setCustomUserId(cleanId);
      setIsLoggedIn(true);
      localStorage.setItem('chatAppUserId', cleanId);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCustomUserId('');
    setActiveChat(null);
    localStorage.removeItem('chatAppUserId');
  };

  // --- DATA FETCHING (CHATS) ---
  useEffect(() => {
    if (!user || !isLoggedIn || !customUserId) return;

    const chatsRef = collection(db, 'artifacts', appId, 'public', 'data', 'chats');
    const unsubscribe = onSnapshot(chatsRef, (snapshot) => {
      const allChats = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
      // Filter in memory: Only keep chats where current user is a participant
      const myChats = allChats.filter(c => c.participants && c.participants.includes(customUserId));
      // Sort by last updated
      myChats.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
      setChats(myChats);
    }, (error) => {
      console.error("Error fetching chats:", error);
    });

    return () => unsubscribe();
  }, [user, isLoggedIn, customUserId]);

  // --- DATA FETCHING (MESSAGES) ---
  useEffect(() => {
    if (!user || !isLoggedIn || !activeChat) return;

    // Use a dynamic collection name for each chat to strictly follow structural rules and avoid complex queries
    const messagesCollectionName = `chat_msgs_${activeChat.id}`;
    const messagesRef = collection(db, 'artifacts', appId, 'public', 'data', messagesCollectionName);
    
    const unsubscribe = onSnapshot(messagesRef, (snapshot) => {
      const msgs = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
      // Sort by timestamp in memory
      msgs.sort((a, b) => a.timestamp - b.timestamp);
      setMessages(msgs);
      scrollToBottom();
    }, (error) => {
      console.error("Error fetching messages:", error);
    });

    return () => unsubscribe();
  }, [user, isLoggedIn, activeChat]);

  // --- SCROLL MANAGEMENT ---
  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // --- ACTIONS ---
  const handleStartChat = async (e) => {
    e.preventDefault();
    const targetId = newContactId.trim().toLowerCase();
    
    if (!targetId || targetId === customUserId) {
        setShowNewChatInput(false);
        setNewContactId('');
        return;
    }

    // Create a deterministic unique chat ID based on the two users
    const sortedIds = [customUserId, targetId].sort();
    const newChatId = `${sortedIds[0]}_${sortedIds[1]}`;

    // Check if we already have it locally
    const existingChat = chats.find(c => c.id === newChatId);
    if (existingChat) {
      setActiveChat(existingChat);
      setIsMobileChatOpen(true);
    } else {
      // Create new chat document
      const chatDocRef = doc(db, 'artifacts', appId, 'public', 'data', 'chats', newChatId);
      const chatData = {
        participants: [customUserId, targetId],
        updatedAt: Date.now(),
        lastMessage: "Chat created"
      };
      try {
        await setDoc(chatDocRef, chatData);
        setActiveChat({ id: newChatId, ...chatData });
        setIsMobileChatOpen(true);
      } catch (err) {
        console.error("Error creating chat:", err);
      }
    }
    
    setNewContactId('');
    setShowNewChatInput(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChat) return;

    const textToSend = newMessage.trim();
    setNewMessage(''); // optimistic clear

    const messagesCollectionName = `chat_msgs_${activeChat.id}`;
    const messagesRef = collection(db, 'artifacts', appId, 'public', 'data', messagesCollectionName);
    const chatDocRef = doc(db, 'artifacts', appId, 'public', 'data', 'chats', activeChat.id);

    try {
      await addDoc(messagesRef, {
        senderId: customUserId,
        text: textToSend,
        timestamp: Date.now()
      });

      await updateDoc(chatDocRef, {
        lastMessage: textToSend,
        updatedAt: Date.now()
      });
    } catch (err) {
      console.error("Error sending message:", err);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getOtherParticipant = (chat) => {
    return chat.participants.find(p => p !== customUserId) || 'Unknown';
  };

  // --- RENDER HELPERS ---
  const filteredChats = chats.filter(chat => 
    getOtherParticipant(chat).toLowerCase().includes(searchQuery.toLowerCase())
  );

  // --- LOGIN SCREEN ---
  if (!isLoggedIn) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#111B21] text-white p-4">
        <div className="bg-[#202C33] p-8 rounded-xl shadow-lg max-w-md w-full">
          <div className="flex justify-center mb-6 text-emerald-500">
            <MessageSquare size={48} />
          </div>
          <h1 className="text-2xl font-bold text-center mb-2">Welcome to WebApp Chat</h1>
          <p className="text-[#8696A0] text-center mb-8">Enter a unique User ID to connect with friends. No phone number required.</p>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <input
                type="text"
                placeholder="e.g. alice_wonderland"
                value={customUserId}
                onChange={(e) => setCustomUserId(e.target.value)}
                className="w-full bg-[#2A3942] text-[#D1D7DB] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                required
                autoFocus
              />
            </div>
            <button 
              type="submit"
              disabled={!user || !customUserId.trim()}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
            >
              Start Chatting
            </button>
          </form>
        </div>
      </div>
    );
  }

  // --- MAIN APP RENDER ---
  return (
    <div className="flex h-screen bg-[#111B21] text-[#E9EDEF] overflow-hidden">
      
      {/* SIDEBAR (Hidden on mobile if chat is open) */}
      <div className={`w-full md:w-[400px] flex-shrink-0 border-r border-[#222D34] flex flex-col ${isMobileChatOpen ? 'hidden md:flex' : 'flex'}`}>
        
        {/* Sidebar Header */}
        <div className="bg-[#202C33] p-3 flex justify-between items-center h-16">
          <div className="flex items-center space-x-3 cursor-pointer group" onClick={handleLogout} title="Click to logout">
            <div className="bg-[#6B7C85] p-2 rounded-full text-white group-hover:bg-red-500 transition">
              <User size={24} />
            </div>
            <span className="font-semibold">{customUserId}</span>
          </div>
          <div className="flex space-x-4 text-[#AEBAC1]">
            <button onClick={() => setShowNewChatInput(!showNewChatInput)} className="hover:text-white transition p-1">
              <Plus size={22} />
            </button>
            <button className="hover:text-white transition p-1">
              <MoreVertical size={22} />
            </button>
          </div>
        </div>

        {/* Search Bar / New Chat Input */}
        <div className="p-2 bg-[#111B21]">
          {showNewChatInput ? (
            <form onSubmit={handleStartChat} className="flex bg-[#202C33] rounded-lg p-1 items-center px-2 shadow-sm">
              <button type="button" onClick={() => setShowNewChatInput(false)} className="text-[#AEBAC1] hover:text-white mr-2">
                <ArrowLeft size={20} />
              </button>
              <input
                type="text"
                placeholder="Enter User ID to chat..."
                value={newContactId}
                onChange={(e) => setNewContactId(e.target.value)}
                className="w-full bg-transparent text-sm p-1.5 focus:outline-none text-[#D1D7DB]"
                autoFocus
              />
              <button type="submit" className="text-emerald-500 hover:text-emerald-400 p-1 font-semibold text-sm ml-2">
                Start
              </button>
            </form>
          ) : (
            <div className="flex bg-[#202C33] rounded-lg p-1 items-center px-2">
              <Search size={18} className="text-[#AEBAC1] ml-2" />
              <input
                type="text"
                placeholder="Search chats"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-sm p-2 focus:outline-none text-[#D1D7DB]"
              />
            </div>
          )}
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {filteredChats.length === 0 ? (
            <div className="text-center text-[#8696A0] mt-10 p-4 text-sm">
              {searchQuery ? "No chats found." : "No chats yet. Click the + icon to start chatting with someone via their User ID."}
            </div>
          ) : (
            filteredChats.map((chat) => (
              <div 
                key={chat.id}
                onClick={() => {
                  setActiveChat(chat);
                  setIsMobileChatOpen(true);
                }}
                className={`flex items-center px-3 py-3 cursor-pointer hover:bg-[#202C33] transition ${activeChat?.id === chat.id ? 'bg-[#2A3942]' : ''}`}
              >
                <div className="bg-[#6B7C85] p-3 rounded-full mr-3 text-white flex-shrink-0">
                  <User size={20} />
                </div>
                <div className="flex-1 min-w-0 border-b border-[#222D34] pb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-semibold text-white truncate">
                      {getOtherParticipant(chat)}
                    </span>
                    <span className="text-xs text-[#8696A0] whitespace-nowrap ml-2">
                      {formatTime(chat.updatedAt)}
                    </span>
                  </div>
                  <div className="text-sm text-[#8696A0] truncate">
                    {chat.lastMessage || "Started a chat"}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* MAIN CHAT AREA (Hidden on mobile if list is open) */}
      <div className={`flex-1 flex flex-col bg-[#0B141A] relative ${!isMobileChatOpen ? 'hidden md:flex' : 'flex'}`}>
        
        {activeChat ? (
          <>
            {/* Chat Header */}
            <div className="bg-[#202C33] px-4 py-2 flex items-center h-16 shadow-sm z-10">
              <button 
                onClick={() => setIsMobileChatOpen(false)}
                className="md:hidden text-[#AEBAC1] hover:text-white mr-3 p-1"
              >
                <ArrowLeft size={24} />
              </button>
              <div className="bg-[#6B7C85] p-2 rounded-full text-white mr-3">
                <User size={20} />
              </div>
              <div className="flex-1">
                <h2 className="font-semibold text-white">{getOtherParticipant(activeChat)}</h2>
              </div>
              <div className="flex space-x-4 text-[#AEBAC1]">
                <Search size={20} className="cursor-pointer hover:text-white transition" />
                <MoreVertical size={20} className="cursor-pointer hover:text-white transition" />
              </div>
            </div>

            {/* Messages Area - Notice the WhatsApp-like background pattern color */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar relative bg-[#0B141A]">
               {/* Decorative background element, optional */}
               <div className="absolute inset-0 opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#AEBAC1 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
              
              {/* Encryption Notice */}
              <div className="flex justify-center mb-4">
                <div className="bg-[#182229] text-[#FFD279] text-xs py-1.5 px-3 rounded-lg text-center max-w-sm shadow-sm relative z-10">
                  Messages are end-to-end simulated. Nobody outside of this chat, not even the app, can read or listen to them.
                </div>
              </div>

              {messages.map((msg, idx) => {
                const isMine = msg.senderId === customUserId;
                return (
                  <div key={msg.id || idx} className={`flex ${isMine ? 'justify-end' : 'justify-start'} relative z-10`}>
                    <div 
                      className={`max-w-[75%] rounded-lg px-3 py-1.5 shadow text-sm relative group
                        ${isMine ? 'bg-[#005C4B] text-[#E9EDEF]' : 'bg-[#202C33] text-[#E9EDEF]'}`}
                      style={{ borderTopRightRadius: isMine ? '0px' : '', borderTopLeftRadius: !isMine ? '0px' : '' }}
                    >
                      <div className="pb-3 break-words pr-8">
                        {msg.text}
                      </div>
                      <div className={`text-[10px] absolute bottom-1 right-2 ${isMine ? 'text-[#8696A0]' : 'text-[#8696A0]'}`}>
                        {formatTime(msg.timestamp)}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} className="h-1" />
            </div>

            {/* Message Input Area */}
            <div className="bg-[#202C33] px-4 py-3 flex items-center z-10">
              <form onSubmit={handleSendMessage} className="flex-1 flex items-center bg-[#2A3942] rounded-lg overflow-hidden pr-2">
                <input
                  type="text"
                  placeholder="Type a message"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="flex-1 bg-transparent text-white px-4 py-2.5 focus:outline-none"
                />
                <button 
                  type="submit" 
                  disabled={!newMessage.trim()}
                  className={`p-2 rounded-full transition-colors ${newMessage.trim() ? 'text-emerald-500 hover:bg-[#202C33]' : 'text-[#8696A0]'}`}
                >
                  <Send size={20} />
                </button>
              </form>
            </div>
          </>
        ) : (
          /* Empty State for Desktop */
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
             <div className="w-64 h-64 mb-8 text-[#202C33] opacity-20">
                <MessageSquare className="w-full h-full" />
             </div>
             <h1 className="text-3xl font-light text-white mb-4">WebApp Chat</h1>
             <p className="text-[#8696A0] max-w-md">
                Send and receive messages without keeping your phone online.
                Use the + icon on the left to start a chat using a friend's User ID.
             </p>
          </div>
        )}
      </div>

      {/* Global Styles for Scrollbar */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar:hover::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.2);
        }
      `}} />
    </div>
  );
}

```
