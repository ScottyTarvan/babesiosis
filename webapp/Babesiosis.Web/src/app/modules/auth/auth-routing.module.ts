import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from 'app/modules/auth/login/login.component';

const routes: Routes = [
  {
    path: '',
    component: LoginComponent,
    data: { returnUrl: window.location.pathname },
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AuthRoutingModule { }
