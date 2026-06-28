'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage, getTelegramWebApp } from '@/lib/telegram'
import { api, type Transaction, type UserProfile } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'

const PACKAGES = [
  { id: 'start',    tokens: 20,   stars: 50,   emoji: '🌱' },
  { id: 'basic',    tokens: 100,  stars: 200,  emoji: '⚡️' },
  { id: 'pro',      tokens: 500,  stars: 800,  emoji: '🚀' },
  { id: 'business', tokens: 1000, stars: 1400, emoji: '💼' },
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
  const [debugMsg, setDebugMsg] = useState<string>('')

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const uid = getTelegramUserId()
    if (!uid) return

    api.getUser(uid).then(setUser).catch(() => null)
    api.getTokenHistory(uid).then(setHistory).catch(() => null)
  }, [])

  const t = getTranslations(locale)
  const packageNames = PACKAGE_NAMES[locale] ?? PACKAGE_NAMES.ru

  const handleBuy = async (pkg: typeof PACKAGES[number]) => {
    const uid = getTelegramUserId()
    const twa = getTelegramWebApp()
    setDebugMsg(`uid=${uid} twa=${!!twa} pkg=${pkg.id}`)

    if (!uid) {
      setDebugMsg('❌ Нет telegram_id — откройте через Telegram')
      return
    }
    if (!twa) {
      setDebugMsg('❌ Нет Telegram WebApp — откройте через Telegram')
      return
    }

    setBuying(pkg.id)
    setDebugMsg(`⏳ Создаём инвойс для ${pkg.id}...`)
    try {
      const res = await fetch('/api/tokens/create_invoice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: uid, package_id: pkg.id }),
      })
      if (!res.ok) {
        const text = await res.text()
        setDebugMsg(`❌ Backend ${res.status}: ${text}`)
        return
      }
      const data = await res.json()
      setDebugMsg('✅ Инвойс получен, открываем оплату...')
      twa.openInvoice(data.invoice_url, (status: string) => {
        setDebugMsg(`💳 Статус: ${status}`)
        if (status === 'paid') {
          api.getUser(uid).then(setUser).catch(() => null)
          api.getTokenHistory(uid).then(setHistory).catch(() => null)
        }
      })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err)
      setDebugMsg(`❌ Ошибка fetch: ${msg}`)
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

      <div className="rounded-2xl p-4 flex items-center gap-3" style={{ backgroundColor: 'var(--tg-secondary-bg)' }}>
        <span className="text-4xl">💎</span>
        <div>
          <p className="text-2xl font-bold">{user?.tokens ?? '—'}</p>
          <p className="text-sm" style={{ color: 'var(--tg-hint)' }}>{t.current_balance}</p>
        </div>
      </div>

      {debugMsg && (
        <div style={{ background: '#1a1a2e', color: '#eee', borderRadius: 12, padding: '10px 14px', fontSize: 13, fontFamily: 'monospace', wordBreak: 'break-all' }}>
          {debugMsg}
        </div>
      )}

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
