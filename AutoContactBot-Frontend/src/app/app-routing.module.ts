import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then((m) => m.AuthModule),
  },
  {
    path: 'dashboard',
    loadChildren: () => import('./features/dashboard/dashboard.module').then((m) => m.DashboardModule),
    canActivate: [AuthGuard],
  },
  {
    path: 'channels',
    loadChildren: () => import('./features/channels/channels.module').then((m) => m.ChannelsModule),
    canActivate: [AuthGuard],
  },
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.module').then((m) => m.UsersModule),
    canActivate: [AuthGuard],
  },
  {
    path: 'payments',
    loadChildren: () => import('./features/payments/payments.module').then((m) => m.PaymentsModule),
    canActivate: [AuthGuard],
  },
  {
    path: 'broadcasts',
    loadChildren: () => import('./features/broadcasts/broadcasts.module').then((m) => m.BroadcastsModule),
    canActivate: [AuthGuard],
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { enableTracing: false })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
