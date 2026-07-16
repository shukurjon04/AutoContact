import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';

import { LayoutComponent } from '@core/components/layout/layout.component';

const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then((m) => m.AuthModule),
  },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./features/dashboard/dashboard.module').then((m) => m.DashboardModule),
      },
      {
        path: 'channels',
        loadChildren: () => import('./features/channels/channels.module').then((m) => m.ChannelsModule),
      },
      {
        path: 'tariffs',
        loadChildren: () => import('./features/tariffs/tariffs.module').then((m) => m.TariffsModule),
      },
      {
        path: 'subscriptions',
        loadChildren: () => import('./features/subscriptions/subscriptions.module').then((m) => m.SubscriptionsModule),
      },
      {
        path: 'users',
        loadChildren: () => import('./features/users/users.module').then((m) => m.UsersModule),
      },
      {
        path: 'payments',
        loadChildren: () => import('./features/payments/payments.module').then((m) => m.PaymentsModule),
      },
      {
        path: 'broadcasts',
        loadChildren: () => import('./features/broadcasts/broadcasts.module').then((m) => m.BroadcastsModule),
      }
    ]
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
