'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { formatTimeAgo, formatDate } from '@/utils/time'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

function stripHtml(text: string): string {
  return text?.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim() ?? ''
}

export default function CountryBriefsPage() {
  const [selectedCountry, setSelectedCountry] = useState('US')
  const [loadingBrief, setLoadingBrief] = useState(false)
  const [brief, setBrief] = useState<any>(null)

  const { data: stories } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/articles/top-stories?country=${selectedCountry}&days=7&limit=20`,
    fetcher
  )

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
    <div className="h-full overflow-auto">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Country Intelligence</h1>
            <p className="text-gray-500 text-sm mt-0.5">
              Deep dive into regional energy transition developments.
            </p>
          </div>
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="US">United States</option>
            <option value="GB">United Kingdom</option>
            <option value="DE">Germany</option>
            <option value="CN">China</option>
            <option value="IN">India</option>
            <option value="AU">Australia</option>
            <option value="IT">Italy</option>
            <option value="PL">Poland</option>
            <option value="ES">Spain</option>
            <option value="NO">Norway</option>
            <option value="JP">Japan</option>
            <option value="KR">South Korea</option>
            <option value="CA">Canada</option>
          </select>
        </div>
      </div>

      <div className="p-5">
        {/* AI Daily Briefing */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-bold text-gray-900 text-lg">AI Daily Briefing</h2>
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
                Analyzing {selectedCountry} articles with AI... (10-15 seconds)
              </div>
            </div>
          ) : brief?.content ? (
            <div className="prose prose-sm max-w-none">
              <div className="text-gray-600 whitespace-pre-wrap">{brief.content}</div>
              <div className="mt-4 text-xs text-gray-400">
                Generated: {brief.generated_at || 'Just now'} • {brief.article_count || 0} articles analyzed
              </div>
            </div>
          ) : brief?.error ? (
            <div className="text-red-600 text-sm">
              {brief.error}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Click "Generate Brief" to create an AI-powered summary of recent {selectedCountry} energy developments.</p>
          )}
        </div>

        {/* Articles List */}
        <div className="mt-4">
          <p className="text-sm text-gray-600 mb-4">
            Showing {stories?.items?.length || 0} articles
          </p>

          <div className="grid grid-cols-3 gap-6">
            {stories?.items?.map((article: any) => (
              <div
                key={article.id}
                className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
              >
                {/* Image */}
                <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200">
                  <img
                    src={article.image_url || (article.source_name === 'NESO' ? '/source-logos/neso.png' : '/source-logos/eia.jpg')}
                    alt={article.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      const fallback = article.source_name === 'NESO' ? '/source-logos/neso.png' : '/source-logos/eia.jpg'
                      if (target.src !== window.location.origin + fallback) {
                        target.src = fallback
                      }
                    }}
                  />
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-tight">
                    {article.title}
                  </h3>

                  <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                    <span className="font-medium">{article.source_name}</span>
                    <span>•</span>
                    <span>{formatTimeAgo(article.published_at)}</span>
                  </div>

                  <p className="text-sm text-gray-600 line-clamp-3 mb-4 leading-relaxed">
                    {stripHtml(article.summary || article.raw_summary || '') || 'No summary available'}
                  </p>

                  {/* Tags */}
                  <div className="flex gap-2 flex-wrap mb-4">
                    {article.country_codes?.slice(0, 2).map((code: string) => (
                      <span
                        key={code}
                        className="px-2 py-1 bg-blue-50 text-blue-600 rounded text-xs font-medium"
                      >
                        {code}
                      </span>
                    ))}
                    {article.topic_tags?.slice(0, 2).map((tag: string) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium"
                      >
                        {tag.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>

                  {/* Read More */}
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors"
                  >
                    Read More
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
