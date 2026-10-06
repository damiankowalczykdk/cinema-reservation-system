import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { LANGUAGES, DEFAULT_LANGUAGE, translate } from './translations.js'
import { setFormatLanguage } from '../format.js'

const STORAGE_KEY = 'cinema.lang'

const LanguageContext = createContext(null)

// saved choice first, then the browser language, then English
function initialLanguage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (LANGUAGES.includes(saved)) return saved
  } catch {
    // storage blocked (private mode): fall through to the browser language
  }
  const browser = (navigator.language || '').slice(0, 2).toLowerCase()
  return LANGUAGES.includes(browser) ? browser : DEFAULT_LANGUAGE
}

function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    const initial = initialLanguage()
    setFormatLanguage(initial)
    return initial
  })

  const setLang = useCallback((next) => {
    if (!LANGUAGES.includes(next)) return
    // format.js helpers read the language at call time, so switch it before the re-render
    setFormatLanguage(next)
    setLangState(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // not persisted, still applies for this visit
    }
  }, [])

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const value = useMemo(
    () => ({ lang, setLang, languages: LANGUAGES, t: (key, vars) => translate(lang, key, vars) }),
    [lang, setLang],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

function useI18n() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useI18n must be used inside <LanguageProvider>')
  return ctx
}

export { LanguageProvider, useI18n }
