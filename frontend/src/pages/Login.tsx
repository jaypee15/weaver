import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { supabase } from '@/lib/supabase'
import { Button } from '../components/ui/button'

export default function Login() {
  const navigate = useNavigate()
  const { session, loading } = useAuthStore()
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  const handleGoogleLogin = async () => {
    setIsAuthenticating(true)
    const redirectUrl = `${window.location.origin}/auth/callback`
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: redirectUrl,
      },
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
          <div className="text-slate-400">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] pointer-events-none"></div>
      
      {/* Gradient orbs */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[120px] animate-pulse"></div>
      <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[120px] animate-pulse delay-1000"></div>

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center font-bold">
              W
            </div>
            <span className="text-xl font-semibold">Weaver</span>
          </div>
          <Button 
            onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
            disabled={isAuthenticating}
            variant="outline" 
            className="bg-blue-900 hover:bg-blue-500 text-white hover:text-white"
          >
            {isAuthenticating ? 'Redirecting...' : session ? 'Go to Dashboard' : 'Sign In'}
          </Button>
        </nav>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 pt-20 pb-32">
          <div className="text-center max-w-4xl mx-auto">
            {/* Floating badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700 mb-8 animate-fade-in">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-300">Powered by Gemini + LangChain</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
              Turn Your Business Knowledge Into an{' '}
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-gradient">
                AI Support Bot
              </span>
            </h1>
            
            <p className="text-xl text-slate-400 mb-4 max-w-3xl mx-auto leading-relaxed">
              Upload your docs. Get a custom AI that answers your customers — instantly.
            </p>
            
            <p className="text-lg text-slate-500 mb-12 max-w-2xl mx-auto">
              Weaver takes your PDFs, manuals, and help guides and turns them into an intelligent customer-service bot. 
              <span className="text-slate-400"> No training, coding, or prompt engineering required.</span>
            </p>

            {/* CTA */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button 
                onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
                disabled={isAuthenticating}
                size="lg"
                className="bg-blue-900 hover:bg-slate-900 text-white shadow-lg shadow-blue-500/30 text-lg px-8 h-14 group"
              >
                {isAuthenticating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mr-3"></div>
                    Redirecting to Google...
                  </>
                ) : session ? (
                  <>
                    Go to Dashboard
                    <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Get Started with Google
                    <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                )}
              </Button>
              <div className="text-sm text-slate-500">
                {session ? 'Welcome back!' : 'Free to start • No credit card required'}
              </div>
            </div>

            {/* Social proof */}
            <div className="mt-16 flex items-center justify-center gap-8 text-slate-600 text-sm">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Secure & Private</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 7H7v6h6V7z" />
                  <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                </svg>
                <span>Sub-2s Response</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Built on GCP</span>
              </div>
            </div>
          </div>
        </section>

        {/* Built for Businesses Section */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">
                Built for Businesses That <span className="text-blue-400">Live in Their Docs</span>
              </h2>
              <p className="text-lg text-slate-400 mb-6 leading-relaxed">
                Your company already has all the answers — in PDFs, Word files, FAQs, and internal wikis.
              </p>
              <p className="text-lg text-slate-300 leading-relaxed">
                Weaver reads them, understands them, and builds a private AI assistant that speaks your brand's voice.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {['PDF', 'DOCX', 'TXT', 'HTML'].map((format, i) => (
                <div 
                  key={format}
                  className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-blue-500/50 transition-all duration-300 hover:scale-105"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <div className="text-3xl mb-2">📄</div>
                  <div className="text-xl font-semibold">{format}</div>
                  <div className="text-sm text-slate-500 mt-1">Supported</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="max-w-7xl mx-auto px-6 py-32">
          <h2 className="text-5xl font-bold text-center mb-20">
            How It <span className="text-blue-500">Works</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { 
                step: '01', 
                icon: '📤', 
                title: 'Upload your documents', 
                desc: 'PDFs, DOCX, TXT — drag and drop right into your dashboard.',
                color: 'blue'
              },
              { 
                step: '02', 
                icon: '🤖', 
                title: 'Weaver builds your bot', 
                desc: 'Your content is chunked, embedded, and indexed securely using Google Cloud + pgvector.',
                color: 'purple'
              },
              { 
                step: '03', 
                icon: '🚀', 
                title: 'Deploy anywhere', 
                desc: 'Get an API endpoint you can embed in your site, app, or internal tools.',
                color: 'pink'
              },
            ].map((item) => (
              <div 
                key={item.step}
                className="group relative p-8 rounded-2xl bg-slate-800/30 border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:-translate-y-2"
              >
                <div className="absolute top-4 right-4 text-6xl font-bold text-slate-800">{item.step}</div>
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="text-2xl font-bold mb-3">{item.title}</h3>
                <p className="text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Why Choose Weaver */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <h2 className="text-5xl font-bold text-center mb-20">
            Why Teams Choose <span className="text-blue-400">Weaver</span>
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '💬', title: 'Custom AI trained on your knowledge', desc: 'Every response is grounded in your actual content — not the open internet.' },
              { icon: '🔐', title: 'Secure, private, multi-tenant architecture', desc: 'Your data never mixes with anyone else\'s. Hosted entirely on Google Cloud with per-tenant isolation.' },
              { icon: '⚡', title: 'Blazing fast responses', desc: 'RAG pipeline built with LangChain + Gemini, optimized to answer in under 2 seconds.' },
              { icon: '🧩', title: 'Integrate anywhere', desc: 'Call your bot via REST API. Connect to your app, CRM, or customer portal in minutes.' },
              { icon: '📊', title: 'Built-in analytics', desc: 'See what customers are asking, where your docs fall short, and how your AI performs.' },
              { icon: '🔒', title: 'Security First', desc: 'Per-tenant isolation, AES-256 encryption, TLS 1.3, key rotation, and access control built-in.' },
            ].map((feature, i) => (
              <div 
                key={i}
                className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:bg-slate-800/80 transition-all duration-300"
              >
                <div className="text-4xl mb-3">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="max-w-7xl mx-auto px-6 py-32">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Under the Hood</h2>
            <p className="text-slate-400 text-lg">Enterprise-grade tech — without the enterprise complexity.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Google Gemini', tag: 'LLM' },
              { name: 'Postgres + pgvector', tag: 'Vector DB' },
              { name: 'Google Cloud Storage', tag: 'Storage' },
              { name: 'FastAPI', tag: 'Backend' },
              { name: 'React', tag: 'Frontend' },
              { name: 'Celery', tag: 'Workers' },
              { name: 'Supabase', tag: 'Auth' },
              { name: 'LangChain', tag: 'Framework' },
            ].map((tech) => (
              <div 
                key={tech.name}
                className="p-4 rounded-lg bg-slate-800/30 border border-slate-700 text-center hover:border-blue-500/50 transition-all duration-300"
              >
                <div className="font-semibold mb-1">{tech.name}</div>
                <div className="text-xs text-slate-500">{tech.tag}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Use Cases */}
        <section className="max-w-7xl mx-auto px-6 py-32 border-t border-slate-800">
          <h2 className="text-4xl font-bold text-center mb-16">Use Weaver For</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              'Customer support automation',
              'Internal knowledge assistants',
              'Product documentation Q&A',
              'HR & IT policy chatbots',
              'SaaS help centers',
              'Managed service FAQs',
            ].map((useCase, i) => (
              <div 
                key={i}
                className="p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-800/30 border border-slate-700 hover:border-slate-600 transition-all"
              >
                <div className="text-blue-400 mb-2">✓</div>
                <div className="text-lg">{useCase}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Example */}
        <section className="max-w-4xl mx-auto px-6 py-32">
          <div className="p-12 rounded-2xl bg-gradient-to-br from-blue-900/30 to-purple-900/30 border border-blue-500/30">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">It's Simple</h2>
            </div>
            <div className="space-y-4 text-lg">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📄</div>
                <div>
                  <div className="font-semibold mb-2">Upload your "Customer Support Manual.pdf"</div>
                  <div className="text-slate-400">↓</div>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="text-3xl">🤖</div>
                <div>
                  <div className="font-semibold mb-2">Weaver builds an AI bot that instantly knows:</div>
                  <div className="text-blue-400 italic">"What's your refund policy?"</div>
                  <div className="text-purple-400 italic">"How do I reset my password?"</div>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="text-3xl">✨</div>
                <div className="text-slate-300">
                  And answers accurately, <span className="text-green-400 font-semibold">24/7</span>.
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="max-w-4xl mx-auto px-6 py-32 text-center">
          <h2 className="text-5xl font-bold mb-6">
            Start Free. <span className="text-blue-500">Scale Securely.</span>
          </h2>
          <p className="text-xl text-slate-400 mb-12">
            Your business knowledge deserves an AI that actually knows your business.
          </p>
          <Button 
            onClick={session ? () => navigate('/dashboard') : handleGoogleLogin}
            disabled={isAuthenticating}
            size="lg"
            className="bg-blue-900 hover:bg-blue-500 text-white shadow-xl shadow-blue-500/30 text-xl px-12 h-16"
          >
            {isAuthenticating ? (
              <>
                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin mr-3"></div>
                Authenticating...
              </>
            ) : session ? (
              <>
                Go to Dashboard
                <svg className="w-6 h-6 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            ) : (
              <>
                Get Started with Weaver
                <svg className="w-6 h-6 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            )}
          </Button>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-800 py-12">
          <div className="max-w-7xl mx-auto px-6 text-center">
            <div className="text-2xl font-semibold mb-2">
              Weaver — weave your knowledge into intelligence.
            </div>
            <div className="text-slate-500 text-sm">
              © 2025 Weaver. Built with Gemini, LangChain, and ❤️
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

