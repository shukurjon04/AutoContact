import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-stats-card',
  template: `
    <div class="glass-card p-4 h-100">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <p class="text-muted small fw-bold text-uppercase letter-spacing-1 mb-2">{{ title }}</p>
          <h3 class="text-white mb-0 font-weight-bold">{{ value | number }}</h3>
        </div>
        <div class="icon-box d-flex align-items-center justify-content-center rounded" [ngClass]="colorClass + '-bg-subtle'">
          <i class="bi fs-4" [ngClass]="[icon, colorClass]"></i>
        </div>
      </div>
      <div class="mt-3" *ngIf="trend">
        <span class="small badge rounded-pill" [ngClass]="trend.startsWith('+') ? 'badge-success-subtle text-success' : 'badge-danger-subtle text-danger'">
          <i class="bi" [ngClass]="trend.startsWith('+') ? 'bi-arrow-up-right' : 'bi-arrow-down-right'"></i> {{ trend }}
        </span>
        <span class="text-muted small ms-2">vs last month</span>
      </div>
    </div>
  `,
  styles: [`
    .icon-box {
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.05);
    }
    .text-primary-bg-subtle { background: rgba(79, 70, 229, 0.15); }
    .text-success-bg-subtle { background: rgba(16, 185, 129, 0.15); }
    .text-warning-bg-subtle { background: rgba(245, 158, 11, 0.15); }
    .text-danger-bg-subtle { background: rgba(239, 68, 68, 0.15); }
    
    .badge-success-subtle { background: rgba(16, 185, 129, 0.15); }
    .badge-danger-subtle { background: rgba(239, 68, 68, 0.15); }
    .letter-spacing-1 { letter-spacing: 1px; }
  `]
})
export class StatsCardComponent {
  @Input() title: string = '';
  @Input() value: number | string = 0;
  @Input() icon: string = '';
  @Input() colorClass: string = '';
  @Input() trend?: string;
}
