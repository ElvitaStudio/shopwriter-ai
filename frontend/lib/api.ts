const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail ?? 'Request failed')
  }
  return res.json()
}

export interface UserProfile {
  id: number
  telegram_id: number
  username: string | null
  full_name: string | null
  language: string
  tokens: number
  referral_code: string
  total_cards: number
  created_at: string
}

export interface CardResult {
  card_id: number
  title: string
  description: string
  characteristics: Array<{ name: string; value: string }>
  seo_tags: string[]
  tokens_left: number
}

export interface HistoryCard {
  id: number
  platform: string
  title: string
  description: string
  characteristics: Array<{ name: string; value: string }>
  seo_tags: string[]
  tokens_spent: number
  created_at: string
}

export interface Transaction {
  id: number
  type: string
  amount: number
  description: string | null
  payment_method: string | null
  created_at: string
}

export interface TokenPackage {
  id: string
  tokens: number
  stars: number
  label: string
}

export interface ReferralInfo {
  referral_code: string
  referral_link: string
  total_referred: number
  earned_tokens: number
  bonus_per_referral: number
}

export const api = {
  getUser: (telegramId: number) =>
    request<UserProfile>(`/users/${telegramId}`),

  registerUser: (data: { telegram_id: number; username?: string; full_name?: string; language?: string }) =>
    request<UserProfile>('/users/register', { method: 'POST', body: JSON.stringify(data) }),

  updateLanguage: (telegramId: number, language: string) =>
    request(`/users/${telegramId}/language`, { method: 'PATCH', body: JSON.stringify({ language }) }),

  generateCard: (data: {
    telegram_id: number
    platform: string
    product_name: string
    category: string
    key_features: string
    language: string
    image_base64?: string
  }) => request<CardResult>('/cards/generate', { method: 'POST', body: JSON.stringify(data) }),

  getHistory: (telegramId: number) =>
    request<HistoryCard[]>(`/cards/history/${telegramId}`),

  getPackages: () =>
    request<TokenPackage[]>('/tokens/packages'),

  purchaseTokens: (telegramId: number, packageId: string, paymentMethod = 'stars') =>
    request('/tokens/purchase', {
      method: 'POST',
      body: JSON.stringify({ telegram_id: telegramId, package_id: packageId, payment_method: paymentMethod }),
    }),

  createInvoice: (telegramId: number, packageId: string) =>
    request<{ invoice_url: string }>('/tokens/create_invoice', {
      method: 'POST',
      body: JSON.stringify({ telegram_id: telegramId, package_id: packageId }),
    }),

  getTokenHistory: (telegramId: number) =>
    request<Transaction[]>(`/tokens/history/${telegramId}`),

  getReferral: (telegramId: number) =>
    request<ReferralInfo>(`/referral/${telegramId}`),

  activateReferral: (telegramId: number, referralCode: string) =>
    request('/referral/activate', {
      method: 'POST',
      body: JSON.stringify({ telegram_id: telegramId, referral_code: referralCode }),
    }),
}
