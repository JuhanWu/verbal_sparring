import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import GameOverModal from './GameOverModal'

const wrap = (ui: React.ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>)

test('shows win message when player wins', () => {
  wrap(<GameOverModal winner="alice" myUsername="alice" matchId="m1" onPlayAgain={vi.fn()} />)
  expect(screen.getByText('你贏了！')).toBeInTheDocument()
})

test('shows loss message when player loses', () => {
  wrap(<GameOverModal winner="bob" myUsername="alice" matchId="m1" onPlayAgain={vi.fn()} />)
  expect(screen.getByText('你輸了...')).toBeInTheDocument()
})

test('calls onPlayAgain on button click', () => {
  const onPlayAgain = vi.fn()
  wrap(<GameOverModal winner="alice" myUsername="alice" matchId="m1" onPlayAgain={onPlayAgain} />)
  fireEvent.click(screen.getByText(/再戰一局/))
  expect(onPlayAgain).toHaveBeenCalledTimes(1)
})
