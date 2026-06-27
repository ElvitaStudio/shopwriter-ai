'use client'

import type { Locale } from '@/lib/i18n'
import { api } from '@/lib/api'
import { getTelegramUserId } from '@/lib/telegram'

const LOCALES: { code: Locale; label: string }[] = [
  { code: 'ru', label: '🇷🇺 RU' },
  { code: 'ua', label: '🇺🇦 UA' },
  { code: 'en', label: '🇬🇧 EN' },
]

interface Props {
  current: Locale
  onChange: (locale: Locale) => void
}

export default function LanguageSwitcher({ current, onChange }: Props) {
  const handleChange = async (locale: Locale) => {
    const uid = getTelegramUserId()
    if (uid) {
      await api.updateLanguage(uid, locale).catch(() => null)
    }
    onChange(locale)
    if (typeof window !== 'undefined') {
      localStorage.setItem('locale', locale)
    }
  }

  return (
    <div className="flex gap-2">
      {LOCALES.map((l) => (
        <button
          key={l.code}
          onClick={() => handleChange(l.code)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            current === l.code ? 'tg-btn' : 'tg-secondary'
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  )
}
