import { useState } from 'react';
import '../styles/MediaCard.css';

export default function MediaCard({ media }) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <>
      <div className="video-card">
        <div className="thumbnail-container">
          <img 
            src={media.img}
            className="thumbnail"
            alt={media.name}
          />
          <span className="duration">{media.duration}</span>
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
          <h3>{media.name}</h3>
          <div className="meta">
            <span>{media.views}次观看</span>
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
          <video src={media.url} scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></video>
        </div>
      )}
    </>
  );
}