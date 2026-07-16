import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { ChannelsRoutingModule } from './channels-routing.module';
import { ChannelListComponent } from './pages/channel-list/channel-list.component';

@NgModule({
  declarations: [ChannelListComponent],
  imports: [SharedModule, ChannelsRoutingModule],
})
export class ChannelsModule {}
