import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loader2, Sparkles, Info, CheckCircle2 } from 'lucide-react'
import { useBotConfig, useGenerateSystemPrompt, useUpdateBotConfig } from '@/hooks/useBot'
import { toast } from 'sonner'

interface BotSettingsTabProps {
  tenantId: string
}

export default function BotSettingsTab({ tenantId }: BotSettingsTabProps) {
  const [businessInfo, setBusinessInfo] = useState({
    businessName: '',
    industry: '',
    description: '',
    tone: 'professional',
    primaryGoal: '',
    specialInstructions: '',
  })
  
  const [generatedPrompt, setGeneratedPrompt] = useState('')
  const [showPrompt, setShowPrompt] = useState(false)
  
  const { data: botConfig, isLoading: isLoadingConfig } = useBotConfig(tenantId)
  const generateMutation = useGenerateSystemPrompt(tenantId)
  const updateMutation = useUpdateBotConfig(tenantId)
  
  // Load existing configuration if available
  useEffect(() => {
    if (botConfig?.config?.system_prompt) {
      setGeneratedPrompt(botConfig.config.system_prompt)
      setShowPrompt(true)
    }
    if (botConfig?.config?.business_info) {
      const info = botConfig.config.business_info
      setBusinessInfo({
        businessName: info.business_name || '',
        industry: info.industry || '',
        description: info.description || '',
        tone: info.tone || 'professional',
        primaryGoal: info.primary_goal || '',
        specialInstructions: info.special_instructions || '',
      })
    }
  }, [botConfig])
  
  const isFormValid = 
    businessInfo.businessName.trim() &&
    businessInfo.industry.trim() &&
    businessInfo.description.trim() &&
    businessInfo.primaryGoal.trim()
  
  const handleGenerate = async () => {
    try {
      const result = await generateMutation.mutateAsync({
        businessName: businessInfo.businessName,
        industry: businessInfo.industry,
        description: businessInfo.description,
        tone: businessInfo.tone,
        primaryGoal: businessInfo.primaryGoal,
        specialInstructions: businessInfo.specialInstructions || undefined,
      })
      setGeneratedPrompt(result.system_prompt)
      setShowPrompt(true)
      toast.success('System prompt generated successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate prompt')
    }
  }
  
  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync({
        system_prompt: generatedPrompt,
        business_info: businessInfo,
      })
      toast.success('Bot configuration saved successfully!')
      // Don't clear the form - keep the saved configuration visible
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save configuration')
    }
  }
  
  if (isLoadingConfig) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    )
  }

  const hasExistingConfig = botConfig?.config?.system_prompt

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Configure Your Bot</h2>
        <p className="text-gray-600">
          Tell us about your business and we'll create the perfect bot personality
        </p>
      </div>

      {/* Current Configuration Status */}
      {hasExistingConfig && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-blue-900">Active Configuration</p>
                <p className="text-sm text-blue-700 mt-1">
                  Your bot currently has a custom system prompt. You can view it below or generate a new one.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            Business Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Business Name */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Business/Product Name *
            </label>
            <Input
              placeholder="e.g., Acme Corp, MyProduct"
              value={businessInfo.businessName}
              onChange={(e) => setBusinessInfo({...businessInfo, businessName: e.target.value})}
            />
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Industry *
            </label>
            <Input
              placeholder="e.g., SaaS, E-commerce, Healthcare, Legal"
              value={businessInfo.industry}
              onChange={(e) => setBusinessInfo({...businessInfo, industry: e.target.value})}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">
              What does your business do? *
            </label>
            <textarea
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={4}
              placeholder="Describe your business, products, or services in 2-3 sentences..."
              value={businessInfo.description}
              onChange={(e) => setBusinessInfo({...businessInfo, description: e.target.value})}
            />
          </div>

          {/* Tone Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Bot Personality *
            </label>
            <select
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={businessInfo.tone}
              onChange={(e) => setBusinessInfo({...businessInfo, tone: e.target.value})}
            >
              <option value="professional">Professional & Polished</option>
              <option value="friendly">Friendly & Conversational</option>
              <option value="technical">Technical & Precise</option>
              <option value="casual">Casual & Approachable</option>
              <option value="formal">Formal & Academic</option>
            </select>
          </div>

          {/* Primary Goal */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Primary Goal *
            </label>
            <Input
              placeholder="e.g., Answer customer support questions, Explain product features, Help with onboarding"
              value={businessInfo.primaryGoal}
              onChange={(e) => setBusinessInfo({...businessInfo, primaryGoal: e.target.value})}
            />
          </div>

          {/* Special Instructions (Optional) */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Special Instructions (Optional)
            </label>
            <textarea
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={3}
              placeholder="Any specific guidelines? e.g., 'Always include a disclaimer', 'Mention our 24/7 support', 'Use emojis'"
              value={businessInfo.specialInstructions}
              onChange={(e) => setBusinessInfo({...businessInfo, specialInstructions: e.target.value})}
            />
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">How it works</p>
              <p>We'll generate an optimal system prompt based on your business information. You can review and edit it before saving.</p>
            </div>
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!isFormValid || generateMutation.isPending}
            className="w-full"
            size="lg"
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Your Bot's Personality...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Bot Configuration
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Prompt Preview */}
      {showPrompt && generatedPrompt && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-900 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5" />
              System Prompt Generated
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-green-900">
                Preview (You can edit if needed)
              </label>
              <textarea
                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-sm bg-white"
                rows={10}
                value={generatedPrompt}
                onChange={(e) => setGeneratedPrompt(e.target.value)}
              />
            </div>

            <div className="flex gap-3">
              <Button 
                onClick={handleSave} 
                disabled={updateMutation.isPending}
                className="bg-green-600 hover:bg-green-700"
              >
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save & Activate Bot'
                )}
              </Button>
              
              <Button 
                variant="outline" 
                onClick={handleGenerate} 
                disabled={generateMutation.isPending || !isFormValid}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Regenerate
              </Button>
              
              <Button 
                variant="ghost" 
                onClick={() => setShowPrompt(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Examples Section */}
      {!showPrompt && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Example Use Cases</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="font-medium">SaaS Product Support</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Professional & Polished<br />
                <strong>Goal:</strong> Answer customer questions about features, pricing, and integrations
              </p>
            </div>
            
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="font-medium">E-commerce Store</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Friendly & Conversational<br />
                <strong>Goal:</strong> Help customers find products and answer shipping/return questions
              </p>
            </div>
            
            <div className="border-l-4 border-green-500 pl-4">
              <p className="font-medium">Technical Documentation</p>
              <p className="text-gray-600 mt-1">
                <strong>Tone:</strong> Technical & Precise<br />
                <strong>Goal:</strong> Provide accurate API documentation and code examples
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

