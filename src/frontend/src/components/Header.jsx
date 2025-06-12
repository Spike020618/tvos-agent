import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Header.css';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const searchUrl = `http://localhost:8000/agent/media_search?message=${encodeURIComponent(searchQuery)}`;
      const response = await fetch(searchUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🟢 搜索引擎解析成功:', data);
      // 检查返回的状态是否为 error
      if (data.status === "error") {
        alert(data.chat); // 使用后端返回的 chat 消息
      }
    } catch (error) {
      console.error('🔴 搜索引擎解析失败:', error);
      alert('搜索失败，请稍后重试');
    }
  };

  return (
    <header className="header">
      <nav>
        <Link to="/" className="logo">Media Agent</Link>
        <div className="search">
          <input 
            type="text" 
            placeholder="搜索视频..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>搜索</button>
        </div>
      </nav>
    </header>
  );
}