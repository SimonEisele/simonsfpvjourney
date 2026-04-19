import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, EventEmitter, Input, Output, ViewChild, ElementRef, HostListener, OnChanges, SimpleChanges, AfterViewInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { FeedbackService, FeedbackPayload } from '../../services/feedback.service';
import { PLATFORM_ID, Inject } from '@angular/core';

@Component({
  selector: 'app-feedback-modal',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './feedback-modal.html',
  styleUrl: './feedback-modal.css',
})
export class FeedbackModal implements OnChanges, AfterViewInit {
  @Input() open = false;
  @Output() closed = new EventEmitter<void>();
  @ViewChild('contentRoot') contentRoot?: ElementRef<HTMLDivElement>;

  message = '';
  name = '';
  contact = '';
  category = '';
  submitting = false;
  success = false;
  error = '';
  messageError = '';

  private wasOpen = false;
  constructor(private feedback: FeedbackService, @Inject(PLATFORM_ID) private platformId: Object) {}

  onClose() {
    this.closed.emit();
    this.reset();
    if (isPlatformBrowser(this.platformId)) {
      document.body.style.overflow = '';
    }
  }

  reset() {
    this.message = '';
    this.name = '';
    this.contact = '';
    this.category = '';
    this.submitting = false;
    this.success = false;
    this.error = '';
    this.messageError = '';
  }

  canSubmit(): boolean {
    return !!this.message.trim() && !this.submitting;
  }

  submit() {
    if (!this.message.trim()) {
      this.messageError = 'Please enter your feedback message.';
      return;
    }
    this.submitting = true;
    const payload: FeedbackPayload = {
      message: this.message.trim(),
      category: this.category || undefined,
      name: this.name || undefined,
      contact: this.contact || undefined,
      page_url: typeof window !== 'undefined' ? window.location.href : undefined,
    };
    this.feedback.submit(payload).subscribe({
      next: () => {
        this.submitting = false;
        // Close modal on success and reset form
        this.onClose();
      },
      error: (e: unknown) => {
        this.error = 'Failed to send feedback. Please try again later.';
        this.submitting = false;
      },
    });
  }

  onInputMessage() {
    if (this.messageError && this.message.trim()) {
      this.messageError = '';
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']) {
      const isBrowser = isPlatformBrowser(this.platformId);
      const prev = changes['open'].previousValue as boolean | undefined;
      if (this.open) {
        if (isBrowser) {
          document.body.style.overflow = 'hidden';
        }
        setTimeout(() => this.contentRoot?.nativeElement.focus(), 0);
        this.wasOpen = true;
      } else if (prev) {
        if (isBrowser) {
          document.body.style.overflow = '';
        }
        this.wasOpen = false;
      }
    }
  }

  ngAfterViewInit(): void {
    if (this.open) {
      this.contentRoot?.nativeElement.focus();
    }
  }

  @HostListener('document:keydown', ['$event'])
  onKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      this.onClose();
    }
  }
}
