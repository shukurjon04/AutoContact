import { NgModule } from '@angular/core';
import { SharedModule } from '@shared/shared.module';
import { DashboardRoutingModule } from './dashboard-routing.module';

@NgModule({
  imports: [SharedModule, DashboardRoutingModule],
})
export class DashboardModule {}
