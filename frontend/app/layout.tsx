import type { Metadata } from 'next'
import Script from 'next/script'
import './globals.css'

export const metadata: Metadata = {
  title: 'ShopWriter AI',
  description: 'AI-powered product card generator for marketplaces',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>
        <TelegramInit />
        {children}
      </body>
    </html>
  )
}

function TelegramInit() {
  return (
    <Script id="tg-init" strategy="afterInteractive">
      {`
        if (window.Telegram?.WebApp) {
          const twa = window.Telegram.WebApp;
          twa.ready();
          twa.expand();
          const tp = twa.themeParams;
          const root = document.documentElement;
          if (tp.bg_color) root.style.setProperty('--tg-bg', tp.bg_color);
          if (tp.text_color) root.style.setProperty('--tg-text', tp.text_color);
          if (tp.hint_color) root.style.setProperty('--tg-hint', tp.hint_color);
          if (tp.link_color) root.style.setProperty('--tg-link', tp.link_color);
          if (tp.button_color) root.style.setProperty('--tg-btn', tp.button_color);
          if (tp.button_text_color) root.style.setProperty('--tg-btn-text', tp.button_text_color);
          if (tp.secondary_bg_color) root.style.setProperty('--tg-secondary-bg', tp.secondary_bg_color);
          if (twa.colorScheme === 'dark') document.documentElement.classList.add('dark');
        }
      `}
    </Script>
  )
}
