import { Component } from '@angular/core';
import { FeedbackModal } from '../../popups/feedbackmodal/feedback-modal';

@Component({
  selector: 'app-footer',
  imports: [FeedbackModal],
  templateUrl: './footer.html',
  styleUrl: './footer.css',
})
export class Footer {
  isFeedbackOpen = false;

}
