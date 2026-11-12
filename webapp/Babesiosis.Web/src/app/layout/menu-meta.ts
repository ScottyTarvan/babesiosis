export type MenuItem = {
  key?: string
  label?: string
  /** Tabler icon name consumed by `<fs-symbol>` (e.g. `chart-pie`). */
  icon?: string
  link?: string
  isTitle?: boolean
  badge?: any
  disabled?: boolean
  /** When true, the item is only shown to administrators (filtered in the sidebar). */
  adminOnly?: boolean
  /** When true, the item is only shown to super administrators (filtered in the sidebar).
   *  The matching routes are also protected by SuperAdminRoleGuard. */
  superAdminOnly?: boolean
  /** When true, only shown outside production (mirrors a dev-only route — see app-routing.module.ts). */
  devOnly?: boolean
  /** When true, the item is not shown; its route still works by URL. */
  hidden?: boolean
}

/**
 * Every navigation item in the application, in render order. The menu is a
 * single flat list: `isTitle` items are section headings, everything else is
 * a link.
 */
export const MENU: MenuItem[] = [
  {
    key: 'home',
    icon: 'home',
    label: 'Overview',
    link: '/home',
  },
  {
    key: 'topics',
    icon: 'report-analytics',
    label: 'Topics',
    link: '/topics',
  },
  {
    key: 'gaps',
    icon: 'list-search',
    label: 'Gaps and questions',
    link: '/gaps',
  },
  {
    key: 'reference-articles',
    icon: 'article',
    label: 'Reference Articles',
    link: '/reference-articles',
  },
  {
    key: 'experiments',
    icon: 'chart-dots-3',
    label: 'Experiments',
    link: '/experiments',
  },
  {
    key: 'clinical',
    icon: 'checkup-list',
    label: 'Clinical',
    link: '/clinical',
  },
  {
    key: 'ai-agent',
    icon: 'sparkles',
    label: 'AI Agent',
    link: '/ai-agent',
  },
]
