import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private languageSubject = new BehaviorSubject<string>('en');
  language$ = this.languageSubject.asObservable();

  get currentLanguage(): string {
    return this.languageSubject.value;
  }

  setLanguage(lang: string) {
    this.languageSubject.next(lang);
  }
}
