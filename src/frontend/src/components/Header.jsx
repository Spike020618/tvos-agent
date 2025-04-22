import { Link } from 'react-router-dom'
import VoiceSearch from './VoiceAssistant';
import VoiceAssistant from './VoiceAssistant';

export default function Header() {
  return (
    <header className="header">
      <nav>
        <Link to="/" className="logo">视频网站</Link>
        <div className="search">
          <input type="text" placeholder="搜索视频..." />
          <VoiceAssistant/>
        </div>
      </nav>
    </header>
  )
}