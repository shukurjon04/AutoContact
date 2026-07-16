import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-payment-list',
  templateUrl: './payment-list.component.html',
  styleUrls: ['./payment-list.component.scss']
})
export class PaymentListComponent implements OnInit {
  transactions: any[] = [];
  isLoading = true;
  currentPage = 1;
  totalItems = 0;
  pageSize = 20;

  constructor(private apiService: ApiService, private toastr: ToastrService) {}

  ngOnInit() {
    this.loadTransactions();
  }

  loadTransactions() {
    this.isLoading = true;
    this.apiService.getTransactions(this.currentPage).subscribe({
      next: (res) => {
        this.transactions = res.results || [];
        this.totalItems = res.count || 0;
        this.isLoading = false;
      },
      error: () => {
        this.toastr.error('Failed to load transactions');
        this.isLoading = false;
      }
    });
  }

  onPageChange(page: number) {
    this.currentPage = page;
    this.loadTransactions();
  }

  approveTransaction(tx: any) {
    if (!confirm('Approve this payment?')) return;
    this.apiService.approveTransaction(tx.id).subscribe({
      next: () => {
        this.toastr.success('Payment approved');
        tx.status = 'completed';
      },
      error: () => this.toastr.error('Failed to approve payment')
    });
  }

  rejectTransaction(tx: any) {
    const reason = prompt('Enter rejection reason:');
    if (reason === null) return;
    this.apiService.rejectTransaction(tx.id, reason).subscribe({
      next: () => {
        this.toastr.success('Payment rejected');
        tx.status = 'failed';
      },
      error: () => this.toastr.error('Failed to reject payment')
    });
  }
}
