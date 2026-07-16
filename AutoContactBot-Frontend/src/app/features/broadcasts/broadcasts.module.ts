import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { BroadcastsRoutingModule } from './broadcasts-routing.module';
import { BroadcastListComponent } from './pages/broadcast-list/broadcast-list.component';

@NgModule({
  declarations: [BroadcastListComponent],
  imports: [SharedModule, BroadcastsRoutingModule],
})
export class BroadcastsModule {}
