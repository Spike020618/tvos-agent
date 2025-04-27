import { useEffect, useState } from 'react'
import axios from 'axios'
import MediaCard from '../components/MediaCard'
import QRCodeGenerator from '../components/QRCodeGenerator'
import VoiceAssistant from '../components/VoiceAssistant';

export default function Home() {
  const [medias, setMedias] = useState([])

  // 暂时弃用：接收语音助手的数据并更新 videos
  const handleUpdateMedias = (newMediaData) => {
    if (newMediaData && newMediaData.length > 0) {
      setMedias(newMediaData);
    } else {
      console.log("没有可添加的媒体数据");
    }
  };

  useEffect(() => {
    // 这里使用模拟数据，实际项目中应该调用API
    const mockMedias = [
      {
        id: 1,
        name: '“一演丁真 便入戏 得太深”——丁真能量单曲《群丁》',
        img: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        url: 'http://localhost:8000/agent/media/1',
        views: '1250.8万',
        duration: '04:09'
      },
      {
        id: 2,
        name: '【Playlist】温暖的旋律让你忘却疲惫|居家歌单|放松|慵懒|节奏',
        img: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        url: 'http://localhost:8000/agent/media/2',
        views: '7.5万',
        duration: '43:38'
      },
    ]
    setMedias(mockMedias)
    
    // 监听redis的sse channel发布的影视查询信息
    const eventSource = new EventSource('http://localhost:8000/agent/see');
    eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log('收到服务器更新:', data);
        setMedias(data);
    };

    eventSource.onerror = (err) => {
      console.error('SSE连接出错:', err);
      eventSource.close();
    };

    // 组件卸载时关闭连接
    return () => {
      eventSource.close();
    };
  }, [])

  return (
    <div className="home-page">
      <div><VoiceAssistant onUpdateMedias={handleUpdateMedias}/></div>
      <div><QRCodeGenerator/></div>
      <h2 className="section-title">推荐视频</h2>
      <div className="video-grid">
        {medias.map(media => (
          <MediaCard key={media.id} media={media} />
        ))}
      </div>
    </div>
  )
}