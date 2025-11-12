import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LogOut, Upload as UploadIcon, Key, BarChart3, Settings } from 'lucide-react'
import UploadTab from '@/components/dashboard/UploadTab'
import APIKeysTab from '@/components/dashboard/APIKeysTab'
import AnalyticsTab from '@/components/dashboard/AnalyticsTab'
import BotSettingsTab from '@/components/dashboard/BotSettingsTab'

export default function Dashboard() {
  const navigate = useNavigate()
  const { session, user, loading, signOut } = useAuthStore()
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    if (!session && !loading) {
      navigate('/')
    }
  }, [session, loading, navigate])

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Setting up your workspace...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-blue-900 bg-clip-text">
              Weaver
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <Button
                onClick={handleSignOut}
                variant="ghost"
                size="sm"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-8">
            <TabsTrigger value="upload">
              <UploadIcon className="w-4 h-4 mr-2" />
              Upload Documents
            </TabsTrigger>
            <TabsTrigger value="keys">
              <Key className="w-4 h-4 mr-2" />
              API Keys
            </TabsTrigger>
            <TabsTrigger value="settings">
              <Settings className="w-4 h-4 mr-2" />
              Bot Settings
            </TabsTrigger>
            <TabsTrigger value="analytics">
              <BarChart3 className="w-4 h-4 mr-2" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <Card>
              <CardContent className="pt-6">
                <UploadTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keys">
            <Card>
              <CardContent className="pt-6">
                <APIKeysTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardContent className="pt-6">
                <BotSettingsTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardContent className="pt-6">
                <AnalyticsTab tenantId={user.tenant_id} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

