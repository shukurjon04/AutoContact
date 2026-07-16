import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { SubscriptionsRoutingModule } from './subscriptions-routing.module';
import { SubscriptionListComponent } from './pages/subscription-list/subscription-list.component';

@NgModule({
  declarations: [SubscriptionListComponent],
  imports: [SharedModule, SubscriptionsRoutingModule],
})
export class SubscriptionsModule {}
