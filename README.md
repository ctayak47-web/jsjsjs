# CrolGram - Premium Messaging & Collectibles

Modern iOS-first web application built with Next.js, React, TypeScript, and Firebase.

## Features

- 🔐 Email/Password authentication with Firebase
- 💬 Messaging system (foundation)
- 🎁 Collectible gifts system (coming)
- 🏪 Marketplace for trading gifts (coming)
- ⭐ CrolGram Stars currency system
- 🌙 Dark/Light/AMOLED themes
- 📱 PWA-ready, mobile-first design
- ✔️ Safe area support for notched devices

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Backend**: Firebase (Auth, Firestore, Storage)
- **Animations**: Framer Motion
- **State**: Zustand
- **Icons**: Custom SVG system

## Setup

### 1. Clone and install

```bash
npm install
```

### 2. Firebase Configuration

Create `.env.local`:

```
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### 3. Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/              # Next.js pages
├── components/       # Reusable UI components
├── hooks/           # Custom React hooks
├── lib/             # Utilities (Firebase config, etc)
├── store/           # Zustand state management
├── types/           # TypeScript definitions
└── styles/          # Global styles
```

## Key Components

- **MobileShell**: Handles navigation & mobile layout
- **Button**: Reusable with variants (primary, secondary, danger, ghost)
- **Card**: Content containers
- **LoadingSpinner**: Loading states
- **IconSystem**: Custom monochrome SVG icons

## Authentication

- Sign up with email/password
- Automatic profile creation
- Starter bonus: 100 CG Stars
- Firebase Security Rules protect user data

## Development

### Adding a new page

1. Create file in `src/app/[section]/page.tsx`
2. Wrap with auth check using `useAuthStore`
3. Use mobile-first responsive design

### Styling

- Use Tailwind classes
- Support dark mode with `dark:` prefix
- AMOLED mode with `amoled:` prefix

### State Management

- Global: `useAuthStore`, `useThemeStore`
- Local: React hooks (useState, useEffect)

## Firestore Collections

- `users` - User accounts
- `profiles` - User profiles
- `numbers` - CrolGram phone numbers
- `chats` - Conversations
- `messages` - Chat messages
- `gifts` - Collectible definitions
- `giftInventory` - User owned gifts
- `starBalances` - User balance
- `marketListings` - Marketplace listings

## Security

✅ Server-side validation
✅ Firestore Security Rules
✅ No secrets in code
✅ Protected routes
✅ Rate limiting (Cloud Functions)

## Next Phases

1. ✅ Foundation & Auth
2. Chats & Messaging
3. Profile & Settings
4. Gift System
5. Marketplace
6. Trading
7. Bot Integration
8. PWA Optimization

## License

Proprietary
