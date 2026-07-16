import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BroadcastListComponent } from './pages/broadcast-list/broadcast-list.component';

const routes: Routes = [
  { path: '', component: BroadcastListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class BroadcastsRoutingModule {}
