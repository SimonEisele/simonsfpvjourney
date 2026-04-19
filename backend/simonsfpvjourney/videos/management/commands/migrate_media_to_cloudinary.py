from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from videos.models import Drone, Picture, Video


class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary and update DB file fields"

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            default="simonsfpvjourney",
            help="Cloudinary folder prefix for uploaded files",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be uploaded without changing Cloudinary or database",
        )

    def handle(self, *args, **options):
        folder = (options.get("folder") or "simonsfpvjourney").strip("/")
        dry_run = bool(options.get("dry_run"))
        media_root = Path(settings.BASE_DIR) / "media"

        fields_to_process = [
            (Drone, "image"),
            (Video, "thumbnail"),
            (Picture, "image"),
        ]

        self.stdout.write(
            self.style.NOTICE(
                f"Starting media migration to Cloudinary folder '{folder}'"
            )
        )
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run enabled: no files will be uploaded"))

        total_seen = 0
        total_uploaded = 0
        total_skipped = 0
        total_missing = 0
        total_failed = 0

        for model, field_name in fields_to_process:
            queryset = model.objects.exclude(**{field_name: ""})
            self.stdout.write(f"Processing {model.__name__}.{field_name} ({queryset.count()} records)")

            for instance in queryset.iterator():
                total_seen += 1
                field = getattr(instance, field_name)
                existing_name = (field.name or "").strip()

                if not existing_name:
                    total_skipped += 1
                    continue

                if existing_name.startswith(f"{folder}/"):
                    total_skipped += 1
                    continue

                # If a full URL is stored, skip to avoid breaking externally hosted files.
                if existing_name.startswith("http://") or existing_name.startswith("https://"):
                    total_skipped += 1
                    continue

                local_path = media_root / existing_name
                if not local_path.exists() or not local_path.is_file():
                    total_missing += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"Missing local file for {model.__name__}:{instance.pk} -> {existing_name}"
                        )
                    )
                    continue

                new_name = f"{folder}/{existing_name.lstrip('/')}"

                if dry_run:
                    self.stdout.write(f"Would upload {existing_name} -> {new_name}")
                    total_uploaded += 1
                    continue

                try:
                    with local_path.open("rb") as source_file:
                        saved_name = field.storage.save(new_name, File(source_file))

                    field.name = saved_name
                    instance.save(update_fields=[field_name])
                    total_uploaded += 1
                except Exception as exc:
                    total_failed += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed {model.__name__}:{instance.pk} ({existing_name}): {exc}"
                        )
                    )

        self.stdout.write("Migration finished")
        self.stdout.write(
            f"Seen={total_seen} Uploaded={total_uploaded} Skipped={total_skipped} "
            f"Missing={total_missing} Failed={total_failed}"
        )
