// src/frontend/src/components/RefereeStamp.tsx
import { motion } from 'framer-motion'

type Props = { comment: string }

function Seal({ char }: { char: string }) {
  return (
    <div className="w-[18px] h-[18px] border border-vermillion/40 flex items-center justify-center flex-shrink-0">
      <span className="text-vermillion/70 text-[8px] font-body">{char}</span>
    </div>
  )
}

export default function RefereeStamp({ comment }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex items-center justify-center gap-2 my-1 py-1 border-t border-b border-vermillion/20"
    >
      <Seal char="判" />
      <span className="text-bark text-[9px] tracking-[2px] font-mono italic">{comment}</span>
      <Seal char="決" />
    </motion.div>
  )
}
