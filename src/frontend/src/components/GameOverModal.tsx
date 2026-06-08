// src/frontend/src/components/GameOverModal.tsx
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from './Button'

type Props = {
  winner: string
  myUsername: string
  matchId: string
  onPlayAgain: () => void
}

export default function GameOverModal({ winner, myUsername, matchId, onPlayAgain }: Props) {
  const didWin = winner === myUsername

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-ink/90 flex items-center justify-center z-40"
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-[#0f0e0b] border-2 border-bamboo p-8 text-center max-w-sm w-full mx-4"
      >
        <div className={`font-display text-4xl tracking-widest mb-2 ${didWin ? 'text-white' : 'text-aged'}`}>
          {didWin ? '你贏了！' : '你輸了...'}
        </div>
        <div className="font-mono text-bark text-[9px] tracking-[3px] mb-8">
          {didWin ? '此役功成，武林震驚' : '一敗塗地，來日再戰'}
        </div>
        <div className="flex flex-col gap-3">
          <Link to={`/replay/${matchId}`}>
            <Button variant="primary-outline" className="w-full">查看回放 ▶</Button>
          </Link>
          <Button variant="primary-solid" onClick={onPlayAgain} className="w-full">再戰一局</Button>
          <Link to="/">
            <Button variant="secondary" className="w-full">回首頁</Button>
          </Link>
        </div>
      </motion.div>
    </motion.div>
  )
}
