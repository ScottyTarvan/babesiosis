import { TestBed } from '@angular/core/testing';
import { MemberRoleGuard } from '@core/guards/member-role.guard';
import { AuthService } from 'app/core/services/auth.service';
import { Router } from '@angular/router';

describe('MemberRoleGuard', () => {
  let guard: MemberRoleGuard;
  let authStub: any;
  let routerStub: any;

  beforeEach(() => {
    authStub = {
      isAuthenticated: true,
      logout: jasmine.createSpy('logout')
    };
    routerStub = { navigate: jasmine.createSpy('navigate') };

    TestBed.configureTestingModule({
      providers: [
        MemberRoleGuard,
        { provide: AuthService, useValue: authStub },
        { provide: Router, useValue: routerStub }
      ]
    });

    guard = TestBed.inject(MemberRoleGuard);
  });

  it('allows authenticated user', () => {
    expect(guard.canActivate({} as any, {} as any)).toBeTrue();
    expect(authStub.logout).not.toHaveBeenCalled();
  });

  it('blocks and logs out unauthenticated user', () => {
    authStub.isAuthenticated = false;

    expect(guard.canActivate({} as any, {} as any)).toBeFalse();
    expect(authStub.logout).toHaveBeenCalled();
  });
});
