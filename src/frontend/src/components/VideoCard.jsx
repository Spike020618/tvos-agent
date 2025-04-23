import { useState } from 'react';
import '../styles/VideoCard.css';

export default function VideoCard({ video }) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <>
      <div className="video-card">
        <div className="thumbnail-container">
          <img 
            src={video.thumbnail}
            className="thumbnail"
            alt={video.title}
          />
          <span className="duration">{video.duration}</span>
          {/* 修改播放按钮点击事件 */}
          <button 
            className="play-button"
            onClick={(e) => {
              e.preventDefault(); // 阻止默认行为
              e.stopPropagation(); // 仍然阻止冒泡
              setIsFullscreen(true); // 直接在这里触发全屏
            }}
          >
            ▶
          </button>
        </div>
        <div className="info">
          <h3>{video.title}</h3>
          <div className="meta">
            <span>{video.views}次观看</span>
          </div>
        </div>
      </div>

      {/* 全屏播放层（保持不变） */}
      {isFullscreen && (
        <div className="fullscreen-overlay">
          <button 
            className="close-button"
            onClick={() => setIsFullscreen(false)}
          >
            ×
          </button>
          <video src={video.videoUrl} scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></video>
        </div>
      )}
    </>
  );
}