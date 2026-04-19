import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { Drone } from '../../models/video.model';
import { MetaService } from '../../services/meta.service';

@Component({
  selector: 'app-gear',
  standalone: true,
  imports: [ CommonModule ],
  templateUrl: './gear.html',
  styleUrl: './gear.css',
})
export class Gear {
  drones$!: Observable<Drone[]>;

  constructor(private metaService: MetaService) {}

  ngOnInit(): void {
    this.drones$ = this.metaService.getDrones();
  }
}
