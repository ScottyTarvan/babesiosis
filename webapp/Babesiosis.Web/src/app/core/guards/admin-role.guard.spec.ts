import { TestBed } from '@angular/core/testing';
import { AdminRoleGuard } from '@core/guards/admin-role.guard';
import { AuthService } from 'app/core/services/auth.service';
import { Router } from '@angular/router';

describe('AdminRoleGuard', () => {
  let guard: AdminRoleGuard;
  let authStub: any;
  let routerStub: any;

  beforeEach(() => {
    authStub = {
      isAuthenticated: true,
      user: { isAdministrator: true },
      logout: jasmine.createSpy('logout')
    };
    routerStub = { navigate: jasmine.createSpy('navigate') };

    TestBed.configureTestingModule({
      providers: [
        AdminRoleGuard,
        { provide: AuthService, useValue: authStub },
        { provide: Router, useValue: routerStub }
      ]
    });

    guard = TestBed.inject(AdminRoleGuard);
  });

  it('allows authenticated admin user', () => {
    expect(guard.canActivate({} as any, {} as any)).toBeTrue();
    expect(authStub.logout).not.toHaveBeenCalled();
  });

  it('blocks and logs out unauthenticated user', () => {
    authStub.isAuthenticated = false;

    expect(guard.canActivate({} as any, {} as any)).toBeFalse();
    expect(authStub.logout).toHaveBeenCalled();
  });
});
