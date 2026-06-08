// src/frontend/src/pages/HomePage.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'
import HomePage from './HomePage'

global.fetch = vi.fn()

const wrap = (ui: React.ReactElement) =>
  render(<AuthProvider><MemoryRouter>{ui}</MemoryRouter></AuthProvider>)

beforeEach(() => {
  localStorage.clear()
  vi.clearAllMocks()
})

test('renders login and register tabs when not authenticated', () => {
  wrap(<HomePage />)
  expect(screen.getByText('登入')).toBeInTheDocument()
  expect(screen.getByText('註冊')).toBeInTheDocument()
})

test('shows error on login failure', async () => {
  (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok: false, json: async () => ({ detail: 'Invalid credentials' }),
  })
  wrap(<HomePage />)
  fireEvent.change(screen.getByPlaceholderText('用戶名'), { target: { value: 'alice' } })
  fireEvent.change(screen.getByPlaceholderText('密碼'), { target: { value: 'wrong' } })
  fireEvent.click(screen.getByRole('button', { name: /進入戰場/ }))
  await waitFor(() => expect(screen.getByText(/登入失敗/)).toBeInTheDocument())
})
