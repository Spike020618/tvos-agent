import React, { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import '../styles/VoiceAssistant.css';

const VoiceAssistant = ({ onUpdateMedias }) => {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [mediaData, setMediaData] = useState([]);
  
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  // 自动触发搜索
  useEffect(() => {
    if (!listening && transcript.trim()) {
      handleAutoSearch();
    }
  }, [listening]);

  const handleAutoSearch = async () => {
    const userMessage = {
      type: 'user',
      content: transcript,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setConversation(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      // API调用 - 按照您的要求配置headers和body
      const searchUrl = `http://localhost:8000/agent/voice_media_search?message=${encodeURIComponent(transcript)}`;
      const response = await fetch(searchUrl, {
        method: 'GET',
        mode: 'cors',  // 明确启用CORS模式
        headers: {
          'Content-Type': 'application/json', // 明确声明期望JSON响应
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔴 HTTP错误:', {
          status: response.status,
          statusText: response.statusText,
          headers: [...response.headers.entries()], // 显示响应头
          body: errorText
        });
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      let data;
      try {
        data = await response.json();
        console.log('🟢 语音助手解析成功:', data); // 调试3：打印解析后的数据
      } catch (jsonError) {
        const textBody = await response.text();
        console.error('🔴 语音助手解析失败:', {
          error: jsonError,
          rawText: textBody,
          headers: [...response.headers.entries()]
        });
        throw new Error(`响应不是有效的JSON: ${textBody.substring(0, 100)}...`);
      }

      const botMessage = {
        content: data.chat,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setConversation(prev => [...prev, botMessage]);
      speak(botMessage.content);

      if (data.medias_info) {
        setMediaData(data.medias_info);
      }
    } catch (error) {
      console.error('❌ 完整错误链:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      
      setConversation(prev => [...prev, {
        type: 'error',
        content: `请求失败: ${error.message.replace('Failed to fetch', '网络连接失败')}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsLoading(false);
      resetTranscript();
    }
  };

  // 新增：将视频数据推送到父组件
  const handleAddToMedias = (mediaData) => {
      console.log(mediaData)
      onUpdateMedias(mediaData);
      mediaData = []
  };

  const speak = (text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 1.2; // 适当语速
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      console.error('语音合成错误:', e);
      setIsSpeaking(false);
    };
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (listening) {
      SpeechRecognition.stopListening();
    } else {
      resetTranscript();
      SpeechRecognition.startListening({ 
        language: 'zh-CN',
        continuous: false // 自动结束
      });
    }
  };

  if (!browserSupportsSpeechRecognition) {
    return (
      <button className="voice-btn" disabled>
        🎤 浏览器不支持语音识别
      </button>
    );
  }

  return (
    <>
      {/* 触发按钮 - 保留原有位置和样式 */}
      <button 
        className={`voice-btn ${isPanelOpen ? 'active' : ''}`}
        onClick={() => setIsPanelOpen(!isPanelOpen)}
      >
        {isPanelOpen ? '✕ 关闭' : '🎤 语音助手'}
      </button>

      {/* 右侧悬浮面板 - 完整保留原有设计 */}
      {isPanelOpen && (
        <div className="voice-panel-overlay" onClick={() => setIsPanelOpen(false)}>
          <div className="voice-panel" onClick={(e) => e.stopPropagation()}>
            <div className="panel-header">
              <h3>语音对话助手</h3>
              <button 
                className="close-btn"
                onClick={() => setIsPanelOpen(false)}
              >
                ✕
              </button>
            </div>
            
            {/* 对话历史区域 */}
            <div className="conversation-history">
              {conversation.map((msg, i) => (
                <div key={i} className={`message-bubble ${msg.type}`}>
                  <div className="message-content">
                    {msg.content}
                    {msg.type === 'bot' && (
                      <button 
                        onClick={() => speak(msg.content)} 
                        className="speak-btn"
                        disabled={isSpeaking}
                      >
                        {isSpeaking ? '🛑 停止' : '🔊 朗读'}
                      </button>
                    )}
                  </div>
                  <div className="message-time">{msg.timestamp}</div>
                </div>
              ))}
              
              {isLoading && (
                <div className="message-bubble bot">
                  <div className="message-content">正在处理您的请求...</div>
                </div>
              )}
            </div>

            {/*mediaData.length > 0 && (
              <button 
                onClick={() => handleAddToMedias(mediaData)}
                className="add-video-btn"
              >
                ➕ 添加到推荐视频
              </button>
            )*/}
            
            {/* 语音控制区域 */}
            <div className="voice-controls">
              <button
                onClick={toggleListening}
                className={`mic-button ${listening ? 'active' : ''}`}
                disabled={isLoading}
              >
                {listening ? (
                  <>
                    <span className="pulse-animation"></span>
                    🎤 聆听中...
                  </>
                ) : '🎤 开始说话'}
              </button>
              <div className="status-text">
                {transcript || (listening ? "请说出您的需求..." : "点击麦克风开始对话")}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default VoiceAssistant;