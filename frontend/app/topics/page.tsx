'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { formatTimeAgo, formatDate } from '@/utils/time'
import ArticleChat from '@/components/ArticleChat'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

const topics = [
  { id: 'all', label: 'All' },
  { id: 'conflict', label: 'Conflict' },
  { id: 'displacement', label: 'Displacement' },
  { id: 'famine', label: 'Famine & Food Crisis' },
  { id: 'disease_outbreak', label: 'Disease Outbreak' },
  { id: 'natural_disaster', label: 'Natural Disaster' },
  { id: 'earthquake', label: 'Earthquake' },
  { id: 'humanitarian_response', label: 'Humanitarian Response' },
  { id: 'protection', label: 'Protection & Human Rights' },
  { id: 'early_warning', label: 'Early Warning' },
]

const countries = [
  { code: 'all', name: 'All Countries' },
  { code: 'SD', name: 'Sudan' },
  { code: 'SS', name: 'South Sudan' },
  { code: 'YE', name: 'Yemen' },
  { code: 'PS', name: 'Gaza / Palestine' },
  { code: 'CD', name: 'DR Congo' },
  { code: 'ET', name: 'Ethiopia' },
  { code: 'SO', name: 'Somalia' },
  { code: 'AF', name: 'Afghanistan' },
  { code: 'HT', name: 'Haiti' },
  { code: 'MM', name: 'Myanmar' },
  { code: 'ML', name: 'Mali' },
  { code: 'UA', name: 'Ukraine' },
  { code: 'SY', name: 'Syria' },
  { code: 'LB', name: 'Lebanon' },
  { code: 'IL', name: 'Israel' },
  { code: 'IQ', name: 'Iraq' },
  { code: 'LY', name: 'Libya' },
  { code: 'NE', name: 'Niger' },
  { code: 'CF', name: 'Central African Republic' },
  { code: 'NG', name: 'Nigeria' },
  { code: 'MZ', name: 'Mozambique' },
  { code: 'BD', name: 'Bangladesh' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'US', name: 'United States' },
  { code: 'FR', name: 'France' },
]

const topicColorMap: { [key: string]: string } = {
  'conflict': 'bg-red-700',
  'displacement': 'bg-orange-600',
  'famine': 'bg-yellow-600',
  'disease_outbreak': 'bg-purple-600',
  'natural_disaster': 'bg-blue-600',
  'earthquake': 'bg-gray-700',
  'humanitarian_response': 'bg-teal-600',
  'protection': 'bg-pink-600',
  'early_warning': 'bg-indigo-600',
}

const topicLabelMap: { [key: string]: string } = {
  'conflict': 'Conflict',
  'displacement': 'Displacement',
  'famine': 'Famine & Food Crisis',
  'disease_outbreak': 'Disease Outbreak',
  'natural_disaster': 'Natural Disaster',
  'earthquake': 'Earthquake',
  'humanitarian_response': 'Humanitarian Response',
  'protection': 'Protection & Human Rights',
  'early_warning': 'Early Warning',
}

export default function TopicsPage() {
  const [selectedTopic, setSelectedTopic] = useState('all')
  const [selectedCountry, setSelectedCountry] = useState('all')
  const [days, setDays] = useState(7)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const { data } = useSWR(
    `${process.env.NEXT_PUBLIC_API_URL}/articles?days=${days}&page_size=100`,
    fetcher
  )

  // Filter articles by selected topic and country
  const filteredArticles = data?.items?.filter((article: any) => {
    // Topic filter
    const topicMatch = selectedTopic === 'all' || article.topic_tags?.some((tag: string) => tag === selectedTopic)
    // Country filter
    const countryMatch = selectedCountry === 'all' || article.country_codes?.includes(selectedCountry)
    return topicMatch && countryMatch;
  })

  const getTopicColor = (tags: string[]) => {
    if (!tags || tags.length === 0) return 'bg-gray-600'
    const firstTag = tags[0]
    return topicColorMap[firstTag] || 'bg-gray-600'
  }

  const getTopicLabel = (tags: string[]) => {
    if (!tags || tags.length === 0) return 'General'
    const firstTag = tags[0]
    return topicLabelMap[firstTag] || firstTag.replace(/_/g, ' ')
  }

  return (
    <div className="h-full overflow-auto bg-gray-50">
      {/* Filter Bar */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        {/* Topic Filters */}
        <div className="mb-4">
          <label className="text-xs font-semibold text-gray-500 uppercase mb-2 block">Topics</label>
          <div className="flex items-center gap-3 flex-wrap">
            {topics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => setSelectedTopic(topic.id)}
                className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${selectedTopic === topic.id
                  ? 'bg-gray-900 text-white shadow-md'
                  : 'bg-white text-gray-700 border border-gray-300 hover:border-gray-400 hover:shadow-sm'
                  }`}
              >
                {topic.label}
              </button>
            ))}
          </div>
        </div>

        {/* Country Filter */}
        <div className="flex items-center gap-3">
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase mb-2 block">Countries</label>
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            >
              {countries.map((country) => (
                <option key={country.code} value={country.code}>
                  {country.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase mb-2 block">Timeline</label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Articles Section */}
      <div className="px-8 py-6">
        {/* Article Count */}
        <p className="text-sm text-gray-600 mb-6">
          Showing {filteredArticles?.length || 0} articles
        </p>

        {/* Articles Grid - 3 columns */}
        <div className="grid grid-cols-3 gap-6">
          {filteredArticles?.map((article: any) => (
            <div
              key={article.id}
              className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow"
            >
              {/* Image with Topic Badge */}
              <div className="relative h-56 bg-gradient-to-br from-gray-100 to-gray-200">
                <img
                  src={
                    article.image_url
                      ? article.image_url
                      : article.source_name === 'NESO'
                        ? '/source-logos/neso.png'
                        : '/source-logos/eia.jpg'
                  }
                  alt={article.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    if (article.source_name === 'NESO') {
                      if (target.src !== window.location.origin + '/source-logos/neso.png') {
                        target.src = '/source-logos/neso.png'
                      }
                    } else {
                      if (target.src !== window.location.origin + '/source-logos/eia.jpg') {
                        target.src = '/source-logos/eia.jpg'
                      }
                    }
                  }}
                />
                {/* Topic Badge Overlay */}
                {article.topic_tags && article.topic_tags.length > 0 && (
                  <div className="absolute top-4 left-4">
                    <span className={`${getTopicColor(article.topic_tags)} text-white text-xs font-medium px-3 py-1.5 rounded-full shadow-md`}>
                      {getTopicLabel(article.topic_tags)}
                    </span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-5">
                {/* Title */}
                <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-tight">
                  {article.title}
                </h3>

                {/* Source and Date */}
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                  <span className="font-medium">{article.source_name || 'News Source'}</span>
                  <span>•</span>
                  <span>{formatTimeAgo(article.published_at)}</span>
                </div>

                {/* Summary */}
                <p className="text-sm text-gray-600 line-clamp-3 mb-4 leading-relaxed">
                  {article.summary || article.raw_summary || 'No summary available'}
                </p>

                {/* Read More Button */}
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

        {/* Empty State */}
        {(!filteredArticles || filteredArticles.length === 0) && (
          <div className="text-center py-12">
            <p className="text-gray-500">No articles found for this topic.</p>
          </div>
        )}
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
