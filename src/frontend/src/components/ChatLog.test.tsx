// src/frontend/src/components/ChatLog.test.tsx
import { render, screen } from '@testing-library/react'
import ChatLog from './ChatLog'
import type { ChatEntry } from '../types/game'

test('renders attack entry with sender and text', () => {
  const entries: ChatEntry[] = [
    { id: 1, kind: 'attack', sender: 'alice', displayText: '你好遜！', damage: 20, isNpc: false },
  ]
  render(<ChatLog entries={entries} />)
  expect(screen.getByText('alice')).toBeInTheDocument()
  expect(screen.getByText('你好遜！')).toBeInTheDocument()
})

test('renders system entry', () => {
  const entries: ChatEntry[] = [
    { id: 1, kind: 'system', displayText: '遊戲開始' },
  ]
  render(<ChatLog entries={entries} />)
  expect(screen.getByText('遊戲開始')).toBeInTheDocument()
})

test('renders referee entry via RefereeStamp', () => {
  const entries: ChatEntry[] = [
    { id: 1, kind: 'referee', displayText: '匕首入心' },
  ]
  render(<ChatLog entries={entries} />)
  expect(screen.getByText('匕首入心')).toBeInTheDocument()
})
