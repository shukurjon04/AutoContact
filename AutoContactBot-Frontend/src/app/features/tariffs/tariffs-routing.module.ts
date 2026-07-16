import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TariffListComponent } from './pages/tariff-list/tariff-list.component';

const routes: Routes = [
  { path: '', component: TariffListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class TariffsRoutingModule {}
