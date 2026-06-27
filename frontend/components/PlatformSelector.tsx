'use client'

import { useRouter } from 'next/navigation'
import type { Locale } from '@/lib/i18n'
import { getTranslations } from '@/lib/i18n'

const PLATFORMS = [
  { id: 'rozetka', emoji: '🛒', color: '#00A046' },
  { id: 'prom', emoji: '🏪', color: '#FF6B00' },
  { id: 'wildberries', emoji: '🍇', color: '#CB11AB' },
  { id: 'etsy', emoji: '🎨', color: '#F1641E' },
  { id: 'universal', emoji: '🌐', color: '#2481cc' },
] as const

interface Props {
  locale: Locale
}

export default function PlatformSelector({ locale }: Props) {
  const router = useRouter()
  const t = getTranslations(locale)

  return (
    <div className="grid grid-cols-2 gap-3">
      {PLATFORMS.map((p) => (
        <button
          key={p.id}
          className="platform-card tg-secondary"
          onClick={() => router.push(`/generate?platform=${p.id}`)}
        >
          <span className="text-4xl">{p.emoji}</span>
          <span className="font-semibold text-sm">{t.platforms[p.id]}</span>
        </button>
      ))}
    </div>
  )
}
