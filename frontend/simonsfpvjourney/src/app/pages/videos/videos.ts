import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Category, Drone, Tag, Video, VideoFilter } from '../../models/video.model';
import { VideoService } from '../../services/video.service';
import { MetaService } from '../../services/meta.service';
import { FormsModule } from '@angular/forms';
import { Videomodal } from '../../popups/videomodal/videomodal';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-videos',
  standalone: true,
  imports: [ CommonModule, FormsModule, Videomodal, RouterModule ],
  templateUrl: './videos.html',
  styleUrl: './videos.css',
})
export class Videos {
  videos$!: Observable<Video[]>;
  videosSnapshot: Video[] = [];
  visibleVideosSnapshot: Video[] = [];
  selectedVideo$ = new BehaviorSubject<Video | null>(null);

  facetCounts: {
    categories: Partial<Record<string, number>>;
    tags: Partial<Record<number, number>>;
    drones: Partial<Record<string, number>>;
    seasons: Partial<Record<string, number>>;
    times: Partial<Record<string, number>>;
    weathers: Partial<Record<string, number>>;
    countries: Partial<Record<string, number>>;
  } = {
    categories: {},
    tags: {},
    drones: {},
    seasons: {},
    times: {},
    weathers: {},
    countries: {},
  };

  categories: Category[] = [];
  tags: Tag[] = [];
  drones: Drone[] = [];

  filter: VideoFilter = { order_by: 'views_current', order_dir: 'desc' };
  searchText: string = '';
  selectedTagToAdd: number | null = null;
  showAdvancedFilters = false;
  availableCountries: string[] = [];
  showSuggestions = false;
  
  // Search suggestions dropdown
  getSuggestions(): Array<{ label: string; type: 'Video' | 'Category' | 'Tag' | 'Drone' }> {
    const q = (this.searchText || '').trim().toLowerCase();
    const max = 12;
    const pool: Array<{ label: string; type: 'Video' | 'Category' | 'Tag' | 'Drone' }> = [];

    // Collect from videos, categories, tags, drones
    for (const v of this.videosSnapshot) {
      if (!v?.title) continue;
      const label = v.title;
      if (!q || label.toLowerCase().includes(q)) {
        pool.push({ label, type: 'Video' });
      }
    }
    for (const c of this.categories) {
      const label = c.name;
      if (!q || label.toLowerCase().includes(q)) {
        pool.push({ label, type: 'Category' });
      }
    }
    for (const t of this.tags) {
      const label = t.name;
      if (!q || label.toLowerCase().includes(q)) {
        pool.push({ label, type: 'Tag' });
      }
    }
    for (const d of this.drones) {
      const label = d.name;
      if (!q || label.toLowerCase().includes(q)) {
        pool.push({ label, type: 'Drone' });
      }
    }

    // Deduplicate by label, preserve first type encountered
    const seen = new Set<string>();
    const out: Array<{ label: string; type: 'Video' | 'Category' | 'Tag' | 'Drone' }> = [];
    for (const item of pool) {
      if (seen.has(item.label)) continue;
      seen.add(item.label);
      out.push(item);
      if (out.length >= max) break;
    }
    return out;
  }

  selectSuggestion(s: { label: string; type: string }): void {
    this.searchText = s.label;
    this.applyFilter();
    this.showSuggestions = false;
  }

  constructor(
    private videoService: VideoService,
    private metaService: MetaService
  ) {}

  ngOnInit(): void {
    // Load Categories, Tags, Drones
    this.metaService.getCategories().subscribe(c => this.categories = c);
    this.metaService.getTags().subscribe(t => this.tags = t);
    this.metaService.getDrones().subscribe(d => this.drones = d);

    // Videos laden
    this.videoService.loadVideos();

    // Set default sorting (views desc)
    this.videoService.setFilter(this.filter);

    // Observable für die Liste
    this.videos$ = this.videoService.filteredVideos$;
    this.videoService.filteredVideos$.subscribe(v => {
      this.visibleVideosSnapshot = v || [];
    });

    // Snapshot für Autocomplete
    this.videoService.videos$.subscribe(videos => {
      this.videosSnapshot = videos;
    });

    // Faceted counts
    this.videoService.facetCounts$.subscribe(c => {
      this.facetCounts = c ?? {
        categories: {},
        tags: {},
        drones: {},
        seasons: {},
        times: {},
        weathers: {},
        countries: {},
      };
      // Build available countries list with count > 0
      const countries = this.facetCounts.countries || {};
      this.availableCountries = Object.keys(countries).filter(k => k && k !== '__all__' && (countries[k] ?? 0) > 0);
    });
  }
  toggleAdvanced(): void {
    this.showAdvancedFilters = !this.showAdvancedFilters;
  }

  /** Filter anwenden */
  applyFilter(): void {
    this.videoService.setFilter({
      ...this.filter,
      search: this.searchText?.trim() || undefined
    });
  }

  onSearchInput(): void {
    this.showSuggestions = !!this.searchText && this.searchText.trim().length > 0;
    this.applyFilter();
  }

  /** Filter zurücksetzen */
  resetFilter(): void {
    this.filter = {};
    this.searchText = '';
    this.videoService.setFilter(null);
  }

  /** Video anklicken */
  onClick(video: Video): void {
    this.selectedVideo$.next(video);
  }

  getIndex(v: Video): number {
    return this.visibleVideosSnapshot.findIndex(x => x.id === v.id);
  }
  canPrev(v: Video): boolean {
    return this.getIndex(v) > 0;
  }
  canNext(v: Video): boolean {
    const i = this.getIndex(v);
    return i >= 0 && i < this.visibleVideosSnapshot.length - 1;
  }
  goPrev(v: Video): void {
    const i = this.getIndex(v);
    if (i > 0) this.selectedVideo$.next(this.visibleVideosSnapshot[i - 1]);
  }
  goNext(v: Video): void {
    const i = this.getIndex(v);
    if (i >= 0 && i < this.visibleVideosSnapshot.length - 1) this.selectedVideo$.next(this.visibleVideosSnapshot[i + 1]);
  }

  /** Tag-Card entfernen */
  removeTag(tagId: number): void {
    const tags = new Set<number>(this.filter.tags ?? []);
    tags.delete(tagId);
    this.filter.tags = Array.from(tags);
    this.applyFilter();
  }

  getTagName(tagId: number): string {
    return this.tags.find(t => t.id === tagId)?.name ?? String(tagId);
  }

  /** Tag aus Liste hinzufügen */
  addTag(): void {
    const tagId = this.selectedTagToAdd;
    if (tagId == null) return;
    const tags = new Set<number>(this.filter.tags ?? []);
    tags.add(tagId);
    this.filter.tags = Array.from(tags);
    this.selectedTagToAdd = null;
    this.applyFilter();
  }
}
