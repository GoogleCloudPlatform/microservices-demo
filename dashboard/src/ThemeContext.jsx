import { createContext, useContext, useState } from 'react'
import { lightTheme, darkTheme } from './styles/theme'

const ThemeCtx = createContext({ theme: lightTheme, dark: false, setDark: () => {} })

export function useTheme() {
  return useContext(ThemeCtx)
}

export function ThemeProvider({ children }) {
  const [dark, setDark] = useState(false)
  return (
    <ThemeCtx.Provider value={{ theme: dark ? darkTheme : lightTheme, dark, setDark }}>
      {children}
    </ThemeCtx.Provider>
  )
}
