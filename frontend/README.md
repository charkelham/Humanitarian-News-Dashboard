# Humanitarian News Dashboard - Frontend

A clean, minimal Next.js dashboard for humanitarian crisis news monitoring and AI-powered analysis.

## Features

- **Left Sidebar**: Country list with article counts for crisis-affected regions
- **Main Panel**: Top stories with ranking scores, filters by humanitarian topic and date range
- **Right Panel**: RAG chat interface with citation links
- **Country Briefs**: AI-generated situation briefs per country covering conflict, displacement, famine, and more
- **Real-time Data**: SWR for automatic data fetching and caching
- **Responsive Design**: Tailwind CSS for clean, minimal styling

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Main dashboard page
├── components/
│   ├── CountrySidebar.tsx    # Country list with counts
│   ├── FilterChips.tsx       # Topic and date filters
│   ├── TopStoriesList.tsx    # Ranked stories list
│   └── ChatPanel.tsx         # RAG chat interface
├── lib/
│   ├── api.ts                # API client functions
│   └── types.ts              # TypeScript types
└── package.json
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Data Fetching**: SWR
- **Language**: TypeScript
- **Date Formatting**: date-fns

## Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Build for Production

```bash
npm run build
npm start
```

## Docker

The frontend is included in the main `docker-compose.yml` and will be available at http://localhost:3000
