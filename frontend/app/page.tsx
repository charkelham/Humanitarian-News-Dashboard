'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { formatTimeAgo } from '@/utils/time'
import ArticleChat from '@/components/ArticleChat'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

function stripHtml(text: string): string {
  return text?.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim() ?? ''
}

export default function Dashboard() {
  const [days, setDays] = useState(7)
  const [selectedCountry, setSelectedCountry] = useState('SD')
  const [loadingBrief, setLoadingBrief] = useState(false)
  const [brief, setBrief] = useState<any>(null)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const { data: stories } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/articles/top-stories?country=${selectedCountry}&days=${days}&limit=1`,
    fetcher,
    { refreshInterval: 30000 }
  )

  const { data: updates } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/articles?days=${days}&page_size=3`,
    fetcher
  )

  const { data: countries } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/countries?days=${days}`,
    fetcher
  )

  const { data: activityData } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/stats/activity?days=${days}&country_code=${selectedCountry}`,
    fetcher
  )

  const { data: topicBreakdown } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/stats/topic-breakdown?days=${days}&country_code=${selectedCountry}`,
    fetcher
  )

  const featuredStory = stories?.items?.[0]

  const generateBrief = async () => {
    setLoadingBrief(true)
    setBrief(null)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/briefs/latest?country_code=${selectedCountry}`
      )
      const data = await response.json()
      setBrief(data)
    } catch (error) {
      console.error('Failed to generate brief:', error)
      setBrief({ content: null, error: 'Failed to generate brief' })
    } finally {
      setLoadingBrief(false)
    }
  }

  return (
    <div className="h-full overflow-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Humanitarian News Dashboard</h1>
            <p className="text-gray-500 text-sm mt-0.5">
              Real-time humanitarian crisis monitoring for FCDO / HEROS early warning.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="SD">Sudan</option>
              <option value="SS">South Sudan</option>
              <option value="YE">Yemen</option>
              <option value="PS">Gaza / Palestine</option>
              <option value="CD">DR Congo</option>
              <option value="ET">Ethiopia</option>
              <option value="SO">Somalia</option>
              <option value="AF">Afghanistan</option>
              <option value="HT">Haiti</option>
              <option value="MM">Myanmar</option>
              <option value="ML">Mali</option>
              <option value="UA">Ukraine</option>
              <option value="SY">Syria</option>
            </select>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-8">
        {/* AI Daily Briefing */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-gray-900 text-lg">AI Situation Brief</h2>
            <button
              onClick={generateBrief}
              disabled={loadingBrief}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm font-medium"
            >
              {loadingBrief ? 'Generating...' : 'Generate Brief'}
            </button>
          </div>

          {loadingBrief ? (
            <div className="text-center py-8">
              <div className="animate-pulse text-gray-500">
                Analysing humanitarian signals for {selectedCountry}... (10-15 seconds)
              </div>
            </div>
          ) : brief?.content ? (
            <div>
              {/* Brief Content */}
              <div className="prose prose-lg max-w-none">
                <style jsx>{`
                  .prose h1 { color: #1f2937; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; border-left: 4px solid #2563eb; padding-left: 1rem; }
                  .prose h2 { color: #374151; font-size: 1.25rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; }
                  .prose h3 { color: #4b5563; font-size: 1.1rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }
                  .prose p { color: #374151; line-height: 1.8; margin-bottom: 1rem; }
                  .prose strong { color: #1f2937; font-weight: 600; }
                  .prose ul { margin-left: 1.5rem; margin-bottom: 1rem; }
                  .prose li { color: #374151; margin-bottom: 0.5rem; }
                `}</style>
                <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">{brief.content}</div>
              </div>

              {/* Footer with metadata */}
              <div className="mt-6 pt-4 border-t border-gray-200 flex items-center justify-between">
                <div className="text-xs text-gray-400">
                  Generated: {brief.generated_at || 'Just now'} • {brief.article_count || 0} articles analysed
                </div>
                {brief.articles && brief.articles.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Sources:</span>
                    <div className="flex gap-1">
                      {[...new Set(brief.articles.slice(0, 5).map((a: any) => a.source_name))].map((source: any, idx: number) => (
                        <span
                          key={idx}
                          className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-100"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : brief?.error ? (
            <div className="text-red-600 text-sm">
              {brief.error}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">
              Click "Generate Brief" to create an AI-powered humanitarian situation brief for the selected country.
            </p>
          )}
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Featured Article */}
          <div className="col-span-2">
            {featuredStory ? (
              <a
                href={featuredStory.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-white rounded-xl shadow-sm overflow-hidden h-full hover:shadow-lg transition-shadow"
              >
                <div className="p-5">
                  <div className="flex items-center gap-2 text-xs mb-3">
                    <span className="font-bold text-red-600 uppercase">
                      {featuredStory.source_name}
                    </span>
                    <span className="text-gray-400">•</span>
                    <span className="text-gray-500">
                      {formatTimeAgo(featuredStory.published_at)}
                    </span>
                    {featuredStory.topic_tags?.[0] && (
                      <>
                        <span className="text-gray-400">•</span>
                        <span className="bg-red-50 text-red-700 px-2 py-0.5 rounded-full border border-red-100 uppercase text-xs font-medium">
                          {featuredStory.topic_tags[0].replace(/_/g, ' ')}
                        </span>
                      </>
                    )}
                  </div>
                  <h2 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
                    {featuredStory.title}
                  </h2>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {stripHtml(featuredStory.summary || '')}
                  </p>
                  {featuredStory.country_codes?.length > 0 && (
                    <div className="mt-4 flex gap-2 flex-wrap">
                      {featuredStory.country_codes.map((code: string) => (
                        <span key={code} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                          {code}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </a>
            ) : (
              <div className="bg-gray-100 rounded-lg h-full flex items-center justify-center min-h-48">
                <div className="text-gray-400 text-sm">No featured story available — try running ingestion</div>
              </div>
            )}
          </div>

          {/* Right Sidebar — Latest Updates */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold text-gray-900 text-sm">Latest Updates</h3>
                <a href="/topics" className="text-blue-600 text-xs hover:underline">
                  View All
                </a>
              </div>
              <div className="space-y-3">
                {updates?.items?.slice(0, 5).map((item: any) => (
                  <a
                    key={item.id}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex gap-3 group"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-medium text-gray-900 line-clamp-2 group-hover:text-blue-600">
                        {item.title}
                      </h4>
                      <p className="text-xs text-gray-500 mt-1">
                        {item.topic_tags?.[0]?.replace(/_/g, ' ') || 'General'} • {formatTimeAgo(item.published_at)}
                      </p>
                    </div>
                  </a>
                ))}
                {!updates?.items?.length && (
                  <p className="text-xs text-gray-400">No articles yet — run ingestion first</p>
                )}
              </div>
            </div>

            {/* Crisis type breakdown */}
            {topicBreakdown?.topics?.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
                <h3 className="font-bold text-gray-900 text-sm mb-3">Crisis Types</h3>
                <div className="space-y-2">
                  {topicBreakdown.topics.slice(0, 5).map((topic: any) => (
                    <div key={topic.topic} className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 capitalize">
                        {topic.topic.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs font-medium text-gray-900">{topic.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center z-40"
        aria-label="Open chat assistant"
      >
        {isChatOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {/* Chat Component */}
      <ArticleChat
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        contextCountry={selectedCountry}
      />
    </div>
  )
}
