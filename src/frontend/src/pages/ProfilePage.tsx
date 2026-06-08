// src/frontend/src/pages/ProfilePage.tsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'
import type { LeaderboardEntry, MatchRecord } from '../types/game'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function rankTitle(wins: number) {
  if (wins >= 50) return '武林盟主'
  if (wins >= 20) return '武林高手'
  if (wins >= 10) return '初出茅廬'
  return '江湖新人'
}

export default function ProfilePage() {
  const { username } = useAuthContext()
  const [stats, setStats] = useState<LeaderboardEntry | null>(null)
  const [history, setHistory] = useState<MatchRecord[]>([])

  useEffect(() => {
    fetch(`${API}/api/leaderboard`)
      .then(r => r.json())
      .then((d: { entries: LeaderboardEntry[] }) => {
        const mine = d.entries.find(e => e.username === username)
        if (mine) setStats(mine)
      })
  }, [username])

  useEffect(() => {
    try {
      const stored: MatchRecord[] = JSON.parse(localStorage.getItem('matchHistory') ?? '[]')
      setHistory(stored.slice(0, 5))
    } catch {
      setHistory([])
    }
  }, [])

  return (
    <div className="flex-1 bg-ink px-4 py-6 max-w-md mx-auto w-full">
      {/* Avatar + name */}
      <div className="flex flex-col items-center mb-6">
        <div className="w-[60px] h-[60px] rounded-full border-2 border-vermillion flex items-center justify-center mb-3"
             style={{ background: '#0f0e0b' }}>
          <span className="font-display text-[22px] text-vermillion">{username.charAt(0).toUpperCase()}</span>
        </div>
        <div className="font-display text-[20px] text-white tracking-[3px]">{username.toUpperCase()}</div>
        <div className="font-mono text-bark text-[8px] tracking-[3px] mt-1">{rankTitle(stats?.wins ?? 0)}</div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-2 mb-6">
        {[
          { label: '勝場', value: stats?.wins ?? 0, color: 'text-white' },
          { label: '敗場', value: stats?.losses ?? 0, color: 'text-[#664433]' },
          { label: '累積傷害', value: (stats?.total_damage ?? 0).toLocaleString(), color: 'text-vermillion' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-parchment border border-[#4a4028] p-3 text-center">
            <div className={`font-display text-[22px] ${color}`}>{value}</div>
            <div className="font-mono text-aged text-[7px] tracking-[2px]">{label}</div>
          </div>
        ))}
      </div>

      {/* Recent matches */}
      <div className="mb-4">
        <div className="font-mono text-bark text-[8px] tracking-[2px] mb-3">最近五場</div>
        {history.length === 0 ? (
          <div className="text-bark font-mono text-[9px] text-center py-4">尚無對戰紀錄</div>
        ) : (
          history.map((r) => (
            <div
              key={r.matchId}
              className="flex items-center gap-2 px-3 py-2 mb-[3px]"
              style={{ borderLeft: `2px solid ${r.result === 'win' ? '#cc3300' : '#443322'}` }}
            >
              <span className={`font-mono text-[8px] tracking-[2px] ${r.result === 'win' ? 'text-vermillion' : 'text-bark'}`}>
                {r.result === 'win' ? '勝' : '敗'}
              </span>
              <span className="font-display text-[11px] text-aged flex-1">vs {r.opponent.toUpperCase()}</span>
              <span className="font-mono text-bark text-[8px]">+{r.totalDamage}</span>
              <Link to={`/replay/${r.matchId}`} className="font-mono text-bark text-[8px] tracking-[2px] hover:text-aged">回放▶</Link>
            </div>
          ))
        )}
      </div>

      <div className="text-center mt-4">
        <Link to="/" className="font-mono text-bark text-[9px] tracking-[2px] hover:text-aged">← 回首頁</Link>
      </div>
    </div>
  )
}
