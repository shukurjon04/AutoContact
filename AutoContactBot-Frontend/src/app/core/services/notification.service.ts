import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root',
})
export class NotificationService {
  constructor(private toastr: ToastrService) {}

  success(message: string, title: string = 'Muvaffaqiyat'): void {
    this.toastr.success(message, title, {
      timeOut: 3000,
      positionClass: 'toast-top-right',
    });
  }

  error(message: string, title: string = 'Xatolik'): void {
    this.toastr.error(message, title, {
      timeOut: 5000,
      positionClass: 'toast-top-right',
    });
  }

  warning(message: string, title: string = 'Ogohlantirish'): void {
    this.toastr.warning(message, title, {
      timeOut: 4000,
      positionClass: 'toast-top-right',
    });
  }

  info(message: string, title: string = 'Ma\'lumot'): void {
    this.toastr.info(message, title, {
      timeOut: 3000,
      positionClass: 'toast-top-right',
    });
  }
}
