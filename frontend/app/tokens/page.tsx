'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage } from '@/lib/telegram'
import { api, type TokenPackage, type Transaction, type UserProfile } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'

const PACKAGE_EMOJIS: Record<string, string> = {
  start: '🌱', basic: '⚡️', pro: '🚀', business: '💼',
}

export default function TokensPage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [packages, setPackages] = useState<TokenPackage[]>([])
  const [history, setHistory] = useState<Transaction[]>([])
  const [locale, setLocale] = useState<Locale>('ru')
  const [buying, setBuying] = useState<string | null>(null)

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const uid = getTelegramUserId()

    Promise.all([
      uid ? api.getUser(uid) : Promise.resolve(null),
      api.getPackages(),
      uid ? api.getTokenHistory(uid) : Promise.resolve([]),
    ]).then(([u, pkgs, txs]) => {
      if (u) setUser(u)
      setPackages(pkgs)
      setHistory(txs)
    }).catch(() => null)
  }, [])

  const t = getTranslations(locale)

  const handleBuy = async (pkg: TokenPackage) => {
    const uid = getTelegramUserId()
    if (!uid) return

    setBuying(pkg.id)
    try {
      const result = await api.purchaseTokens(uid, pkg.id, 'stars')
      if (user) setUser({ ...user, tokens: (result as any).tokens_total })
    } catch {
      // handle error
    } finally {
      setBuying(null)
    }
  }

  const txTypeEmoji: Record<string, string> = {
    purchase: '💰', referral: '🤝', bonus: '🎁', spend: '⚡️',
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-5">
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <h1 className="font-bold text-lg">{t.tokens_title}</h1>
      </div>

      {user && (
        <div className="tg-secondary rounded-2xl p-4 flex items-center gap-3">
          <span className="text-4xl">💎</span>
          <div>
            <p className="text-2xl font-bold">{user.tokens}</p>
            <p className="text-sm tg-hint">{t.current_balance}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        {packages.map((pkg) => (
          <button
            key={pkg.id}
            onClick={() => handleBuy(pkg)}
            disabled={buying === pkg.id}
            className="tg-secondary rounded-2xl p-4 text-left space-y-2 active:scale-95 transition-transform disabled:opacity-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-2xl">{PACKAGE_EMOJIS[pkg.id] ?? '⚡️'}</span>
              <span className="text-xs tg-hint">{t.token_packages[pkg.id as keyof typeof t.token_packages] ?? pkg.label}</span>
            </div>
            <p className="text-xl font-bold">💎 {pkg.tokens}</p>
            <p className="text-sm tg-btn px-3 py-1 rounded-lg inline-block">
              {t.buy_btn} {pkg.stars} ⭐
            </p>
          </button>
        ))}
      </div>

      {history.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold tg-hint uppercase tracking-wide mb-3">{t.tx_history}</h2>
          <div className="space-y-2">
            {history.slice(0, 20).map((tx) => (
              <div key={tx.id} className="tg-secondary rounded-xl px-4 py-3 flex items-center gap-3">
                <span className="text-lg">{txTypeEmoji[tx.type] ?? '•'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{tx.description ?? tx.type}</p>
                  <p className="text-xs tg-hint">{new Date(tx.created_at).toLocaleDateString()}</p>
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
