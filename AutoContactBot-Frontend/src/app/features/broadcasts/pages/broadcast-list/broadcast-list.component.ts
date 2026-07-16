import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-broadcast-list',
  templateUrl: './broadcast-list.component.html',
  styleUrls: ['./broadcast-list.component.scss']
})
export class BroadcastListComponent implements OnInit {
  broadcasts: any[] = [];
  isLoading = true;

  constructor(private apiService: ApiService, private toastr: ToastrService) {}

  ngOnInit() {
    this.loadBroadcasts();
  }

  loadBroadcasts() {
    this.isLoading = true;
    this.apiService.getBroadcasts().subscribe({
      next: (res) => {
        this.broadcasts = res.results || [];
        this.isLoading = false;
      },
      error: () => {
        this.toastr.error('Failed to load broadcasts');
        this.isLoading = false;
      }
    });
  }

  launchBroadcast(bc: any) {
    if (!confirm('Are you sure you want to launch this broadcast?')) return;
    this.apiService.launchBroadcast(bc.id).subscribe({
      next: () => {
        this.toastr.success('Broadcast launched successfully');
        this.loadBroadcasts();
      },
      error: () => this.toastr.error('Failed to launch broadcast')
    });
  }
}
