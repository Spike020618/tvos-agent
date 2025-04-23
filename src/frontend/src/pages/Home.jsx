import { useEffect, useState } from 'react'
import axios from 'axios'
import VideoCard from '../components/VideoCard'
import QRCodeGenerator from '../components/QRCodeGenerator'

export default function Home() {
  const [videos, setVideos] = useState([])

  useEffect(() => {
    // 这里使用模拟数据，实际项目中应该调用API
    const mockVideos = [
      {
        id: 1,
        title: '“一演丁真 便入戏 得太深”——丁真能量单曲《群丁》',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'http://localhost:8000/agent/media/1',
        views: '1250.8万',
        duration: '04:09'
      },
      {
        id: 2,
        title: '【Playlist】温暖的旋律让你忘却疲惫|居家歌单|放松|慵懒|节奏',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'http://localhost:8000/agent/media/2',
        views: '7.5万',
        duration: '43:38'
      },
      {
        id: 3,
        title: '【Playlist】温暖的旋律让你忘却疲惫|居家歌单|放松|慵懒|节奏',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'https://player.bilibili.com/player.html?aid=699690540&bvid=BV1Zm4y1e7eR&cid=1159067867&p=1&as_wide=1&high_quality=1&danmaku=0&t=30',
        views: '7.5万',
        duration: '43:38'
      },
      {
        id: 4,
        title: '“一演丁真 便入戏 得太深”——丁真能量单曲《群丁》',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'https://www.bilibili.com/video/BV1Y7SWYpERP/',
        views: '1250.8万',
        duration: '04:09'
      },
      {
        id: 5,
        title: '【Playlist】温暖的旋律让你忘却疲惫|居家歌单|放松|慵懒|节奏',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'https://www.bilibili.com/video/BV1Dy1aYwEWg',
        views: '7.5万',
        duration: '43:38'
      },
      {
        id: 6,
        title: '【Playlist】温暖的旋律让你忘却疲惫|居家歌单|放松|慵懒|节奏',
        thumbnail: 'https://tse1-mm.cn.bing.net/th/id/OIP-C.dC6CLNcwmIg1I2fEbinJyQHaE5',
        videoUrl: 'https://www.bilibili.com/video/BV1Dy1aYwEWg',
        views: '7.5万',
        duration: '43:38'
      },
      // 可以添加更多视频...
    ]
    setVideos(mockVideos)
    
    // 实际API调用示例：
    // axios.get('/api/videos').then(res => setVideos(res.data))
  }, [])

  return (
    <div className="home-page">
      <h2 className="section-title">推荐视频</h2>
      <div><QRCodeGenerator></QRCodeGenerator></div>
      <div className="video-grid">
        {videos.map(video => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </div>
  )
}