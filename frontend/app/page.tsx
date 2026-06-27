'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUser, getTelegramLanguage } from '@/lib/telegram'
import { api, type UserProfile } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'
import PlatformSelector from '@/components/PlatformSelector'
import TokenBalance from '@/components/TokenBalance'

export default function HomePage() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [locale, setLocale] = useState<Locale>('ru')

  useEffect(() => {
    const tgUser = getTelegramUser()
    const savedLocale = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(savedLocale)

    if (!tgUser) return

    api.registerUser({
      telegram_id: tgUser.id,
      username: tgUser.username,
      full_name: `${tgUser.first_name} ${tgUser.last_name ?? ''}`.trim(),
      language: savedLocale,
    }).then((u) => {
      setUser(u)
      setLocale(u.language as Locale)
    }).catch(() => null)
  }, [])

  const t = getTranslations(locale)

  return (
    <main className="min-h-screen p-4 pb-8 space-y-6">
      <div className="flex items-center justify-between pt-2">
        <div>
          <h1 className="text-2xl font-bold">{t.title}</h1>
          <p className="text-sm tg-hint">{t.tagline}</p>
        </div>
        <Link href="/profile" className="text-3xl">👤</Link>
      </div>

      {user && <TokenBalance tokens={user.tokens} locale={locale} />}

      <div>
        <h2 className="text-sm font-semibold tg-hint uppercase tracking-wide mb-3">{t.platform_select}</h2>
        <PlatformSelector locale={locale} />
      </div>

      <nav className="flex justify-around pt-2">
        {[
          { href: '/history', emoji: '📦' },
          { href: '/tokens', emoji: '⚡️' },
          { href: '/referral', emoji: '🤝' },
        ].map((item) => (
          <Link key={item.href} href={item.href} className="text-2xl p-3 tg-secondary rounded-xl">
            {item.emoji}
          </Link>
        ))}
      </nav>
    </main>
  )
}
