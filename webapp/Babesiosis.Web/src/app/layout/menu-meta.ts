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
}

/**
 * Every navigation item in the application, in render order. The menu is a
 * single flat list: `isTitle` items are section headings, everything else is
 * a link.
 */
export const MENU: MenuItem[] = [
  {
    key: 'literature-review',
    icon: 'clipboard-check',
    label: 'Literature Review',
    link: '/literature-review',
  },
  {
    key: 'reference-articles',
    icon: 'article',
    label: 'Reference Articles',
    link: '/reference-articles',
  },
  {
    key: 'system',
    label: 'System',
    isTitle: true,
  },
  {
    key: 'help',
    icon: 'help-circle',
    label: 'Help & Support',
    link: '/help',
  },
]
