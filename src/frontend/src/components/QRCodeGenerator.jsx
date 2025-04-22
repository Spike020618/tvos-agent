import React, { useRef, useState, useEffect } from 'react';
import QRCode from 'react-qr-code';
import * as htmlToImage from 'html-to-image';
import '../styles/QRCodeGenerator.css';
import axios from 'axios'; // 或者使用 fetch

const QRCodeGenerator = ({ qrIsVisible = true }) => {
  const qrCodeRef = useRef(null);
  const [currentUrl, setCurrentUrl] = useState('http://localhost:8000/agent/uploader_page');
  const [isLoading, setIsLoading] = useState(false);

  // 获取后端 IP 的函数
  const fetchServerIp = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/agent/server_ip'); // 替换为你的后端API
      const ip = response.data.ip;
      setCurrentUrl(`http://${ip}:8000/agent/uploader_page`);
    } catch (error) {
      console.error('Error fetching server IP:', error);
      // 保持默认值不变
    } finally {
      setIsLoading(false);
    }
  };

  // 组件加载时获取一次IP
  useEffect(() => {
    fetchServerIp();
  }, []);

  return (
    <div className="qrcode__container">
      {isLoading ? (
        <div>Loading IP address...</div>
      ) : (
        qrIsVisible && (
          <div className="qrcode__download">
            <div className="qrcode__image" ref={qrCodeRef}>
              <QRCode 
                value={currentUrl}
                size={300}
                bgColor="#ffffff"
                fgColor="#000000"
                level="H"
              />
            </div>
            <button onClick={fetchServerIp} className="refresh-button">
              Refresh
            </button>
            <div>Current URL: {currentUrl.replace('http://', '')}</div>
          </div>
        )
      )}
    </div>
  );
};

export default QRCodeGenerator;