import { Routes } from '@angular/router';
import { Map } from './pages/map/map';
import { Videos } from './pages/videos/videos';
import { Pictures } from './pages/pictures/pictures';
import { Gear } from './pages/gear/gear';
import { Impressum } from './pages/impressum/impressum';
import { Privacypolicy } from './pages/privacypolicy/privacypolicy';

export const routes: Routes = [
    { path: '', component: Map },
    // { path: 'impressum', component: Impressum },
    // { path: 'privacy_policy', component: Privacypolicy },
    { path: 'videos', component: Videos },
    { path: 'pictures', component: Pictures },
    { path: 'gear', component: Gear },
];
