import { useEffect, useState } from 'react'
import axios from 'axios'
import MediaCard from '../components/MediaCard'
import QRCodeGenerator from '../components/QRCodeGenerator'
import VoiceAssistant from '../components/VoiceAssistant';

export default function Home() {
  const [medias, setMedias] = useState([])

  // 新增：接收语音助手的数据并更新 videos
  const handleUpdateMedias = (newMediaData) => {
    setMedias(prev => [...prev, newMediaData]);
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
        videoUrl: 'http://localhost:8000/agent/media/2',
        views: '7.5万',
        duration: '43:38'
      },
    ]
    setMedias(mockMedias)
    
    // 实际API调用示例：
    // axios.get('/api/videos').then(res => setVideos(res.data))
  }, [])

  return (
    <div className="home-page">
      <div><VoiceAssistant onUpdateVideos={handleUpdateMedias}/></div>
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