import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChannelListComponent } from './pages/channel-list/channel-list.component';

const routes: Routes = [
  { path: '', component: ChannelListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ChannelsRoutingModule {}
