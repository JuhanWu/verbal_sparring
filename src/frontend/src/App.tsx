// src/frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import BattlePage from './pages/BattlePage'
import LeaderboardPage from './pages/LeaderboardPage'
import ReplayPage from './pages/ReplayPage'
import ProfilePage from './pages/ProfilePage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/battle/:matchId" element={<BattlePage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/replay/:matchId" element={<ReplayPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
