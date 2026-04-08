'use client'

import { useState } from 'react'
import { login } from '@/app/actions/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { BadgeCheck, Lock, User } from 'lucide-react'
import Image from 'next/image'

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)

    const formData = new FormData(event.currentTarget)
    const result = await login(formData)

    if (result?.error) {
      setError(result.error)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/50 p-4">
      <Card className="w-full max-w-md shadow-lg border-t-4 border-t-red-600">
        <CardHeader className="space-y-4 text-center pb-8 border-b border-gray-100">
          <div className="mx-auto bg-white p-2 flex justify-center w-[120px] h-[80px] relative">
            {/* Using standard img tag if Image component fails locally without next.config.js domains */}
            <img
              src="/images/deutsche-bahn-logo.png"
              alt="DB Logo"
              className="object-contain w-full h-full"
            />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">Operations</CardTitle>
            <CardDescription className="text-md font-medium text-gray-500">(DB RRTS)</CardDescription>
          </div>
        </CardHeader>

        <CardContent className="pt-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="sr-only">Email ID</Label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-400">
                  <User size={18} />
                </div>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Email ID"
                  required
                  className="pl-10 py-6 text-md bg-gray-50/50 focus-visible:bg-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="sr-only">Password</Label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-400">
                  <Lock size={18} />
                </div>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Password"
                  required
                  className="pl-10 py-6 text-md bg-gray-50/50 focus-visible:bg-white"
                />
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-md font-medium text-center">
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="w-full py-6 text-md bg-red-600 hover:bg-red-700 text-white font-semibold transition-colors"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 rounded-full border-2 border-white/20 border-t-white animate-spin" />
                  <span>Signing In...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between items-center bg-gray-50/50 px-6 py-4 border-t border-gray-100 mt-2">
          <div className="flex items-center text-xs text-gray-500 font-medium">
            <BadgeCheck size={14} className="mr-1 text-green-600" /> Secure Login
          </div>
          <span className="text-xs text-gray-400 font-medium tracking-wide">Ver 2.0</span>
        </CardFooter>
      </Card>
    </div>
  )
}
