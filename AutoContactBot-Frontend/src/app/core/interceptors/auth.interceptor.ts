import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private auth: AuthService,
    private notification: NotificationService
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip interceptor for token requests
    if (request.url.includes('/auth/token/')) {
      return next.handle(request);
    }

    const token = this.auth.getAccessToken();
    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Token expired, try to refresh
          const refreshToken = this.auth.getRefreshToken();
          if (refreshToken) {
            return this.auth.refreshToken().pipe(
              switchMap(() => {
                // Retry request with new token
                const newToken = this.auth.getAccessToken();
                request = request.clone({
                  setHeaders: {
                    Authorization: `Bearer ${newToken}`,
                  },
                });
                return next.handle(request);
              }),
              catchError(() => {
                this.auth.logout();
                return throwError(() => error);
              })
            );
          } else {
            this.auth.logout();
          }
        } else if (error.status === 403) {
          this.notification.error('Sizda bu amalni bajarishga ruxsat yo\'q', 'Ruxsat kerak');
        } else if (error.status >= 500) {
          this.notification.error('Server xatosi. Iltimos keyinroq qayta urinib ko\'ring', 'Server xatosi');
        }

        return throwError(() => error);
      })
    );
  }
}
