'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Bot, BookOpen, Code, Terminal, Mic, Plug, Shield, Globe, ChevronRight, Search, Sun, Moon, Menu, X } from 'lucide-react'

const DOCS_SECTIONS = [
  {
    title: 'Getting Started',
    icon: Bot,
    pages: [
      { title: 'Introduction', href: '/docs/introduction', description: 'What is ELE Agent and how it works' },
      { title: 'Quick Start', href: '/docs/quick-start', description: 'Get up and running in 5 minutes' },
      { title: 'Installation', href: '/docs/installation', description: 'Desktop, CLI, and Web installation' },
      { title: 'Configuration', href: '/docs/configuration', description: 'Environment variables and settings' },
    ],
  },
  {
    title: 'Core Concepts',
    icon: BookOpen,
    pages: [
      { title: 'Architecture', href: '/docs/architecture', description: 'System architecture overview' },
      { title: 'Agent Loop', href: '/docs/agent-loop', description: 'How the agent processes requests' },
      { title: 'Memory System', href: '/docs/memory', description: 'Short-term, long-term, episodic, project' },
      { title: 'RAG & Context', href: '/docs/rag', description: 'Retrieval-augmented generation' },
    ],
  },
  {
    title: 'Interfaces',
    icon: Globe,
    pages: [
      { title: 'Web Dashboard', href: '/docs/web', description: 'Next.js web interface guide' },
      { title: 'Desktop App', href: '/docs/desktop', description: 'Electron app features and shortcuts' },
      { title: 'CLI/TUI', href: '/docs/cli', description: 'Terminal interface usage' },
      { title: 'Telegram Bot', href: '/docs/telegram', description: 'Remote access via Telegram' },
    ],
  },
  {
    title: 'Features',
    icon: Code,
    pages: [
      { title: 'Voice Control', href: '/docs/voice', description: 'STT, TTS, and wake word' },
      { title: 'File Operations', href: '/docs/files', description: 'Read, write, search, and manage files' },
      { title: 'Browser Automation', href: '/docs/browser', description: 'Playwright-powered web control' },
      { title: 'Shell Commands', href: '/docs/shell', description: 'Safe command execution' },
      { title: 'Parallel LLMs', href: '/docs/parallel-llms', description: 'Multi-provider orchestration' },
    ],
  },
  {
    title: 'Extending ELE',
    icon: Plug,
    pages: [
      { title: 'Plugin Development', href: '/docs/plugins/development', description: 'Create custom plugins' },
      { title: 'Plugin Manifest', href: '/docs/plugins/manifest', description: 'JSON manifest specification' },
      { title: 'Python Decorators', href: '/docs/plugins/python', description: 'Native Python plugin API' },
      { title: 'WASM Plugins', href: '/docs/plugins/wasm', description: 'Sandboxed polyglot plugins' },
      { title: 'Marketplace', href: '/docs/plugins/marketplace', description: 'Publishing and distribution' },
    ],
  },
  {
    title: 'API Reference',
    icon: Terminal,
    pages: [
      { title: 'REST API', href: '/docs/api/rest', description: 'HTTP endpoints reference' },
      { title: 'WebSocket API', href: '/docs/api/websocket', description: 'Real-time streaming events' },
      { title: 'Authentication', href: '/docs/api/auth', description: 'JWT and API key auth' },
      { title: 'Rate Limits', href: '/docs/api/rate-limits', description: 'Tier-based limits' },
      { title: 'Error Codes', href: '/docs/api/errors', description: 'Error code reference' },
    ],
  },
  {
    title: 'Deployment',
    icon: Shield,
    pages: [
      { title: 'Self-Hosting', href: '/docs/deployment/self-host', description: 'Oracle Cloud, Docker, systemd' },
      { title: 'Supabase Setup', href: '/docs/deployment/supabase', description: 'Database and auth configuration' },
      { title: 'Cloudflare Pages', href: '/docs/deployment/cloudflare', description: 'Web frontend deployment' },
      { title: 'CI/CD', href: '/docs/deployment/ci-cd', description: 'GitHub Actions workflows' },
      { title: 'Desktop Distribution', href: '/docs/deployment/desktop', description: 'Code signing and releases' },
    ],
  },
]

const SEARCH_RESULTS = [
  { title: 'Wake Word Configuration', href: '/docs/voice#wake-word', section: 'Voice Control' },
  { title: 'Plugin Permissions', href: '/docs/plugins/manifest#permissions', section: 'Plugin Development' },
  { title: 'Memory Layers', href: '/docs/memory#layers', section: 'Memory System' },
  { title: 'Parallel LLM Merge', href: '/docs/parallel-llms#merging', section: 'Parallel LLMs' },
  { title: 'Supabase RLS', href: '/docs/deployment/supabase#rls', section: 'Deployment' },
  { title: 'WebSocket Events', href: '/docs/api/websocket#events', section: 'API Reference' },
]

export default function DocsPage() {
  const [search, setSearch] = useState('')
  const [showSidebar, setShowSidebar] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const filteredResults = search
    ? SEARCH_RESULTS.filter(r =>
        r.title.toLowerCase().includes(search.toLowerCase()) ||
        r.section.toLowerCase().includes(search.toLowerCase())
      )
    : []

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <aside className={`fixed inset-y-0 left-0 z-40 transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-100 dark:border-gray-700 w-72 ${!showSidebar && 'hidden lg:block'} ${mobileMenuOpen && 'block'}`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-100 dark:border-gray-700">
            <Link href="/docs" className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              <span className="text-xl font-bold text-gray-900 dark:text-gray-100">ELE Docs</span>
            </Link>
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search docs..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10"
              />
            </div>

            {search && filteredResults.length > 0 && (
              <div className="mt-4 max-h-48 overflow-y-auto">
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Results</p>
                <ul className="space-y-1">
                  {filteredResults.map((result, i) => (
                    <li key={i}>
                      <Link
                        href={result.href}
                        className="block px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                      >
                        <p className="font-medium">{result.title}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{result.section}</p>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <nav className="flex-1 px-4 overflow-y-auto" aria-label="Documentation">
            {DOCS_SECTIONS.map((section, i) => (
              <div key={i} className="mb-6">
                <h3 className="flex items-center gap-2 px-2 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  <section.icon className="w-4 h-4" />
                  {section.title}
                </h3>
                <ul className="space-y-1 mt-1">
                  {section.pages.map((page, j) => (
                    <li key={j}>
                      <Link
                        href={page.href}
                        className="block px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        {page.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>

          <div className="p-4 border-t border-gray-100 dark:border-gray-700">
            <Link href="/docs/contributing" className="block px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <ChevronRight className="w-4 h-4 inline mr-2" />
              Contributing
            </Link>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col ml-0 lg:ml-72">
        <header className="sticky top-0 z-30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Menu className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="hidden lg:flex p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {showSidebar ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Documentation</h1>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link href="https://github.com/ele-agent/ele-agent" target="_blank" rel="noopener noreferrer" className="btn-ghost">
                <Code className="w-4 h-4 mr-2" />
                GitHub
              </Link>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          {search && filteredResults.length > 0 ? (
            <div className="p-8 max-w-3xl mx-auto">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Search Results</h1>
              <p className="text-gray-600 dark:text-gray-400 mb-8">{filteredResults.length} results for "{search}"</p>
              <ul className="space-y-4">
                {filteredResults.map((result, i) => (
                  <li key={i} className="card p-6 hover:shadow-lg transition-shadow">
                    <Link href={result.href} className="block">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">{result.title}</h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{result.section}</p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="p-8 max-w-5xl mx-auto">
              <div className="mb-12 text-center">
                <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">ELE Agent Documentation</h1>
                <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                  Comprehensive guides, API reference, and tutorials for building with ELE Agent.
                  Choose a section from the sidebar or search above.
                </p>
              </div>

              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {DOCS_SECTIONS.map((section, i) => (
                  <Link key={i} href={section.pages[0].href} className="card p-6 hover:shadow-lg hover:border-primary-200 dark:hover:border-primary-800 transition-all group">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`p-3 rounded-xl bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400 group-hover:scale-110 transition-transform`}>
                        <section.icon className="w-6 h-6" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{section.title}</h3>
                    </div>
                    <ul className="space-y-2">
                      {section.pages.slice(0, 3).map((page, j) => (
                        <li key={j} className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                          {page.title}
                        </li>
                      ))}
                      {section.pages.length > 3 && (
                        <li className="text-sm text-primary-600 dark:text-primary-400 font-medium">
                          +{section.pages.length - 3} more pages
                        </li>
                      )}
                    </ul>
                  </Link>
                ))}
              </div>

              <div className="mt-16 p-8 bg-primary-50 dark:bg-primary-900/30 rounded-2xl text-center">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Want to Contribute?</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-xl mx-auto">
                  Help improve these docs! Fix typos, add examples, or write new guides.
                </p>
                <Link href="/docs/contributing" className="btn bg-primary-600 text-white hover:bg-primary-700">
                  View Contributing Guide
                  <ChevronRight className="ml-2 w-4 h-4" />
                </Link>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}