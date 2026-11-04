import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { ThemeService } from '@core/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: false,
  templateUrl: './app.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'Basecamp';

  constructor(private themeService: ThemeService) {}

  ngOnInit(): void {
    // Theme is already applied by ThemeService constructor
  }
}
