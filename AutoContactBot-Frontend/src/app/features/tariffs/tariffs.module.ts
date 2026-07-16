import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { TariffsRoutingModule } from './tariffs-routing.module';
import { TariffListComponent } from './pages/tariff-list/tariff-list.component';

@NgModule({
  declarations: [TariffListComponent],
  imports: [SharedModule, TariffsRoutingModule],
})
export class TariffsModule {}
