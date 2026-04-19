import { CommonModule } from '@angular/common';
import { Component, HostListener } from '@angular/core';
import { Picture } from '../../models/picture.model';
import { RouterModule } from '@angular/router';
import { VideoService } from '../../services/video.service';
import { Video } from '../../models/video.model';

@Component({
  selector: 'app-pictures',
  standalone: true,
  imports: [ CommonModule, RouterModule ],
  templateUrl: './pictures.html',
  styleUrl: './pictures.css',
})
export class Pictures {
  pictures: Picture[] = [];
  fullscreenPicture: Picture | null = null;
  private touchStartX = 0;
  private touchStartY = 0;
  private thumbTouchStartX = 0;
  private thumbTouchStartY = 0;
  private thumbMovedDistance = 0;

  constructor(private videoService: VideoService) {}

  ngOnInit(): void {
    this.videoService.loadVideos();
    this.videoService.filteredVideos$.subscribe(videos => {
      this.pictures = this.flattenPictures(videos);
    });
  }

  private flattenPictures(videos: Video[]): Picture[] {
    const flattened: Picture[] = [];
    for (const video of videos) {
      const pics = (video.pictures ?? []).map(p => ({
        id: p.id,
        image: p.image,
        video: video.id,
        video_title: video.title,
        video_latitude: video.latitude,
        video_longitude: video.longitude,
        video_place: video.place ?? '',
        created_at: p.created_at,
      }));
      flattened.push(...pics);
    }
    return flattened;
  }

  openFullscreen(pic: Picture): void {
    this.fullscreenPicture = pic;
    document.body.style.overflow = 'hidden';
  }

  onThumbTouchStart(event: TouchEvent): void {
    // Record start position for movement detection
    if (event.touches && event.touches.length > 0) {
      this.thumbTouchStartX = event.touches[0].clientX;
      this.thumbTouchStartY = event.touches[0].clientY;
      this.thumbMovedDistance = 0;
    }
  }

  onThumbTouchMove(event: TouchEvent): void {
    // Track if user is scrolling - calculate distance moved
    if (event.touches && event.touches.length > 0) {
      const dx = Math.abs(event.touches[0].clientX - this.thumbTouchStartX);
      const dy = Math.abs(event.touches[0].clientY - this.thumbTouchStartY);
      this.thumbMovedDistance = Math.max(dx, dy);
    }
  }

  onThumbTouchEnd(pic: Picture, event: TouchEvent): void {
    // Only open fullscreen if touch movement was minimal (tap, not scroll)
    if (this.thumbMovedDistance < 10) {
      console.log('✅ Opening fullscreen - tap detected (distance:', this.thumbMovedDistance, ')');
      this.openFullscreen(pic);
    } else {
      console.log('➡️ Scrolling detected (distance:', this.thumbMovedDistance, ') - ignoring tap');
    }
  }

  onThumbClick(pic: Picture): void {
    // For desktop click support
    console.log('🖱️ Click event fired - desktop tap');
    this.openFullscreen(pic);
  }

  closeFullscreen(): void {
    this.fullscreenPicture = null;
    document.body.style.overflow = '';
  }

  private getFullscreenIndex(): number {
    if (!this.fullscreenPicture) return -1;
    return this.pictures.findIndex(p => p.id === this.fullscreenPicture?.id);
  }

  canPrevFullscreen(): boolean {
    return this.getFullscreenIndex() > 0;
  }

  canNextFullscreen(): boolean {
    const i = this.getFullscreenIndex();
    return i >= 0 && i < this.pictures.length - 1;
  }

  showPrevFullscreen(): void {
    const i = this.getFullscreenIndex();
    if (i > 0) this.fullscreenPicture = this.pictures[i - 1];
  }

  showNextFullscreen(): void {
    const i = this.getFullscreenIndex();
    if (i >= 0 && i < this.pictures.length - 1) this.fullscreenPicture = this.pictures[i + 1];
  }

  onFullscreenTouchStart(event: TouchEvent): void {
    if (!event.touches || event.touches.length === 0) return;
    this.touchStartX = event.touches[0].clientX;
    this.touchStartY = event.touches[0].clientY;
  }

  onFullscreenTouchEnd(event: TouchEvent): void {
    if (!this.fullscreenPicture) return;
    const touch = event.changedTouches && event.changedTouches[0];
    if (!touch) return;
    const dx = touch.clientX - this.touchStartX;
    const dy = touch.clientY - this.touchStartY;
    const absDx = Math.abs(dx);
    const absDy = Math.abs(dy);

    // Horizontal swipe only; ignore mostly vertical gestures.
    if (absDx > 30 && absDx > absDy * 1.2) {
      if (dx < 0) this.showNextFullscreen();
      if (dx > 0) this.showPrevFullscreen();
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.fullscreenPicture) {
      this.closeFullscreen();
    }
  }

  @HostListener('document:keydown.arrowleft')
  onArrowLeft(): void {
    if (this.fullscreenPicture) this.showPrevFullscreen();
  }

  @HostListener('document:keydown.arrowright')
  onArrowRight(): void {
    if (this.fullscreenPicture) this.showNextFullscreen();
  }
}
