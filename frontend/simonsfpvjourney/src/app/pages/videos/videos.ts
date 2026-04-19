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
  private readonly advancedFiltersStorageKey = 'simonsfpvjourney.videos.showAdvancedFilters';
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

  private readonly seasonOptions = [
    { value: 'Spring', label: 'Spring' },
    { value: 'Summer', label: 'Summer' },
    { value: 'Autumn', label: 'Autumn' },
    { value: 'Winter', label: 'Winter' },
  ];

  private readonly weatherOptions = [
    { value: 'Sunny', label: 'Sunny' },
    { value: 'Cloudy', label: 'Cloudy' },
    { value: 'Rainy', label: 'Rainy' },
    { value: 'Snowy', label: 'Snowy' },
    { value: 'Foggy', label: 'Foggy' },
  ];

  private readonly timeOptions = [
    { value: 'Morning', label: 'Morning' },
    { value: 'Afternoon', label: 'Afternoon' },
    { value: 'Evening', label: 'Evening' },
    { value: 'Night', label: 'Night' },
    { value: 'Sunrise', label: 'Sunrise' },
    { value: 'Golden Hour', label: 'Golden Hour' },
    { value: 'Sunset', label: 'Sunset' },
  ];

  // Search suggestions dropdown
  getSuggestions(): Array<{ label: string; count: number; type: 'Video' | 'Category' | 'Tag'; value: string | number }> {
    const q = (this.searchText || '').trim().toLowerCase();
    const max = 12;
    const suggestions: Array<{ label: string; count: number; type: 'Video' | 'Category' | 'Tag'; value: string | number }> = [];

    for (const video of this.videosSnapshot) {
      if (!video?.title) continue;
      const label = video.title.trim();
      if (!label) continue;
      if (q && !label.toLowerCase().includes(q)) continue;
      suggestions.push({ label, count: 1, type: 'Video', value: label });
    }

    for (const category of this.categories) {
      const label = category.name.trim();
      if (!label) continue;
      if (q && !label.toLowerCase().includes(q)) continue;
      const count = this.facetCounts.categories?.[category.id] ?? 0;
      if (count <= 0) continue;
      suggestions.push({ label, count, type: 'Category', value: category.id });
    }

    for (const tag of this.tags) {
      const label = tag.name.trim();
      if (!label) continue;
      if (q && !label.toLowerCase().includes(q)) continue;
      const count = this.facetCounts.tags?.[tag.id] ?? 0;
      if (count <= 0) continue;
      suggestions.push({ label, count, type: 'Tag', value: tag.id });
    }

    const seen = new Set<string>();
    return suggestions
      .filter(item => item.count > 0)
      .filter(item => {
        const key = `${item.type}:${item.label}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      })
      .sort((a, b) => b.count - a.count || a.type.localeCompare(b.type) || a.label.localeCompare(b.label))
      .slice(0, max);
  }

  selectSuggestion(s: { label: string; count: number; type: 'Video' | 'Category' | 'Tag'; value: string | number }): void {
    this.searchText = s.label;

    if (s.type === 'Category') {
      this.filter.category = String(s.value);
    } else if (s.type === 'Tag') {
      const tagId = Number(s.value);
      const tags = new Set<number>(this.filter.tags ?? []);
      tags.add(tagId);
      this.filter.tags = Array.from(tags);
    }

    this.applyFilter();
    this.showSuggestions = false;
  }

  constructor(
    private videoService: VideoService,
    private metaService: MetaService
  ) {}

  ngOnInit(): void {
    const savedFilter = this.videoService.getCurrentFilter();
    if (savedFilter) {
      this.filter = { order_by: 'views_current', order_dir: 'desc', ...savedFilter };
      this.searchText = savedFilter.search ?? '';
    }
    this.showAdvancedFilters = this.loadSavedAdvancedFiltersState();

    // Load Categories, Tags, Drones
    this.metaService.getCategories().subscribe(c => this.categories = c);
    this.metaService.getTags().subscribe(t => this.tags = t);
    this.metaService.getDrones().subscribe(d => this.drones = d);

    // Videos laden
    this.videoService.loadVideos();

    // Set current filter (restored from localStorage or defaults)
    this.applyFilter();

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
    this.saveAdvancedFiltersState(this.showAdvancedFilters);
  }

  getSeasonOptions(): Array<{ value: string; label: string; count: number }> {
    return this.seasonOptions
      .map(option => ({
        ...option,
        count: this.facetCounts.seasons?.[option.value] ?? 0,
      }))
      .filter(option => option.count > 0);
  }

  getWeatherOptions(): Array<{ value: string; label: string; count: number }> {
    return this.weatherOptions
      .map(option => ({
        ...option,
        count: this.facetCounts.weathers?.[option.value] ?? 0,
      }))
      .filter(option => option.count > 0);
  }

  getTimeOptions(): Array<{ value: string; label: string; count: number }> {
    return this.timeOptions
      .map(option => ({
        ...option,
        count: this.facetCounts.times?.[option.value] ?? 0,
      }))
      .filter(option => option.count > 0);
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
    this.filter = { order_by: 'views_current', order_dir: 'desc' };
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

  onFilterChange(): void {
    this.applyFilter();
  }

  private loadSavedAdvancedFiltersState(): boolean {
    if (typeof localStorage === 'undefined') return false;
    try {
      return localStorage.getItem(this.advancedFiltersStorageKey) === 'true';
    } catch {
      return false;
    }
  }

  private saveAdvancedFiltersState(isOpen: boolean): void {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(this.advancedFiltersStorageKey, String(isOpen));
    } catch {}
  }
}
