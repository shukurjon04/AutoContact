/**
 * Core Models — API Response Types
 */

export interface AuthToken {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface TelegramUser {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_bot_blocked: boolean;
  is_active: boolean;
  language_code: string;
  registered_at: string;
  updated_at: string;
  active_subscriptions_count?: number;
}

export interface Tariff {
  id: number;
  channel: number;
  name: string;
  duration_days: number;
  price: number;
  final_price: number;
  price_tiyin: number;
  discount_percent: number;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Channel {
  id: number;
  name: string;
  telegram_id: number;
  username: string;
  description: string;
  is_active: boolean;
  bot_is_admin: boolean;
  created_at: string;
  updated_at: string;
  tariffs?: Tariff[];
  subscribers_count?: number;
  revenue_uzs?: number;
}

export interface Subscription {
  id: string;
  user: TelegramUser | number;
  channel: Channel | number;
  tariff: number;
  status: 'active' | 'expired' | 'cancelled';
  start_date: string;
  end_date: string;
  is_active: boolean;
  remaining_days: number;
  reminder_sent: string;
  extended_by_admin: boolean;
  admin_note?: string;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  user: TelegramUser | number;
  channel: Channel | number;
  tariff: number;
  amount: number;
  amount_uzs: number;
  status: 'pending' | 'paid' | 'cancelled' | 'failed';
  created_at: string;
  paid_at?: string;
  cancelled_at?: string;
  cancel_reason?: number;
  receipt_image?: string;
}

export interface Broadcast {
  id: number;
  text: string;
  photo?: string;
  target_type: 'all' | 'channel' | 'expiring';
  target_channel?: number;
  expiring_days?: number;
  status: 'draft' | 'in_progress' | 'completed' | 'failed';
  total_count: number;
  sent_count: number;
  failed_count: number;
  progress_percent?: number;
  created_by: string;
  created_at: string;
  sent_at?: string;
}

export interface DashboardStats {
  active_subscribers: number;
  monthly_revenue_uzs: number;
  today_revenue_uzs: number;
  expiring_7d: number;
  stale_pending: number;
  total_users: number;
  total_channels: number;
}

export interface PaymentSettings {
  card_number: string;
  card_owner: string;
}

export interface ApiResponse<T> {
  count?: number;
  next?: string;
  previous?: string;
  results?: T[];
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
