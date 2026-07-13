import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { AuthService } from './services/auth.service';
import { ApiService } from './services/api.service';
import { NotificationService } from './services/notification.service';
import { AuthGuard } from './guards/auth.guard';

@NgModule({
  imports: [CommonModule, HttpClientModule],
  providers: [
    AuthService,
    ApiService,
    NotificationService,
    AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
  ],
})
export class CoreModule {}
