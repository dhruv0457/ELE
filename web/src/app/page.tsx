import Link from 'next/link'
import { Bot, Sparkles, Terminal, Mic, Shield, Globe, ArrowRight, CheckCircle, Zap } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-900">
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Global">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <Link href="/" className="flex items-center gap-2">
                <Bot className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                <span className="text-xl font-bold text-gray-900 dark:text-gray-100">ELE Agent</span>
              </Link>
            </div>
            <div className="hidden md:flex md:items-center md:gap-8">
              <Link href="#features" className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">Features</Link>
              <Link href="#demo" className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">Demo</Link>
              <Link href="/docs" className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">Docs</Link>
              <Link href="/pricing" className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400">Pricing</Link>
            </div>
            <div className="hidden md:flex md:items-center md:gap-4">
              <Link href="/login" className="btn-ghost text-sm">Sign in</Link>
              <Link href="/signup" className="btn-primary text-sm">Get Started</Link>
            </div>
          </div>
        </nav>
      </header>

      <main>
        <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 xl:pb-36">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1 text-sm font-medium text-primary-700 dark:bg-primary-900/30 dark:text-primary-300 mb-6">
                <Zap className="h-4 w-4" />
                <span>Now with Parallel LLM Orchestration</span>
              </div>
              <h1 className="text-5xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-7xl mb-6">
                Control Your Computer with{' '}
                <span className="text-primary-600 dark:text-primary-400">Natural Language</span>
              </h1>
              <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300 mb-10">
                ELE Agent is a unified AI desktop assistant that combines OpenAI, Gemini, Local LLMs, and OpenClaw
                into a single intelligent agent. Control files, browser, shell, and more through voice, text, or API.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                <Link href="/signup" className="btn-primary w-full sm:w-auto">
                  Download for Free
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
                <Link href="#demo" className="btn-secondary w-full sm:w-auto">Watch Demo</Link>
              </div>
              <div className="flex items-center justify-center gap-8 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-2"><CheckCircle className="h-4 w-4" />Open Source (MIT)</div>
                <div className="flex items-center gap-2"><CheckCircle className="h-4 w-4" />Runs Offline</div>
                <div className="flex items-center gap-2"><CheckCircle className="h-4 w-4" />Privacy First</div>
              </div>
            </div>

            <div className="mt-20 relative">
              <div className="absolute inset-0 bg-gradient-to-t from-white dark:from-gray-900 to-transparent z-10 h-32 bottom-0 top-auto" />
              <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-2xl overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                  </div>
                  <div className="flex-1 text-center text-sm text-gray-500 dark:text-gray-400 font-mono">ele-agent: chat "Create a React dashboard"</div>
                </div>
                <div className="p-6 font-mono text-sm text-gray-100 bg-gray-950 overflow-x-auto">
                  <div className="text-green-400 mb-2"> ele chat "Create a React dashboard with charts"</div>
                  <div className="text-gray-500 mb-1">�� Analyzing request...</div>
                  <div className="text-gray-500 mb-1">�� Planning approach...</div>
                  <div className="text-gray-500 mb-1">�� Creating files...</div>
                  <div className="text-blue-400 mb-2">��� Created Dashboard.tsx with Recharts</div>
                  <div className="text-blue-400 mb-2">��� Created useDashboardData hook</div>
                  <div className="text-blue-400 mb-2">��� Added to routing</div>
                  <div className="text-green-400">��� Done! Running at localhost:3000</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="py-20 lg:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">Four Interfaces, One Agent</h2>
              <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300">
                Use ELE Agent however you prefer - web, desktop, terminal, or Telegram
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <FeatureCard
                icon={Globe}
                title="Web App"
                description="Full-featured Next.js dashboard with real-time chat, marketplace, settings, and analytics."
                features={["Real-time streaming", "Supabase auth", "Marketplace", "Analytics"]}
              />
              <FeatureCard
                icon={Bot}
                title="Desktop App"
                description="Electron + React app with system tray, global hotkeys, overlay, and native notifications."
                features={["System tray", "Global hotkeys", "Voice overlay", "Auto-updates"]}
              />
              <FeatureCard
                icon={Terminal}
                title="CLI / TUI"
                description="Textual-based terminal UI with live agent thoughts, tool execution, and keyboard shortcuts."
                features={["Live thoughts", "Keyboard-driven", "Scriptable", "SSH friendly"]}
              />
              <FeatureCard
                icon={Mic}
                title="Telegram Bot"
                description="Chat with ELE Agent from anywhere. Send commands, get results, receive notifications."
                features={["Remote access", "Notifications", "File sharing", "Voice messages"]}
              />
            </div>
          </div>
        </section>

        <section className="py-20 lg:py-32 bg-gray-50 dark:bg-gray-900/50">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">Powered by Parallel LLMs</h2>
              <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300">
                Query multiple LLM providers simultaneously and merge the best responses automatically.
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              <ProviderCard name="OpenAI" models={["GPT-4o", "GPT-4 Turbo", "GPT-3.5"]} color="text-green-600" />
              <ProviderCard name="Google Gemini" models={["Gemini 1.5 Pro", "Gemini 1.5 Flash"]} color="text-blue-600" />
              <ProviderCard name="Local (Ollama)" models={["Llama 3", "Mistral", "CodeLlama"]} color="text-purple-600" />
              <ProviderCard name="OpenClaw" models={["OpenClaw v1", "Custom models"]} color="text-orange-600" />
              <ProviderCard name="Anthropic" models={["Claude 3.5 Sonnet", "Claude 3 Opus"]} color="text-yellow-600" />
              <ProviderCard name="Auto Mode" models={["Smart routing", "Cost optimization", "Fallback"]} color="text-primary-600" />
            </div>
          </div>
        </section>

        <section id="demo" className="py-20 lg:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">What Can ELE Do?</h2>
              <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300">
                From coding to automation, ELE Agent handles complex multi-step tasks.
              </p>
            </div>
            <div className="space-y-8">
              <DemoItem
                title="Code Generation & Refactoring"
                description="Create, edit, and refactor code across your entire codebase. Run tests, lint, and deploy."
                commands={["ele chat \"Create a FastAPI auth module\"", "ele chat \"Add tests for user service\"", "ele chat \"Refactor to use dependency injection\""]}
              />
              <DemoItem
                title="File & Project Management"
                description="Organize files, create project structures, batch rename, convert formats, and more."
                commands={["ele chat \"Organize my downloads folder\"", "ele chat \"Create React project structure\"", "ele chat \"Convert all .md to .txt\""]}
              />
              <DemoItem
                title="Web Automation & Research"
                description="Browse, scrape, fill forms, take screenshots, and extract data from any website."
                commands={["ele chat \"Scrape pricing from competitor sites\"", "ele chat \"Fill out this job application\"", "ele chat \"Monitor this page for changes\""]}
              />
              <DemoItem
                title="System Administration"
                description="Run commands, manage services, monitor resources, and automate DevOps tasks."
                commands={["ele chat \"Restart nginx and check logs\"", "ele chat \"Show disk usage by folder\"", "ele chat \"Setup cron job for backups\""]}
              />
            </div>
          </div>
        </section>

        <section className="py-20 lg:py-32 bg-primary-600">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">Ready to Get Started?</h2>
            <p className="mx-auto max-w-2xl text-lg text-primary-100 mb-8">
              Download ELE Agent free and start automating your workflow today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup" className="btn bg-white text-primary-600 hover:bg-primary-50 w-full sm:w-auto">
                Download for Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link href="/docs" className="btn border-2 border-white text-white hover:bg-primary-700 w-full sm:w-auto">
                Read Documentation
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <Link href="/" className="flex items-center gap-2 mb-4">
                <Bot className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                <span className="text-xl font-bold text-gray-900 dark:text-gray-100">ELE Agent</span>
              </Link>
              <p className="text-sm text-gray-600 dark:text-gray-400">Unified AI Desktop Assistant</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link href="/features" className="hover:text-primary-600 dark:hover:text-primary-400">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-primary-600 dark:hover:text-primary-400">Pricing</Link></li>
                <li><Link href="/docs" className="hover:text-primary-600 dark:hover:text-primary-400">Documentation</Link></li>
                <li><Link href="/marketplace" className="hover:text-primary-600 dark:hover:text-primary-400">Marketplace</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link href="/blog" className="hover:text-primary-600 dark:hover:text-primary-400">Blog</Link></li>
                <li><Link href="/community" className="hover:text-primary-600 dark:hover:text-primary-400">Community</Link></li>
                <li><Link href="/api" className="hover:text-primary-600 dark:hover:text-primary-400">API Reference</Link></li>
                <li><Link href="/status" className="hover:text-primary-600 dark:hover:text-primary-400">Status</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link href="/about" className="hover:text-primary-600 dark:hover:text-primary-400">About</Link></li>
                <li><Link href="/careers" className="hover:text-primary-600 dark:hover:text-primary-400">Careers</Link></li>
                <li><Link href="/privacy" className="hover:text-primary-600 dark:hover:text-primary-400">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-primary-600 dark:hover:text-primary-400">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>© 2024 ELE Agent. Open source under MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon: Icon, title, description, features }: { icon: React.ComponentType<any>, title: string, description: string, features: string[] }) {
  return (
    <div className="card p-6 hover:shadow-lg transition-shadow">
      <div className="h-12 w-12 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-4">
        <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300 mb-4">{description}</p>
      <ul className="space-y-1">
        {features.map((f, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <CheckCircle className="h-4 w-4 text-primary-500" />
            {f}
          </li>
        ))}
      </ul>
    </div>
  )
}

function ProviderCard({ name, models, color }: { name: string, models: string[], color: string }) {
  return (
    <div className="card p-6">
      <h3 className={`font-semibold text-lg ${color} mb-3`}>{name}</h3>
      <ul className="space-y-1">
        {models.map((m, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <CheckCircle className="h-4 w-4" style={{ color: 'currentColor' }} />
            {m}
          </li>
        ))}
      </ul>
    </div>
  )
}

function DemoItem({ title, description, commands }: { title: string, description: string, commands: string[] }) {
  return (
    <div className="card p-6 lg:p-8">
      <div className="lg:grid lg:grid-cols-3 lg:gap-8">
        <div className="lg:col-span-1">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
          <p className="text-gray-600 dark:text-gray-300">{description}</p>
        </div>
        <div className="lg:col-span-2 mt-4 lg:mt-0">
          <div className="bg-gray-950 rounded-lg p-4 font-mono text-sm text-gray-100 overflow-x-auto">
            {commands.map((cmd, i) => (
              <div key={i} className="flex gap-2">
                <span className="text-green-400">$</span>
                <span className="text-blue-300">ele</span>
                <span className="text-gray-300">{cmd.replace('ele chat ', '')}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}