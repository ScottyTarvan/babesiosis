import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private isDarkModeSubject: BehaviorSubject<boolean>;
  isDarkMode$: Observable<boolean>;

  constructor(@Inject(PLATFORM_ID) private linkedServiceId: Object) {
    const initialTheme = this.getInitialTheme();
    this.isDarkModeSubject = new BehaviorSubject<boolean>(initialTheme);
    this.isDarkMode$ = this.isDarkModeSubject.asObservable();
    this.applyTheme(initialTheme);
  }

  private getInitialTheme(): boolean {
    if (isPlatformBrowser(this.linkedServiceId)) {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
        return savedTheme === 'dark';
      }
    }
    return false;
  }

  toggleTheme(): void {
    const newValue = !this.isDarkModeSubject.value;
    this.isDarkModeSubject.next(newValue);
    this.applyTheme(newValue);
    localStorage.setItem('theme', newValue ? 'dark' : 'light');
  }

  private applyTheme(isDark: boolean): void {
    if (!isPlatformBrowser(this.linkedServiceId)) {
      return;
    }
    const body = document.body;
    if (isDark) {
      body.classList.add('dark-theme');
      body.classList.remove('light-theme');
    } else {
      body.classList.add('light-theme');
      body.classList.remove('dark-theme');
    }
    document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
  }

  get isDarkMode(): boolean {
    return this.isDarkModeSubject.value;
  }
}
