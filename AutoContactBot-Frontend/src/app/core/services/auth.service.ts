import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '@env/environment';
import { AuthToken, User } from '../models';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.checkAuth();
  }

  login(username: string, password: string): Observable<AuthToken> {
    return this.http
      .post<AuthToken>(`${environment.apiUrl}/auth/token/`, {
        username,
        password,
      })
      .pipe(
        tap((response) => {
          this.setTokens(response);
          this.getCurrentUser().subscribe();
        }),
        catchError((error) => {
          console.error('Login error:', error);
          return throwError(() => error);
        })
      );
  }

  refreshToken(): Observable<AuthToken> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http
      .post<AuthToken>(`${environment.apiUrl}/auth/token/refresh/`, {
        refresh: refreshToken,
      })
      .pipe(
        tap((response) => {
          this.setTokens(response);
        }),
        catchError((error) => {
          this.logout();
          return throwError(() => error);
        })
      );
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me/`).pipe(
      tap((user) => {
        this.currentUserSubject.next(user);
        this.isAuthenticatedSubject.next(true);
      }),
      catchError((error) => {
        this.logout();
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    this.clearTokens();
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/auth/login']);
  }

  private checkAuth(): void {
    const token = this.getAccessToken();
    if (token) {
      this.isAuthenticatedSubject.next(true);
      this.getCurrentUser().subscribe();
    }
  }

  private setTokens(response: AuthToken): void {
    localStorage.setItem(environment.tokenKey, response.access);
    localStorage.setItem(environment.refreshTokenKey, response.refresh);
  }

  private clearTokens(): void {
    localStorage.removeItem(environment.tokenKey);
    localStorage.removeItem(environment.refreshTokenKey);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(environment.tokenKey);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(environment.refreshTokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}
