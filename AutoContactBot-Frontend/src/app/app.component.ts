import { Component, OnInit } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'AutoContactBot Admin Panel';

  constructor(private translate: TranslateService) {}

  ngOnInit() {
    // Set default language to Uzbek
    this.translate.setDefaultLang('uz');
    this.translate.use('uz');
  }
}
