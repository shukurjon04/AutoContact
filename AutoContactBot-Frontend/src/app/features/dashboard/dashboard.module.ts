import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { DashboardRoutingModule } from './dashboard-routing.module';

import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { StatsCardComponent } from './components/stats-card/stats-card.component';
import { RevenueChartComponent } from './components/revenue-chart/revenue-chart.component';

@NgModule({
  declarations: [
    DashboardComponent,
    StatsCardComponent,
    RevenueChartComponent
  ],
  imports: [SharedModule, DashboardRoutingModule],
})
export class DashboardModule {}
