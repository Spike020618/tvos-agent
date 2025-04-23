import React, { useRef, useState, useEffect } from 'react';
import QRCode from 'react-qr-code';
import * as htmlToImage from 'html-to-image';
import '../styles/QRCodeGenerator.css';
import axios from 'axios';

const QRCodeGenerator = () => {
  const qrCodeRef = useRef(null);
  const [currentUrl, setCurrentUrl] = useState('http://localhost:8000/agent/uploader_page');
  const [isLoading, setIsLoading] = useState(false);
  const [showQR, setShowQR] = useState(false);

  const fetchServerIp = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/agent/server_ip');
      const ip = response.data.ip;
      setCurrentUrl(`http://${ip}:8000/agent/uploader_page`);
    } catch (error) {
      console.error('Error fetching server IP:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchServerIp();
  }, []);

  return (
    <>
      {/* 固定在右上角的小开关 */}
      <button 
        className="qr-toggle-button"
        onClick={() => setShowQR(!showQR)}
      >
        {showQR ? '×' : 'QR'}
      </button>

      {showQR && (
        <div className="qr-modal-overlay">
          <div className="qr-modal-content">
            <button 
              className="close-modal-button"
              onClick={() => setShowQR(false)}
            >
              ×
            </button>
            
            {isLoading ? (
              <div>Loading IP address...</div>
            ) : (
              <>
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
                <div className="current-url">Current URL: {currentUrl.replace('http://', '')}</div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default QRCodeGenerator;