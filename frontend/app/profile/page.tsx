'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUser, getTelegramLanguage } from '@/lib/telegram'
import { api, type UserProfile } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'
import LanguageSwitcher from '@/components/LanguageSwitcher'

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [locale, setLocale] = useState<Locale>('ru')

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const tgUser = getTelegramUser()
    if (!tgUser) return
    api.getUser(tgUser.id).then((u) => {
      setUser(u)
      setLocale(u.language as Locale)
    }).catch(() => null)
  }, [])

  const t = getTranslations(locale)

  const handleLocaleChange = (newLocale: Locale) => {
    setLocale(newLocale)
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-5">
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <h1 className="font-bold text-lg">{t.profile_title}</h1>
      </div>

      {user && (
        <div className="space-y-4">
          <div className="tg-secondary rounded-2xl p-5 text-center space-y-2">
            <div className="text-6xl">👤</div>
            <h2 className="font-bold text-xl">{user.full_name ?? user.username ?? 'User'}</h2>
            {user.username && <p className="tg-hint text-sm">@{user.username}</p>}
          </div>

          <div className="tg-secondary rounded-2xl p-4 grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-500">💎 {user.tokens}</p>
              <p className="text-xs tg-hint mt-1">{t.tokens_left}</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{user.total_cards}</p>
              <p className="text-xs tg-hint mt-1">{t.cards_created}</p>
            </div>
          </div>

          <div className="tg-secondary rounded-2xl p-4 space-y-3">
            <div>
              <p className="text-xs tg-hint mb-2">{t.language_label}</p>
              <LanguageSwitcher current={locale} onChange={handleLocaleChange} />
            </div>
            <div className="pt-2 border-t border-[var(--tg-bg)]">
              <p className="text-xs tg-hint">{t.registered}</p>
              <p className="text-sm mt-0.5">{new Date(user.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          <Link href="/tokens" className="block w-full tg-btn py-3.5 rounded-xl font-medium text-center">
            ⚡️ {t.buy_tokens}
          </Link>
        </div>
      )}
    </main>
  )
}
