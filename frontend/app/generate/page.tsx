'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { getTelegramUserId, getTelegramLanguage } from '@/lib/telegram'
import { api, type CardResult } from '@/lib/api'
import { getTranslations, type Locale } from '@/lib/i18n'
import CardForm from '@/components/CardForm'
import CardResultComponent from '@/components/CardResult'

function GeneratePage() {
  const searchParams = useSearchParams()
  const platform = searchParams.get('platform') ?? 'universal'
  const [locale, setLocale] = useState<Locale>('ru')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CardResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const saved = (localStorage.getItem('locale') as Locale) ?? getTelegramLanguage()
    setLocale(saved)
  }, [])

  const t = getTranslations(locale)

  const handleSubmit = async (data: {
    product_name: string
    category: string
    key_features: string
    image_base64?: string
  }) => {
    const telegramId = getTelegramUserId()
    if (!telegramId) {
      setError('Откройте приложение через Telegram')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const card = await api.generateCard({
        telegram_id: telegramId,
        platform,
        language: locale,
        ...data,
      })
      setResult(card)
    } catch (e: any) {
      if (e.message?.includes('Insufficient')) {
        setError(t.error_insufficient)
      } else {
        setError(t.error_generic)
      }
    } finally {
      setLoading(false)
    }
  }

  const platformEmojis: Record<string, string> = {
    rozetka: '🛒', prom: '🏪', wildberries: '🍇', etsy: '🎨', universal: '🌐',
  }

  return (
    <main className="min-h-screen p-4 pb-8 space-y-5">
      <div className="flex items-center gap-3 pt-2">
        <Link href="/" className="text-2xl">←</Link>
        <div>
          <h1 className="font-bold text-lg">
            {platformEmojis[platform] ?? '🌐'} {t.platforms[platform as keyof typeof t.platforms] ?? platform}
          </h1>
          <p className="text-sm tg-hint">{t.generate}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-500 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {result ? (
        <div className="space-y-4">
          <CardResultComponent result={result} locale={locale} />
          <button
            onClick={() => setResult(null)}
            className="w-full tg-secondary py-3 rounded-xl text-sm font-medium"
          >
            ← {t.generate}
          </button>
        </div>
      ) : (
        <CardForm platform={platform} locale={locale} onSubmit={handleSubmit} loading={loading} />
      )}
    </main>
  )
}

export default function GeneratePageWrapper() {
  return (
    <Suspense fallback={<div className="p-8 text-center tg-hint">Загрузка...</div>}>
      <GeneratePage />
    </Suspense>
  )
}
