"use client"

import { useState, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { Input } from '@/components/ui/input'

interface SearchBarProps {
  onSearch: (query: string) => void
  initialQuery?: string
  placeholder?: string
}

export function SearchBar({ onSearch, initialQuery = '', placeholder = 'Tìm bài hát, nghệ sĩ, album...' }: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery)
  
  useEffect(() => {
    setQuery(initialQuery)
  }, [initialQuery])
  
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query !== initialQuery) {
        onSearch(query)
      }
    }, 500)
    
    return () => clearTimeout(timeoutId)
  }, [query, onSearch, initialQuery])
  
  const handleClear = () => {
    setQuery('')
    onSearch('')
  }
  
  return (
    <div className="relative">
      <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="pl-10 pr-10"
      />
      {query && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
          aria-label="Xóa tìm kiếm"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}