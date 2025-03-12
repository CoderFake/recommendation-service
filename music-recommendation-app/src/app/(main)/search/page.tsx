import { Suspense } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { SearchBar } from '@/components/search/search-bar'
import { SearchFilters } from '@/components/search/search-filters'
import { SearchResults } from '@/components/search/search-results'
import { searchSongs, searchSpotify } from '@/lib/api/songs'

interface SearchPageProps {
  searchParams: {
    q?: string;
    genre?: string;
    artist?: string;
    page?: string;
  }
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const query = searchParams.q || '';
  const genre = searchParams.genre || '';
  const artist = searchParams.artist || '';
  const page = parseInt(searchParams.page || '1', 10);
  
  let genres: string[] = [];
  let localResults = { songs: [], total: 0 };
  let spotifyResults = [];
  
  try {
    const genresResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/songs/genres`);
    if (genresResponse.ok) {
      const genresData = await genresResponse.json();
      genres = genresData.genres;
    }
    
    if (query || genre || artist) {
      localResults = await searchSongs({
        q: query,
        genre,
        artist,
        page,
        size: 20
      });
      
      if (query) {
        spotifyResults = await searchSpotify(query, 10);
      }
    }
  } catch (error) {
    console.error('Error searching:', error);
  }
  
  return (
    <div className="space-y-6 py-6">
      <PageHeader title="Tìm kiếm" />
      
      <div className="space-y-4">
        <SearchBar
          initialQuery={query}
          onSearch={(q) => {
          }}
        />
        
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <SearchFilters
            genres={genres}
            selectedGenre={genre}
            onFilterChange={(g) => {
            }}
          />
          
          {localResults.total > 0 && (
            <p className="text-sm text-muted-foreground">
              Tìm thấy {localResults.total} kết quả
            </p>
          )}
        </div>
      </div>
      
      <Suspense fallback={<div>Đang tải kết quả tìm kiếm...</div>}>
        <SearchResults
          localResults={localResults.songs}
          spotifyResults={spotifyResults}
          isLoading={false}
        />
      </Suspense>
    </div>
  )
}

