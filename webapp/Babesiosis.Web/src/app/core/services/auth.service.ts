import { EventEmitter, Injectable, Output } from '@angular/core';
import { Router } from '@angular/router';
import { LoginViewModel } from 'app/modules/auth/login/viewmodels/login.viewmodel';
import { UserViewModel } from 'app/core/viewmodels/user.viewmodel';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  userSubject = new BehaviorSubject<UserViewModel>(this.user);
  user$ = this.userSubject.asObservable();

  constructor(private router: Router) {
  }

  set authToken(token: string) {
    localStorage.setItem('jwtToken', token);
  }

  get authToken(): string {
    return localStorage.getItem('jwtToken');
  }

  set user(user: UserViewModel) {
    localStorage.setItem('user', JSON.stringify(user));
  }

  get user(): UserViewModel {
    const raw = localStorage.getItem('user');
    if (!raw || raw === 'null') return null;
    return new UserViewModel(JSON.parse(raw));
  }

  set isAuthenticated(value: boolean) {
    localStorage.setItem('isLoggedIn', value ? 'true' : 'false');
  }

  get isAuthenticated(): boolean {
    return localStorage.getItem('isLoggedIn') === 'true';
  }

  @Output() notifyLogin = new EventEmitter();
  @Output() notifyLogout = new EventEmitter();

  saveLogin(login: LoginViewModel) {
    this.user = new UserViewModel(login.user);
    this.authToken = login.authToken;
    this.isAuthenticated = true;
    this.notifyLogin.emit();
    this.userSubject.next(this.user);
  }

  logout(returnUrl: string = null) {
    const theme = localStorage.getItem('theme');

    localStorage.removeItem('jwtToken');
    localStorage.removeItem('user');
    localStorage.removeItem('isLoggedIn');

    if (theme) {
      localStorage.setItem('theme', theme);
    }

    this.user = null;
    this.authToken = null;
    this.isAuthenticated = false;
    this.notifyLogout.emit();
    this.userSubject.next(null);

    // `returnUrl` is the same param name the login page reads back, so the
    // round trip actually lands the user where they were headed.
    if (returnUrl) {
      this.router.navigate(['/login'], { queryParams: { returnUrl } });
    } else {
      this.router.navigate(['/login']);
    }
  }
}
