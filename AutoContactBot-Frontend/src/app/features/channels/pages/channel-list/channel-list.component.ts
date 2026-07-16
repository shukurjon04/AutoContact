import { Component, OnInit } from '@angular/core';
import { ApiService } from '@core/services/api.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-channel-list',
  template: `
    <div class="channels-container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="text-white mb-0">Channel Management</h3>
        <button class="btn btn-primary d-flex align-items-center">
          <i class="bi bi-plus-lg me-2"></i> Add Channel
        </button>
      </div>

      <div class="glass-card p-0 overflow-hidden" *ngIf="!isLoading">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th class="ps-4">Channel</th>
                <th>Telegram ID</th>
                <th>Status</th>
                <th>Subscribers</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let ch of channels" class="animate-fade-in">
                <td class="ps-4">
                  <div class="d-flex align-items-center">
                    <div class="channel-icon me-3">
                      <i class="bi bi-megaphone"></i>
                    </div>
                    <div>
                      <div class="text-white fw-semibold">{{ ch.title }}</div>
                      <small class="text-muted">{{ ch.description || 'No description' }}</small>
                    </div>
                  </div>
                </td>
                <td><code class="text-primary">{{ ch.telegram_id }}</code></td>
                <td>
                  <span class="badge rounded-pill px-3 py-1" [ngClass]="ch.is_active ? 'bg-success' : 'bg-danger'">
                    {{ ch.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="text-muted">{{ ch.subscribers_count || 0 }}</td>
                <td class="text-end pe-4">
                  <div class="btn-group">
                    <button class="btn btn-sm btn-glass" (click)="deactivateChannel(ch)" *ngIf="ch.is_active" title="Deactivate"><i class="bi bi-pause-circle text-warning"></i></button>
                    <button class="btn btn-sm btn-glass" (click)="deleteChannel(ch)" title="Delete"><i class="bi bi-trash text-danger"></i></button>
                  </div>
                </td>
              </tr>
              <tr *ngIf="channels.length === 0">
                <td colspan="5" class="text-center py-5 text-muted">
                  <i class="bi bi-megaphone fs-1 d-block mb-2"></i>
                  No channels found. Click "Add Channel" to get started.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div *ngIf="isLoading" class="d-flex justify-content-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
    </div>
  `,
  styles: [`
    .channel-icon {
      width: 40px; height: 40px; border-radius: 50%;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      display: flex; align-items: center; justify-content: center;
      color: white; font-size: 1rem;
      box-shadow: 0 4px 10px rgba(14,165,233,0.25);
    }
    code { background: rgba(139,92,246,0.1); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.85rem; }
  `]
})
export class ChannelListComponent implements OnInit {
  channels: any[] = [];
  isLoading = true;

  constructor(private apiService: ApiService, private toastr: ToastrService) {}

  ngOnInit() {
    this.apiService.getChannels().subscribe({
      next: (res) => { this.channels = res.results || []; this.isLoading = false; },
      error: () => { this.isLoading = false; }
    });
  }

  deactivateChannel(ch: any) {
    this.apiService.deactivateChannel(ch.id).subscribe({
      next: () => { ch.is_active = false; this.toastr.success('Channel deactivated'); },
      error: () => this.toastr.error('Failed to deactivate channel')
    });
  }

  deleteChannel(ch: any) {
    if (!confirm('Delete this channel?')) return;
    this.apiService.deleteChannel(ch.id).subscribe({
      next: () => { this.channels = this.channels.filter(c => c.id !== ch.id); this.toastr.success('Channel deleted'); },
      error: () => this.toastr.error('Failed to delete channel')
    });
  }
}
