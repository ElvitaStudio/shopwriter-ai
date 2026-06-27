'use client'

import { useState } from 'react'
import type { CardResult as CardResultType } from '@/lib/api'
import type { Locale } from '@/lib/i18n'
import { getTranslations } from '@/lib/i18n'
import { hapticSuccess } from '@/lib/telegram'

interface Props {
  result: CardResultType
  locale: Locale
}

export default function CardResult({ result, locale }: Props) {
  const t = getTranslations(locale)
  const [copied, setCopied] = useState(false)

  const fullText = [
    `${t.result_title_label}: ${result.title}`,
    `\n${t.result_desc_label}:\n${result.description}`,
    `\n${t.result_chars_label}:\n${result.characteristics.map((c) => `${c.name}: ${c.value}`).join('\n')}`,
    `\n${t.result_tags_label}:\n${result.seo_tags.join(', ')}`,
  ].join('\n')

  const copyText = async (text: string) => {
    await navigator.clipboard.writeText(text)
    hapticSuccess()
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadTxt = () => {
    const blob = new Blob([fullText], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `card-${result.card_id}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4">
      <div className="tg-secondary rounded-2xl p-4 space-y-3">
        <section>
          <h3 className="text-xs font-semibold tg-hint uppercase tracking-wide mb-1">{t.result_title_label}</h3>
          <p className="font-semibold">{result.title}</p>
        </section>

        <section>
          <h3 className="text-xs font-semibold tg-hint uppercase tracking-wide mb-1">{t.result_desc_label}</h3>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{result.description}</p>
        </section>

        {result.characteristics.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold tg-hint uppercase tracking-wide mb-1">{t.result_chars_label}</h3>
            <div className="space-y-1">
              {result.characteristics.map((c, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="tg-hint min-w-[100px]">{c.name}:</span>
                  <span>{c.value}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {result.seo_tags.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold tg-hint uppercase tracking-wide mb-1">{t.result_tags_label}</h3>
            <div className="flex flex-wrap gap-1">
              {result.seo_tags.map((tag, i) => (
                <span key={i} className="text-xs px-2 py-0.5 rounded-full tg-btn opacity-80">
                  {tag}
                </span>
              ))}
            </div>
          </section>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => copyText(fullText)}
          className="flex-1 tg-btn py-3 rounded-xl font-medium text-sm"
        >
          {copied ? t.copied : t.copy_all}
        </button>
        <button
          onClick={() => copyText(result.description)}
          className="flex-1 tg-secondary py-3 rounded-xl font-medium text-sm"
        >
          {t.copy_description}
        </button>
        <button
          onClick={downloadTxt}
          className="tg-secondary px-4 py-3 rounded-xl font-medium text-sm"
        >
          📥
        </button>
      </div>

      <div className="text-center tg-hint text-sm">
        💎 {t.tokens_left}: {result.tokens_left}
      </div>
    </div>
  )
}
