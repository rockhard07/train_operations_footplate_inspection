import { createClient } from '@/utils/supabase/server'
import { ForcePasswordRedirect } from '@/components/force-password-redirect'
import { redirect } from 'next/navigation'
import { Sidebar } from '@/components/sidebar'
import type { UserRole } from '@/lib/rbac'

export default async function ProtectedLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const supabase = await createClient()
    const { data: { user }, error } = await supabase.auth.getUser()

    if (error || !user) {
        redirect('/')
    }

    // Fetch user profile from custom users table
    const { data: profile } = await supabase
        .from('users')
        .select('full_name, role, employee_id, force_password_change')
        .eq('id', user.id)
        .single()

    // Fetch employee details directly from employees table using employee_id
    const { data: empData } = profile?.employee_id
        ? await supabase.from('employees').select('name, designation, role, department').eq('employee_id', profile.employee_id).single()
        : { data: null }

    const userRole = (empData?.role?.toLowerCase() || profile?.role?.toLowerCase() || 'employee') as UserRole
    const userDesignation = empData?.designation || profile?.role || 'User'
    const userDepartment = empData?.department || ''
    const userName = empData?.name || profile?.full_name || user.email || 'User'
    const userEmail = user.email || ''

    return (
        <div className="min-h-screen bg-gray-50 flex print:block print:bg-white print:min-h-0">
            <ForcePasswordRedirect force={!!profile?.force_password_change} />
            <Sidebar userRole={userRole} userDepartment={userDepartment} userName={userName} userEmail={userEmail} userDesignation={userDesignation} />
            <main className="flex-1 flex flex-col min-h-screen overflow-x-hidden md:ml-0 print:block print:min-h-0 print:overflow-visible">
                <header className="bg-white shadow-sm border-b px-6 py-4 flex justify-between items-center sticky top-0 z-10 print:hidden">
                    <div>
                        <h1 className="text-lg font-semibold text-slate-800">Operations (DB RRTS)</h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-500 hidden sm:inline">{userName}</span>
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold uppercase rounded">
                            {userDesignation}
                        </span>
                    </div>
                </header>
                <div className="flex-1 p-6 print:p-0">
                    {children}
                </div>
            </main>
        </div>
    )
}
