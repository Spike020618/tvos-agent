import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Header from './components/Header'

function App() {
  return (
    <div className="app">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </main>
    </div>
  )
}

export default App