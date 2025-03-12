"use client"

import { useState } from 'react'
import { Check, ChevronsUpDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { cn } from '@/lib/utils'

interface SearchFiltersProps {
  genres: string[]
  onFilterChange: (genre: string) => void
  selectedGenre?: string
}

export function SearchFilters({ genres, onFilterChange, selectedGenre }: SearchFiltersProps) {
  const [open, setOpen] = useState(false)
  
  return (
    <div className="flex space-x-4">
      <div>
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="justify-between w-[200px]"
            >
              {selectedGenre ? selectedGenre : "Thể loại nhạc"}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[200px] p-0">
            <Command>
              <CommandInput placeholder="Tìm thể loại..." />
              <CommandEmpty>Không tìm thấy thể loại nào.</CommandEmpty>
              <CommandGroup>
                <CommandItem
                  onSelect={() => {
                    onFilterChange('')
                    setOpen(false)
                  }}
                  className="justify-between"
                >
                  Tất cả
                  {!selectedGenre && <Check className="h-4 w-4" />}
                </CommandItem>
                {genres.map((genre) => (
                  <CommandItem
                    key={genre}
                    onSelect={() => {
                      onFilterChange(genre)
                      setOpen(false)
                    }}
                    className="justify-between"
                  >
                    {genre}
                    {genre === selectedGenre && <Check className="h-4 w-4" />}
                  </CommandItem>
                ))}
              </CommandGroup>
            </Command>
          </PopoverContent>
        </Popover>
      </div>
    </div>
  )
}
