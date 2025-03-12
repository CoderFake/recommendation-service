# Music Recommendation App - Next.js Frontend

## Project Structure

```
music-recommendation-app/
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── images/
│       ├── album-placeholder.png
│       └── default-avatar.png
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── reset-password/page.tsx
│   │   ├── (main)/
│   │   │   ├── discover/page.tsx
│   │   │   ├── search/page.tsx
│   │   │   ├── library/page.tsx
│   │   │   ├── playlists/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   ├── artists/[id]/page.tsx
│   │   │   ├── songs/[id]/page.tsx
│   │   │   ├── recommendations/page.tsx
│   │   │   └── taste-profile/page.tsx
│   │   ├── admin/
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── songs/page.tsx
│   │   │   ├── users/page.tsx
│   │   │   ├── recommendations/page.tsx
│   │   │   └── model/page.tsx
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   │   └── [...nextauth]/route.ts
│   │   │   ├── revalidate/route.ts
│   │   │   └── webhooks/
│   │   │       └── spotify/route.ts
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   ├── register-form.tsx
│   │   │   └── reset-password-form.tsx
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── main-nav.tsx
│   │   │   ├── admin-nav.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── footer.tsx
│   │   │   ├── page-header.tsx
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx
│   │   ├── music/
│   │   │   ├── song-card.tsx
│   │   │   ├── song-list.tsx
│   │   │   ├── song-table.tsx
│   │   │   ├── song-details.tsx
│   │   │   ├── artist-card.tsx
│   │   │   ├── playlist-card.tsx
│   │   │   ├── playlist-form.tsx
│   │   │   ├── mini-player.tsx
│   │   │   └── audio-player.tsx
│   │   ├── recommendations/
│   │   │   ├── recommendation-list.tsx
│   │   │   ├── similar-songs.tsx
│   │   │   ├── recommendations-settings.tsx
│   │   │   └── taste-profile.tsx
│   │   ├── search/
│   │   │   ├── search-bar.tsx
│   │   │   ├── search-filters.tsx
│   │   │   └── search-results.tsx
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dropdown.tsx
│   │   │   ├── modal.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── skeleton.tsx
│   │   │   └── avatar.tsx
│   │   └── admin/
│   │       ├── user-table.tsx
│   │       ├── songs-table.tsx
│   │       ├── model-stats.tsx
│   │       ├── dashboard-stats.tsx
│   │       └── model-control.tsx
│   ├── contexts/
│   │   ├── auth-context.tsx
│   │   └── player-context.tsx
│   ├── hooks/
│   │   ├── use-auth.ts
│   │   ├── use-player.ts
│   │   ├── use-recommendations.ts
│   │   ├── use-search.ts
│   │   ├── use-playlists.ts
│   │   ├── use-songs.ts
│   │   ├── use-toast.ts
│   │   └── use-admin.ts
│   ├── lib/
│   │   ├── api/
│   │   │   ├── auth.ts
│   │   │   ├── songs.ts
│   │   │   ├── interactions.ts
│   │   │   ├── recommendations.ts
│   │   │   ├── playlists.ts
│   │   │   └── admin.ts
│   │   ├── firebase.ts
│   │   ├── spotify.ts
│   │   ├── utils.ts
│   │   ├── constants.ts
│   │   └── types.ts
│   ├── providers/
│   │   ├── auth-provider.tsx
│   │   ├── theme-provider.tsx
│   │   └── toast-provider.tsx
│   └── styles/
│       └── tailwind.css
├── middleware.ts
├── next.config.js
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

## Key Features

- **Authentication System**: Firebase Authentication integration.
- **Main Music Interface**: Discover, search, and interact with songs.
- **Recommendation System**: Personalized recommendations based on user preferences.
- **User Library**: Playlists, liked songs, and history management.
- **Admin Panel**: Separate administrative interface with user management, song management, and recommendation model controls.
- **Responsive Design**: Works on desktop and mobile devices.
- **Dark/Light Mode**: Theme toggle functionality.

## Design Patterns

1. **Container/Presentation Pattern**: Separates data fetching from UI rendering.
2. **Context API Pattern**: For global state management (auth, player).
3. **Custom Hooks Pattern**: For reusable logic and API interactions.
4. **Composition Pattern**: Building