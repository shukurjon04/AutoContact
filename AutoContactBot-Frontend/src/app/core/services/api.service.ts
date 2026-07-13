import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@env/environment';
import {
  TelegramUser,
  Channel,
  Tariff,
  Subscription,
  Transaction,
  Broadcast,
  DashboardStats,
  PaymentSettings,
  PaginatedResponse,
} from '../models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(private http: HttpClient) {}

  // ===== USERS =====
  getUsers(page: number = 1, params?: any): Observable<PaginatedResponse<TelegramUser>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<TelegramUser>>(
      `${environment.apiUrl}/users/`,
      { params: httpParams }
    );
  }

  getUser(id: number): Observable<TelegramUser> {
    return this.http.get<TelegramUser>(`${environment.apiUrl}/users/${id}/`);
  }

  updateUser(id: number, data: Partial<TelegramUser>): Observable<TelegramUser> {
    return this.http.patch<TelegramUser>(`${environment.apiUrl}/users/${id}/`, data);
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/users/${id}/`);
  }

  blockUser(id: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/users/${id}/block/`, {});
  }

  unblockUser(id: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/users/${id}/unblock/`, {});
  }

  // ===== CHANNELS =====
  getChannels(page: number = 1, params?: any): Observable<PaginatedResponse<Channel>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Channel>>(
      `${environment.apiUrl}/channels/`,
      { params: httpParams }
    );
  }

  getChannel(id: number): Observable<Channel> {
    return this.http.get<Channel>(`${environment.apiUrl}/channels/${id}/`);
  }

  createChannel(data: any): Observable<Channel> {
    return this.http.post<Channel>(`${environment.apiUrl}/channels/`, data);
  }

  updateChannel(id: number, data: any): Observable<Channel> {
    return this.http.patch<Channel>(`${environment.apiUrl}/channels/${id}/`, data);
  }

  deleteChannel(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/channels/${id}/`);
  }

  deactivateChannel(id: number): Observable<any> {
    return this.http.post(`${environment.apiUrl}/channels/${id}/deactivate/`, {});
  }

  // ===== TARIFFS =====
  getTariffs(page: number = 1, params?: any): Observable<PaginatedResponse<Tariff>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Tariff>>(
      `${environment.apiUrl}/tariffs/`,
      { params: httpParams }
    );
  }

  getTariff(id: number): Observable<Tariff> {
    return this.http.get<Tariff>(`${environment.apiUrl}/tariffs/${id}/`);
  }

  createTariff(data: any): Observable<Tariff> {
    return this.http.post<Tariff>(`${environment.apiUrl}/tariffs/`, data);
  }

  updateTariff(id: number, data: any): Observable<Tariff> {
    return this.http.patch<Tariff>(`${environment.apiUrl}/tariffs/${id}/`, data);
  }

  deleteTariff(id: number): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/tariffs/${id}/`);
  }

  // ===== SUBSCRIPTIONS =====
  getSubscriptions(page: number = 1, params?: any): Observable<PaginatedResponse<Subscription>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Subscription>>(
      `${environment.apiUrl}/subscriptions/`,
      { params: httpParams }
    );
  }

  getSubscription(id: string): Observable<Subscription> {
    return this.http.get<Subscription>(`${environment.apiUrl}/subscriptions/${id}/`);
  }

  createSubscription(data: any): Observable<Subscription> {
    return this.http.post<Subscription>(`${environment.apiUrl}/subscriptions/`, data);
  }

  extendSubscription(id: string, days: number, note: string = ''): Observable<Subscription> {
    return this.http.post<Subscription>(
      `${environment.apiUrl}/subscriptions/${id}/extend/`,
      { days, note }
    );
  }

  cancelSubscription(id: string, reason: string = ''): Observable<any> {
    return this.http.post(`${environment.apiUrl}/subscriptions/${id}/cancel/`, { reason });
  }

  // ===== TRANSACTIONS =====
  getTransactions(page: number = 1, params?: any): Observable<PaginatedResponse<Transaction>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Transaction>>(
      `${environment.apiUrl}/transactions/`,
      { params: httpParams }
    );
  }

  getTransaction(id: string): Observable<Transaction> {
    return this.http.get<Transaction>(`${environment.apiUrl}/transactions/${id}/`);
  }

  approveTransaction(id: string): Observable<Transaction> {
    return this.http.post<Transaction>(
      `${environment.apiUrl}/transactions/${id}/approve/`,
      {}
    );
  }

  rejectTransaction(id: string, reason: string = ''): Observable<Transaction> {
    return this.http.post<Transaction>(
      `${environment.apiUrl}/transactions/${id}/reject/`,
      { reason }
    );
  }

  getTransactionStats(): Observable<any> {
    return this.http.get(`${environment.apiUrl}/transactions/stats/`);
  }

  // ===== BROADCASTS =====
  getBroadcasts(page: number = 1, params?: any): Observable<PaginatedResponse<Broadcast>> {
    let httpParams = new HttpParams().set('page', page.toString());
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }
    return this.http.get<PaginatedResponse<Broadcast>>(
      `${environment.apiUrl}/broadcasts/`,
      { params: httpParams }
    );
  }

  getBroadcast(id: number): Observable<Broadcast> {
    return this.http.get<Broadcast>(`${environment.apiUrl}/broadcasts/${id}/`);
  }

  createBroadcast(data: any): Observable<Broadcast> {
    return this.http.post<Broadcast>(`${environment.apiUrl}/broadcasts/`, data);
  }

  launchBroadcast(id: number): Observable<Broadcast> {
    return this.http.post<Broadcast>(`${environment.apiUrl}/broadcasts/${id}/launch/`, {});
  }

  getBroadcastRecipients(id: number, page: number = 1): Observable<any> {
    return this.http.get(
      `${environment.apiUrl}/broadcasts/${id}/recipients/`,
      { params: new HttpParams().set('page', page.toString()) }
    );
  }

  // ===== DASHBOARD =====
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${environment.apiUrl}/dashboard/stats/`);
  }

  // ===== SETTINGS =====
  getPaymentSettings(): Observable<PaymentSettings> {
    return this.http.get<PaymentSettings>(`${environment.apiUrl}/payment-settings/`);
  }

  updatePaymentSettings(data: PaymentSettings): Observable<PaymentSettings> {
    return this.http.put<PaymentSettings>(`${environment.apiUrl}/payment-settings/`, data);
  }
}
