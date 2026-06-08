// src/frontend/src/components/AttackInput.tsx
import { useState, useRef } from 'react'
import type { AttackPayload } from '../types/game'

type Props = { onSend: (p: AttackPayload) => void; disabled: boolean }

export default function AttackInput({ onSend, disabled }: Props) {
  const [text, setText] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  function handleSend() {
    if (!text.trim() || disabled) return
    onSend({ text })
    setText('')
  }

  function handleImage(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => onSend({ text, image: reader.result as string })
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  return (
    <div className="bg-[#0f0e0b] border-t-2 border-bamboo px-4 py-3 flex gap-2 items-center flex-shrink-0">
      <span className="text-bark text-[13px] font-body italic flex-shrink-0">筆▶</span>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="執筆出招，揮毫傷人..."
        disabled={disabled}
        className="flex-1 bg-[#080805] border border-bamboo border-b-2 border-b-vermillion px-3 py-2 text-[#d4c5aa] font-body italic text-[11px] placeholder:text-bark placeholder:not-italic focus:outline-none disabled:opacity-40"
      />
      <button
        onClick={() => fileRef.current?.click()}
        disabled={disabled}
        className="border border-bamboo text-bark px-2 py-2 text-[13px] hover:text-aged disabled:opacity-40"
      >
        📷
      </button>
      <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleImage} />
      <button
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        className="bg-ink border-2 border-vermillion text-vermillion font-display text-[11px] tracking-[3px] px-4 py-2 shadow-[0_0_12px_rgba(204,51,0,0.25)] hover:shadow-[0_0_20px_rgba(204,51,0,0.4)] disabled:opacity-40 disabled:cursor-not-allowed"
      >
        出手
      </button>
    </div>
  )
}
