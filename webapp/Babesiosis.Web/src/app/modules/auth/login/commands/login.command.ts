/** Body of `auth-password-login`. Mirrors `PasswordLoginCommand` on the backend. */
export class LoginCommand {
  constructor(public email: string,
    public password: string) { }
}
