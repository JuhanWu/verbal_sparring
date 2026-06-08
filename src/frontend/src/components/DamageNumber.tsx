// src/frontend/src/components/DamageNumber.tsx
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'

type Props = { damageEvent: { damage: number; id: number } | null }

export default function DamageNumber({ damageEvent }: Props) {
  return createPortal(
    <AnimatePresence>
      {damageEvent && (
        <motion.div
          key={damageEvent.id}
          initial={{ opacity: 1, y: 0, x: '-50%', scale: 1.2 }}
          animate={{ opacity: 0, y: -70, scale: 0.8 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="fixed left-1/2 top-1/3 font-display text-[56px] text-fire pointer-events-none z-50"
          style={{ textShadow: '0 0 20px rgba(255,80,0,0.6), 0 0 40px rgba(200,50,0,0.3)' }}
        >
          -{damageEvent.damage}
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  )
}
