export const basePath: string = '/'

/**
 * The landing page: the shell's own '' redirect sends every visitor here. The
 * (currently unrouted) password login and SSO callback read it too, so the
 * three can't drift apart if sign-in returns.
 */
export const homeUrl: string = '/home'
