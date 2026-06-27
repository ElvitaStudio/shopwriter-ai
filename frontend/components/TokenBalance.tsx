'use client'

import Link from 'next/link'
import type { Locale } from '@/lib/i18n'
import { getTranslations } from '@/lib/i18n'

interface Props {
  tokens: number
  locale: Locale
}

export default function TokenBalance({ tokens, locale }: Props) {
  const t = getTranslations(locale)
  return (
    <div className="flex items-center gap-2 tg-secondary rounded-xl px-4 py-2">
      <span className="text-yellow-500 text-lg">💎</span>
      <span className="font-medium">{tokens}</span>
      <span className="tg-hint text-sm">{t.tokens_left}</span>
      <Link href="/tokens" className="ml-auto text-sm font-medium" style={{ color: 'var(--tg-link)' }}>
        {t.buy_tokens}
      </Link>
    </div>
  )
}
