# Todo App Frontend - Phase 2

Next.js 14 frontend for the Todo SaaS application with premium UI and authentication.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Premium UI components
- **Framer Motion** - Smooth animations
- **next-themes** - Dark/light theme support

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Setup environment

```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 3. Start development server

```bash
npm run dev
```

App will be available at: http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/          # Next.js App Router pages
│   ├── components/   # React components
│   │   └── ui/       # shadcn/ui components
│   ├── hooks/        # Custom React hooks
│   ├── lib/          # Utility functions
│   ├── styles/       # Global styles
│   └── types/        # TypeScript type definitions
├── public/           # Static assets
└── package.json      # Dependencies and scripts
```

## Available Scripts

```bash
# Development
npm run dev           # Start dev server

# Building
npm run build         # Build for production
npm run start         # Start production server

# Testing
npm test              # Run unit tests
npm run test:watch    # Watch mode
npm run test:e2e      # Run E2E tests with Playwright

# Code Quality
npm run lint          # Run ESLint
npm run lint:fix      # Fix ESLint issues
npm run format        # Format with Prettier
npm run type-check    # TypeScript type checking
```

## Features

### Authentication
- Login with email/password
- User registration with validation
- Secure JWT token storage
- Auto-redirect based on auth state

### Todo Management
- Create, edit, delete todos
- Mark todos as complete
- Filter by status
- Search todos
- Sort by date, priority

### User Profile
- View and edit profile
- Upload avatar (Cloudinary)
- Update name and email

### AI Features
- Generate todos from text
- Summarize tasks
- Prioritize tasks

### UI/UX
- Dark/light theme toggle
- Smooth animations
- Mobile responsive
- Loading states
- Error handling

## Environment Variables

See `.env.example` for required environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_ENABLE_AI=true
```

## Component Library

This project uses [shadcn/ui](https://ui.shadcn.com/) for premium UI components.

### Adding new components

```bash
npx shadcn-ui@latest add [component-name]
```

Available components:
- Button, Input, Label, Card
- Dialog, Dropdown Menu, Select
- Tabs, Switch, Avatar
- Toast, and more...

## State Management

- React Context for auth state
- React hooks for local state
- Server Components for data fetching
- Client Components for interactivity

## Styling

- **Tailwind CSS** - Utility classes
- **CSS Variables** - Theme customization
- **Framer Motion** - Animations
- **shadcn/ui** - Pre-built components

## Testing

```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e

# E2E with UI
npm run e2e:ui

# E2E debug mode
npm run e2e:debug
```

## Building for Production

```bash
# Build
npm run build

# Test production build locally
npm run start
```

## Deployment

This app is designed to be deployed on **Vercel**:

1. Push code to GitHub
2. Import project in Vercel
3. Configure environment variables
4. Deploy

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## License

MIT
