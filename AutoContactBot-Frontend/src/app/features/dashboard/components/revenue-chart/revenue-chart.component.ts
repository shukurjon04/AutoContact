import { Component, OnInit } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';

@Component({
  selector: 'app-revenue-chart',
  template: `
    <div class="glass-card p-4 h-100">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="text-white mb-0">Revenue Overview</h5>
        <div class="btn-group">
          <button class="btn btn-sm" [class.btn-primary]="period === '7d'" [class.btn-glass]="period !== '7d'" (click)="period = '7d'">7D</button>
          <button class="btn btn-sm" [class.btn-primary]="period === '30d'" [class.btn-glass]="period !== '30d'" (click)="period = '30d'">30D</button>
          <button class="btn btn-sm" [class.btn-primary]="period === '90d'" [class.btn-glass]="period !== '90d'" (click)="period = '90d'">90D</button>
        </div>
      </div>
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'line'">
      </canvas>
    </div>
  `,
  styles: [`
    :host { display: block; }
  `]
})
export class RevenueChartComponent implements OnInit {
  period = '30d';

  chartData: ChartData<'line'> = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Revenue (UZS)',
        data: [650000, 590000, 800000, 810000, 560000, 550000, 900000],
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#8b5cf6',
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: 'Subscribers',
        data: [280, 320, 350, 410, 390, 420, 480],
        borderColor: '#ec4899',
        backgroundColor: 'rgba(236, 72, 153, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointBackgroundColor: '#ec4899',
        pointBorderColor: '#ec4899',
        pointRadius: 4,
        pointHoverRadius: 6,
      }
    ]
  };

  chartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',
          usePointStyle: true,
          padding: 20,
          font: { family: 'Inter', size: 12 }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(24, 24, 27, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        titleColor: '#f8fafc',
        bodyColor: '#94a3b8',
        padding: 12,
        cornerRadius: 8,
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
      }
    }
  };

  ngOnInit() {}
}
