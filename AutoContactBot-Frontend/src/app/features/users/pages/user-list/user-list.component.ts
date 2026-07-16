import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss']
})
export class UserListComponent implements OnInit {
  users: any[] = [];
  isLoading = true;
  currentPage = 1;
  totalItems = 0;
  pageSize = 20;
  searchQuery = '';
  statusFilter = '';

  constructor(
    private apiService: ApiService,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.isLoading = true;
    const params: any = {};
    if (this.searchQuery) params.search = this.searchQuery;
    if (this.statusFilter) params.is_blocked = this.statusFilter === 'blocked';

    this.apiService.getUsers(this.currentPage, params).subscribe({
      next: (response) => {
        this.users = response.results || [];
        this.totalItems = response.count || 0;
        this.isLoading = false;
      },
      error: () => {
        this.toastr.error('Failed to load users');
        this.isLoading = false;
      }
    });
  }

  onSearch() {
    this.currentPage = 1;
    this.loadUsers();
  }

  onPageChange(page: number) {
    this.currentPage = page;
    this.loadUsers();
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadUsers();
  }

  blockUser(user: any) {
    if (!confirm(`Are you sure you want to block ${user.first_name || user.telegram_id}?`)) return;

    this.apiService.blockUser(user.id).subscribe({
      next: () => {
        this.toastr.success('User blocked successfully');
        user.is_blocked = true;
      },
      error: () => this.toastr.error('Failed to block user')
    });
  }

  unblockUser(user: any) {
    this.apiService.unblockUser(user.id).subscribe({
      next: () => {
        this.toastr.success('User unblocked successfully');
        user.is_blocked = false;
      },
      error: () => this.toastr.error('Failed to unblock user')
    });
  }

  deleteUser(user: any) {
    if (!confirm(`Are you sure you want to DELETE ${user.first_name || user.telegram_id}? This action cannot be undone.`)) return;

    this.apiService.deleteUser(user.id).subscribe({
      next: () => {
        this.toastr.success('User deleted successfully');
        this.loadUsers();
      },
      error: () => this.toastr.error('Failed to delete user')
    });
  }
}
