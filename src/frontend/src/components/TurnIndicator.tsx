// src/frontend/src/components/TurnIndicator.tsx
type Props = { isMyTurn: boolean }

export default function TurnIndicator({ isMyTurn }: Props) {
  return (
    <div className={`py-[5px] px-4 text-center font-mono text-[9px] tracking-[3px] border-t border-b flex-shrink-0 ${
      isMyTurn
        ? 'bg-parchment border-[#4a4028] text-vermillion'
        : 'bg-ink border-bamboo text-bark'
    }`}>
      {isMyTurn ? '⚔ 輪到你出招！⚔' : '等待對手...'}
    </div>
  )
}
