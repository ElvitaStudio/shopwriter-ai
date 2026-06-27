'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage } from '@/lib/telegram'
import { api, type HistoryCard } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'

export default function HistoryPage() {
  const [cards, setCards] = useState<HistoryCard[]>([])
  const [locale, setLocale] = useState<Locale>('ru')
  const [expanded, setExpanded] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const uid = getTelegramUserId()
    if (!uid) { setLoading(false); return }
    api.getHistory(uid).then(setCards).catch(() => null).finally(() => setLoading(false))
  }, [])

  const t = getTranslations(locale)

  const platformEmojis: Record<string, string> = {
    rozetka: '🛒', prom: '🏪', wildberries: '🍇', etsy: '🎨', universal: '🌐',
  }

  const copyCard = async (card: HistoryCard) => {
    const text = [
      card.title,
      card.description,
      card.characteristics.map((c) => `${c.name}: ${c.value}`).join('\n'),
      card.seo_tags.join(', '),
    ].join('\n\n')
    await navigator.clipboard.writeText(text)
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-4">
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <h1 className="font-bold text-lg">{t.history_title}</h1>
      </div>

      {loading && <p className="text-center tg-hint py-8">...</p>}

      {!loading && cards.length === 0 && (
        <div className="text-center py-12 tg-hint">
          <div className="text-5xl mb-3">📭</div>
          <p>{t.history_empty}</p>
          <Link href="/" className="mt-4 inline-block tg-btn px-6 py-3 rounded-xl font-medium">
            {t.generate}
          </Link>
        </div>
      )}

      <div className="space-y-3">
        {cards.map((card) => (
          <div key={card.id} className="tg-secondary rounded-2xl overflow-hidden">
            <button
              className="w-full flex items-center gap-3 p-4 text-left"
              onClick={() => setExpanded(expanded === card.id ? null : card.id)}
            >
              <span className="text-2xl">{platformEmojis[card.platform] ?? '🌐'}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{card.title}</p>
                <p className="text-xs tg-hint">{new Date(card.created_at).toLocaleDateString()}</p>
              </div>
              <span className="tg-hint text-sm">{expanded === card.id ? '▲' : '▼'}</span>
            </button>

            {expanded === card.id && (
              <div className="px-4 pb-4 space-y-3 border-t border-[var(--tg-secondary-bg)]">
                <p className="text-sm leading-relaxed pt-3">{card.description}</p>
                {card.characteristics.length > 0 && (
                  <div className="space-y-1">
                    {card.characteristics.map((c, i) => (
                      <div key={i} className="flex gap-2 text-sm">
                        <span className="tg-hint min-w-[100px]">{c.name}:</span>
                        <span>{c.value}</span>
                      </div>
                    ))}
                  </div>
                )}
                {card.seo_tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {card.seo_tags.map((tag, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded-full tg-btn opacity-80">{tag}</span>
                    ))}
                  </div>
                )}
                <button
                  onClick={() => copyCard(card)}
                  className="w-full tg-btn py-2.5 rounded-xl text-sm font-medium"
                >
                  {t.copy_all}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </main>
  )
}
