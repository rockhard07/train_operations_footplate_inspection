'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { type SidebarItem, type UserRole, getFilteredSidebar } from '@/lib/rbac'
import {
    LayoutDashboard, Users, List, UserCircle, Train, ClipboardCheck,
    BarChart3, MessageCircle, FileText, Radio, Building2, FileBarChart,
    FileCheck, PieChart, TrendingUp, ChevronDown, ChevronRight, Menu, X, LogOut,
    ShieldCheck, UserCog, KeyRound, Key, CalendarDays, ShieldAlert, UserPlus,
} from 'lucide-react'

const iconMap: Record<string, React.ElementType> = {
    LayoutDashboard, Users, List, UserCircle, Train, ClipboardCheck,
    BarChart3, MessageCircle, FileText, Radio, Building2, FileBarChart,
    FileCheck, PieChart, TrendingUp, ShieldCheck, UserCog, KeyRound, Key,
    CalendarDays, ShieldAlert, UserPlus,
}

interface SidebarProps {
    userRole: UserRole
    userDepartment?: string
    userName: string
    userEmail: string
    userDesignation?: string
}

export function Sidebar({ userRole, userDepartment, userName, userEmail }: SidebarProps) {
    const pathname = usePathname()
    const [mobileOpen, setMobileOpen] = useState(false)
    const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

    const menuItems = getFilteredSidebar(userRole, userDepartment)

    function toggleGroup(label: string) {
        setExpandedGroups((prev) => {
            const next = new Set(prev)
            if (next.has(label)) next.delete(label)
            else next.add(label)
            return next
        })
    }

    function isActive(href?: string) {
        if (!href) return false
        return pathname === href || pathname.startsWith(href + '/')
    }

    function renderItem(item: SidebarItem, depth = 0) {
        const Icon = iconMap[item.icon] || FileText
        const hasChildren = item.children && item.children.length > 0
        const isExpanded = expandedGroups.has(item.label)
        const active = isActive(item.href)

        // Auto-expand if a child is active
        const childActive = item.children?.some((c) => isActive(c.href))

        if (hasChildren) {
            const open = isExpanded || childActive
            return (
                <li key={item.label}>
                    <button
                        onClick={() => toggleGroup(item.label)}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors hover:bg-slate-800 ${childActive ? 'text-red-400' : 'text-slate-300'
                            }`}
                    >
                        <Icon className="h-4 w-4 shrink-0" />
                        <span className="flex-1 text-left">{item.label}</span>
                        {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </button>
                    {open && (
                        <ul className="ml-4 mt-1 space-y-0.5 border-l border-slate-700 pl-2">
                            {item.children!.map((child) => renderItem(child, depth + 1))}
                        </ul>
                    )}
                </li>
            )
        }

        return (
            <li key={item.label}>
                <Link
                    href={item.href || '#'}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${active
                        ? 'bg-red-600/20 text-red-400 border-l-2 border-red-500'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                        }`}
                >
                    <Icon className="h-4 w-4 shrink-0" />
                    <span>{item.label}</span>
                </Link>
            </li>
        )
    }

    const sidebarContent = (
        <>
            {/* Brand */}
            <div className="p-4 border-b border-slate-800 flex items-center gap-3">
                <img src="/images/deutsche-bahn-logo.png" alt="DB" className="h-8 w-8 object-contain" />
                <div>
                    <h2 className="text-lg font-bold text-white">Operations</h2>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">DB RRTS</p>
                </div>
            </div>

            {/* User Info */}
            <div className="px-4 py-3 border-b border-slate-800">
                <p className="text-sm font-semibold text-white truncate">{userName}</p>
                <p className="text-xs text-slate-400 truncate">{userEmail}</p>
                <span className="inline-block mt-1 px-2 py-0.5 bg-red-600/20 text-red-400 text-[10px] font-bold uppercase rounded">
                    {userRole}
                </span>
            </div>

            {/* Nav Items */}
            <nav className="flex-1 overflow-y-auto p-3">
                <ul className="space-y-1">
                    {menuItems.map((item) => renderItem(item))}
                </ul>
            </nav>

            {/* Logout */}
            <div className="p-3 border-t border-slate-800">
                <form action="/auth/signout" method="post">
                    <button
                        type="submit"
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-600/10 transition-colors"
                    >
                        <LogOut className="h-4 w-4" />
                        <span>Sign Out</span>
                    </button>
                </form>
            </div>
        </>
    )

    return (
        <>
            {/* Mobile Toggle */}
            <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden fixed top-4 left-4 z-50 bg-slate-900 text-white p-2 rounded-lg shadow-lg"
            >
                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {/* Mobile Overlay */}
            {mobileOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black/50 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed md:sticky top-0 left-0 z-40 h-screen w-64 bg-slate-900 text-white flex flex-col
          transition-transform duration-300
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
            >
                {sidebarContent}
            </aside>
        </>
    )
}
