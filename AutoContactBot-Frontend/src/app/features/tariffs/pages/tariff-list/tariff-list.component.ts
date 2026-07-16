import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-tariff-list',
  templateUrl: './tariff-list.component.html',
  styleUrls: ['./tariff-list.component.scss']
})
export class TariffListComponent implements OnInit {
  tariffs: any[] = [];
  isLoading = true;

  constructor(private apiService: ApiService, private toastr: ToastrService) {}

  ngOnInit() {
    this.loadTariffs();
  }

  loadTariffs() {
    this.apiService.getTariffs().subscribe({
      next: (res) => {
        this.tariffs = res.results || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.toastr.error('Failed to load tariffs');
      }
    });
  }

  deleteTariff(tariff: any) {
    if (!confirm(`Are you sure you want to delete ${tariff.name}?`)) return;

    this.apiService.deleteTariff(tariff.id).subscribe({
      next: () => {
        this.toastr.success('Tariff deleted successfully');
        this.loadTariffs();
      },
      error: () => this.toastr.error('Failed to delete tariff')
    });
  }
}
