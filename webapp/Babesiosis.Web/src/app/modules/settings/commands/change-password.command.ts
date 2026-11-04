export class ChangePasswordCommand {
  constructor(public currentPassword: string,
    public newPassword: string,
    public confirmPassword: string) { }
}
