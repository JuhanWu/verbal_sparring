// src/frontend/src/pages/HomePage.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'
import Button from '../components/Button'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function HomePage() {
  const { isAuthenticated, username, token, userId, error, login, register, clearError } = useAuthContext()
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [inputUsername, setInputUsername] = useState('')
  const [inputPassword, setInputPassword] = useState('')
  const [opponent, setOpponent] = useState('npc')
  const [opponentTab, setOpponentTab] = useState<'npc' | 'human'>('npc')
  const [matchError, setMatchError] = useState('')
  const navigate = useNavigate()

  async function handleAuth() {
    clearError()
    const success = tab === 'login'
      ? await login(inputUsername, inputPassword)
      : await register(inputUsername, inputPassword)
    if (success) { setInputUsername(''); setInputPassword('') }
  }

  async function handleStartMatch() {
    setMatchError('')
    const resp = await fetch(`${API}/api/matches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ opponent }),
    })
    const data = await resp.json()
    if (resp.ok) {
      navigate(`/battle/${data.match_id}`, { state: { token, myUsername: username, userId } })
    } else {
      setMatchError(data.detail ?? '建立對局失敗')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-ink">
        <div className="w-full max-w-xs px-6 py-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="font-display text-[42px] text-white tracking-[5px] leading-tight">唇槍</div>
            <div className="font-display text-[42px] text-vermillion tracking-[5px] leading-tight" style={{ textShadow: '0 0 20px rgba(204,51,0,0.5)' }}>舌戰</div>
            <div className="font-mono text-bark text-[7px] tracking-[6px] mt-1">VERBAL SPARRING</div>
          </div>
          {/* Auth tabs */}
          <div className="flex border border-bamboo mb-3">
            <button onClick={() => setTab('login')} className={`flex-1 py-2 font-display text-[10px] tracking-[3px] ${tab === 'login' ? 'bg-vermillion text-white' : 'text-bark'}`}>登入</button>
            <button onClick={() => setTab('register')} className={`flex-1 py-2 font-mono text-[10px] tracking-[3px] ${tab === 'register' ? 'bg-vermillion text-white' : 'text-bark'}`}>註冊</button>
          </div>
          {/* Inputs */}
          <input
            placeholder="用戶名"
            value={inputUsername}
            onChange={e => setInputUsername(e.target.value)}
            className="w-full bg-[#080805] border border-bamboo px-3 py-2 text-aged font-mono text-[10px] mb-2 focus:outline-none focus:border-vermillion"
          />
          <input
            type="password"
            placeholder="密碼"
            value={inputPassword}
            onChange={e => setInputPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAuth()}
            className="w-full bg-[#080805] border border-bamboo px-3 py-2 text-aged font-mono text-[10px] mb-3 focus:outline-none focus:border-vermillion"
          />
          {error && (
            <div className="border-l-[3px] border-vermillion bg-[#1a0005] px-3 py-2 text-[#cc6633] font-mono text-[9px] mb-3">{error}</div>
          )}
          <Button variant="primary-outline" onClick={handleAuth} className="w-full">進入戰場</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-ink p-6">
      {/* Welcome */}
      <div className="mb-6 text-center">
        <div className="font-mono text-bark text-[8px] tracking-[3px] mb-1">武士歸來</div>
        <div className="font-display text-[24px] text-white tracking-[2px]">
          {username.toUpperCase()}<span className="text-vermillion text-[14px] ml-2 tracking-wider">入場</span>
        </div>
      </div>
      {/* Match card */}
      <div className="w-full max-w-sm border border-bamboo bg-parchment p-5">
        <div className="font-mono text-bark text-[8px] tracking-[3px] mb-3">選擇對手</div>
        <div className="flex border border-bamboo mb-3">
          <button onClick={() => { setOpponentTab('npc'); setOpponent('npc') }}
            className={`flex-1 py-2 font-display text-[10px] tracking-[2px] ${opponentTab === 'npc' ? 'bg-vermillion text-white' : 'text-bark'}`}>
            AI NPC
          </button>
          <button onClick={() => setOpponentTab('human')}
            className={`flex-1 py-2 font-mono text-[10px] tracking-[2px] ${opponentTab === 'human' ? 'bg-vermillion text-white' : 'text-bark'}`}>
            人類對手
          </button>
        </div>
        {opponentTab === 'human' && (
          <input
            placeholder="輸入對手用戶名"
            value={opponent === 'npc' ? '' : opponent}
            onChange={e => setOpponent(e.target.value || 'npc')}
            className="w-full bg-ink border border-bamboo px-3 py-2 text-aged font-mono text-[10px] mb-3 focus:outline-none focus:border-vermillion"
          />
        )}
        {matchError && (
          <div className="border-l-[3px] border-vermillion bg-[#1a0005] px-3 py-2 text-[#cc6633] font-mono text-[9px] mb-3">{matchError}</div>
        )}
        <Button variant="primary-solid" onClick={handleStartMatch} className="w-full">開戰！</Button>
      </div>
    </div>
  )
}
