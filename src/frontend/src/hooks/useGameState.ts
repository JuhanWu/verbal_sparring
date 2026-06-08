// src/frontend/src/hooks/useGameState.ts
import { useState, useCallback } from 'react'
import type { ChatEntry, HPMap, ServerMessage } from '../types/game'

export function useGameState(myPlayerId: string) {
  const [hp, setHp] = useState<HPMap>({})
  const [currentTurn, setCurrentTurn] = useState('')
  const [chatLog, setChatLog] = useState<ChatEntry[]>([])
  const [gameOver, setGameOver] = useState<string | null>(null)
  const [lastDamageEvent, setLastDamageEvent] = useState<{ damage: number; id: number } | null>(null)

  const handleMessage = useCallback((msg: ServerMessage) => {
    if (msg.type === 'system') {
      setHp(msg.hp_status)
      setCurrentTurn(msg.current_turn)
      setChatLog(prev => [...prev, { id: Date.now(), kind: 'system', displayText: msg.message }])
    } else if (msg.type === 'attack') {
      setHp(msg.hp_status)
      setCurrentTurn(msg.current_turn)
      setLastDamageEvent({ damage: msg.damage, id: Date.now() })
      setChatLog(prev => [...prev,
        { id: Date.now(), kind: 'attack', sender: msg.sender, displayText: msg.display_text, damage: msg.damage, isNpc: false },
        { id: Date.now() + 1, kind: 'referee', displayText: msg.referee_comment },
      ])
    } else if (msg.type === 'npc_attack') {
      setHp(msg.hp_status)
      setLastDamageEvent({ damage: msg.damage, id: Date.now() })
      setChatLog(prev => [...prev,
        { id: Date.now(), kind: 'attack', sender: 'NPC', displayText: msg.display_text, damage: msg.damage, isNpc: true },
        { id: Date.now() + 1, kind: 'referee', displayText: msg.referee_comment },
      ])
    } else if (msg.type === 'game_over') {
      setGameOver(msg.winner)
      setChatLog(prev => [...prev, { id: Date.now(), kind: 'system', displayText: msg.message }])
    }
  }, [myPlayerId])

  return {
    hp, currentTurn,
    isMyTurn: currentTurn === myPlayerId,
    chatLog, gameOver, lastDamageEvent,
    handleMessage,
  }
}
