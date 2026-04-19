import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withHashLocation } from '@angular/router';

import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { languageInterceptor } from './interceptors/language.interceptor';
import { apiBaseUrlInterceptor } from './interceptors/api-base-url.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes, withHashLocation()), provideClientHydration(withEventReplay()),
    provideHttpClient(
      withFetch(),
      withInterceptors([apiBaseUrlInterceptor, languageInterceptor])
    )
  ]
};
