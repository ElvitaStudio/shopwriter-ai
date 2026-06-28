'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage, getTelegramWebApp } from '@/lib/telegram'
import { api, type Transaction, type UserProfile } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'

const PACKAGES = [
  { id: 'tokens_20',   tokens: 20,   stars: 50,   emoji: '🌱' },
  { id: 'tokens_100',  tokens: 100,  stars: 200,  emoji: '⚡️' },
  { id: 'tokens_500',  tokens: 500,  stars: 800,  emoji: '🚀' },
  { id: 'tokens_1000', tokens: 1000, stars: 1400, emoji: '💼' },
]

const PACKAGE_NAMES: Record<Locale, string[]> = {
  ru: ['Старт', 'Базовый', 'Про', 'Бизнес'],
  ua: ['Старт', 'Базовий', 'Про', 'Бізнес'],
  en: ['Starter', 'Basic', 'Pro', 'Business'],
}

const TX_EMOJI: Record<string, string> = {
  purchase: '💰', referral: '🤝', bonus: '🎁', spend: '⚡️',
}

export default function TokensPage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [history, setHistory] = useState<Transaction[]>([])
  const [locale, setLocale] = useState<Locale>('ru')
  const [buying, setBuying] = useState<string | null>(null)

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const uid = getTelegramUserId()

    Promise.all([
      uid ? api.getUser(uid) : Promise.resolve(null),
      uid ? api.getTokenHistory(uid) : Promise.resolve([]),
    ]).then(([u, txs]) => {
      if (u) setUser(u)
      setHistory(txs)
    }).catch(() => null)
  }, [])

  const t = getTranslations(locale)
  const packageNames = PACKAGE_NAMES[locale] ?? PACKAGE_NAMES.ru

  const handleBuy = async (pkg: typeof PACKAGES[number]) => {
    const uid = getTelegramUserId()
    const twa = getTelegramWebApp()
    if (!uid || !twa) return

    setBuying(pkg.id)
    try {
      const { invoice_url } = await api.createInvoice(uid, pkg.id)
      twa.openInvoice(invoice_url, (status: string) => {
        if (status === 'paid') {
          // Refresh balance after payment
          api.getUser(uid).then((u) => setUser(u)).catch(() => null)
          api.getTokenHistory(uid).then(setHistory).catch(() => null)
        }
      })
    } catch {
      // silently fail — user stays on page
    } finally {
      setBuying(null)
    }
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-5" style={{ backgroundColor: 'var(--tg-bg)', color: 'var(--tg-text)' }}>
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <h1 className="font-bold text-lg">{t.tokens_title}</h1>
      </div>

      {/* Balance */}
      <div className="rounded-2xl p-4 flex items-center gap-3" style={{ backgroundColor: 'var(--tg-secondary-bg)' }}>
        <span className="text-4xl">💎</span>
        <div>
          <p className="text-2xl font-bold">{user?.tokens ?? '—'}</p>
          <p className="text-sm" style={{ color: 'var(--tg-hint)' }}>{t.current_balance}</p>
        </div>
      </div>

      {/* Packages */}
      <div className="grid grid-cols-2 gap-3">
        {PACKAGES.map((pkg, i) => (
          <button
            key={pkg.id}
            onClick={() => handleBuy(pkg)}
            disabled={buying === pkg.id}
            className="rounded-2xl p-4 text-left space-y-2 active:scale-95 transition-transform disabled:opacity-50"
            style={{ backgroundColor: 'var(--tg-secondary-bg)' }}
          >
            <div className="flex items-center justify-between">
              <span className="text-2xl">{pkg.emoji}</span>
              <span className="text-xs" style={{ color: 'var(--tg-hint)' }}>{packageNames[i]}</span>
            </div>
            <p className="text-xl font-bold">💎 {pkg.tokens}</p>
            <p
              className="text-sm px-3 py-1 rounded-lg inline-block"
              style={{ backgroundColor: 'var(--tg-btn)', color: 'var(--tg-btn-text)' }}
            >
              {pkg.stars} ⭐
            </p>
          </button>
        ))}
      </div>

      <p className="text-center text-xs" style={{ color: 'var(--tg-hint)' }}>
        Оплата через Telegram Stars — безопасно и мгновенно
      </p>

      {/* Transaction history */}
      {history.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide mb-3" style={{ color: 'var(--tg-hint)' }}>
            {t.tx_history}
          </h2>
          <div className="space-y-2">
            {history.slice(0, 20).map((tx) => (
              <div
                key={tx.id}
                className="rounded-xl px-4 py-3 flex items-center gap-3"
                style={{ backgroundColor: 'var(--tg-secondary-bg)' }}
              >
                <span className="text-lg">{TX_EMOJI[tx.type] ?? '•'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{tx.description ?? tx.type}</p>
                  <p className="text-xs" style={{ color: 'var(--tg-hint)' }}>
                    {new Date(tx.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`font-semibold text-sm ${tx.amount > 0 ? 'text-green-500' : 'text-red-400'}`}>
                  {tx.amount > 0 ? '+' : ''}{tx.amount}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  )
}
