'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage, getTelegramWebApp, hapticSuccess } from '@/lib/telegram'
import { api, type ReferralInfo } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'

export default function ReferralPage() {
  const [info, setInfo] = useState<ReferralInfo | null>(null)
  const [locale, setLocale] = useState<Locale>('ru')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
    const uid = getTelegramUserId()
    if (!uid) return
    api.getReferral(uid).then(setInfo).catch(() => null)
  }, [])

  const t = getTranslations(locale)

  const copyLink = async () => {
    if (!info) return
    await navigator.clipboard.writeText(info.referral_link)
    hapticSuccess()
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const share = () => {
    if (!info) return
    const twa = getTelegramWebApp()
    if (twa) {
      twa.openTelegramLink(
        `https://t.me/share/url?url=${encodeURIComponent(info.referral_link)}&text=${encodeURIComponent('🤖 ShopWriter AI — создаю карточки товаров за 30 секунд!')}`
      )
    } else {
      copyLink()
    }
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-5">
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <h1 className="font-bold text-lg">{t.referral_title}</h1>
      </div>

      {info && (
        <div className="space-y-4">
          <div className="tg-secondary rounded-2xl p-4 grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold">👥 {info.total_referred}</p>
              <p className="text-xs tg-hint mt-1">{t.invited}</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">💎 {info.earned_tokens}</p>
              <p className="text-xs tg-hint mt-1">{t.earned}</p>
            </div>
          </div>

          <div className="tg-secondary rounded-2xl p-4 space-y-3">
            <p className="text-sm font-medium">{t.referral_link}</p>
            <div className="bg-[var(--tg-bg)] rounded-xl px-3 py-2.5 text-sm font-mono break-all tg-hint">
              {info.referral_link}
            </div>
            <div className="flex gap-2">
              <button onClick={copyLink} className="flex-1 tg-secondary py-3 rounded-xl text-sm font-medium">
                {copied ? t.copied : '📋 Copy'}
              </button>
              <button onClick={share} className="flex-1 tg-btn py-3 rounded-xl text-sm font-medium">
                📤 {t.share}
              </button>
            </div>
          </div>

          <div className="tg-secondary rounded-2xl p-4 text-sm text-center tg-hint">
            🎁 {t.ref_terms}
          </div>
        </div>
      )}

      {!info && (
        <div className="text-center py-12 tg-hint">
          <p>Загрузка...</p>
        </div>
      )}
    </main>
  )
}
