'use client'

import { useState } from 'react'
import type { Locale } from '@/lib/i18n'
import { getTranslations } from '@/lib/i18n'

interface Props {
  platform: string
  locale: Locale
  onSubmit: (data: {
    product_name: string
    category: string
    key_features: string
    image_base64?: string
  }) => void
  loading: boolean
}

export default function CardForm({ platform, locale, onSubmit, loading }: Props) {
  const t = getTranslations(locale)
  const [productName, setProductName] = useState('')
  const [category, setCategory] = useState('')
  const [features, setFeatures] = useState('')
  const [imageBase64, setImageBase64] = useState<string | undefined>()

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      setImageBase64(result.split(',')[1])
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!productName.trim() || !category.trim() || !features.trim()) return
    onSubmit({ product_name: productName, category, key_features: features, image_base64: imageBase64 })
  }

  const inputClass = 'w-full tg-secondary rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 ring-[var(--tg-btn)] transition'

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1.5">{t.product_name}</label>
        <input
          className={inputClass}
          placeholder={t.product_name_placeholder}
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">{t.category}</label>
        <input
          className={inputClass}
          placeholder={t.category_placeholder}
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">{t.features}</label>
        <textarea
          className={`${inputClass} resize-none h-24`}
          placeholder={t.features_placeholder}
          value={features}
          onChange={(e) => setFeatures(e.target.value)}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5">{t.photo}</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="w-full text-sm tg-hint"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full tg-btn py-4 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? t.creating : t.create_btn}
      </button>
    </form>
  )
}
