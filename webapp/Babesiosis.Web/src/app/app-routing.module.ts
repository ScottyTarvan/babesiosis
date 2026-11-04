import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";

// The application has no sign-in for now: every route is open and anything
// unknown (old /login and /logout links included) lands on the shell's default
// page. The auth module (login, password
// reset, SSO callback, logout) and AuthGuard are left in place, unrouted, so
// sign-in can be restored by adding those routes and the guard back.
const routes: Routes = [
  //{
  //  path: 'error',
  //  loadChildren: () =>
  //    import('./modules/errors/errors.module').then((m) => m.ErrorsModule),
  //},
  {
    path: '',
    loadChildren: () =>
      import('@layouts/layout.module').then((m) => m.LayoutModule),
  },
  { path: '**', redirectTo: '' }
];
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
