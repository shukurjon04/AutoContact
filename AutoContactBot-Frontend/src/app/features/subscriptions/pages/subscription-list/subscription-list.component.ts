import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-subscription-list',
  templateUrl: './subscription-list.component.html',
  styleUrls: ['./subscription-list.component.scss']
})
export class SubscriptionListComponent implements OnInit {
  subscriptions: any[] = [];
  isLoading = true;
  currentPage = 1;
  totalItems = 0;
  pageSize = 20;
  statusFilter = '';

  constructor(private apiService: ApiService, private toastr: ToastrService) {}

  ngOnInit() {
    this.loadSubscriptions();
  }

  loadSubscriptions() {
    this.isLoading = true;
    const params: any = {};
    if (this.statusFilter) params.status = this.statusFilter;

    this.apiService.getSubscriptions(this.currentPage, params).subscribe({
      next: (res) => {
        this.subscriptions = res.results || [];
        this.totalItems = res.count || 0;
        this.isLoading = false;
      },
      error: () => {
        this.toastr.error('Failed to load subscriptions');
        this.isLoading = false;
      }
    });
  }

  onPageChange(page: number) {
    this.currentPage = page;
    this.loadSubscriptions();
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadSubscriptions();
  }

  cancelSubscription(sub: any) {
    if (!confirm('Are you sure you want to cancel this subscription?')) return;

    this.apiService.cancelSubscription(sub.id, 'Cancelled by admin').subscribe({
      next: () => {
        this.toastr.success('Subscription cancelled');
        sub.status = 'cancelled';
      },
      error: () => this.toastr.error('Failed to cancel subscription')
    });
  }

  calculateDaysLeft(endDateString: string): number {
    if (!endDateString) return 0;
    const endDate = new Date(endDateString);
    const today = new Date();
    const diffTime = endDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }
}
