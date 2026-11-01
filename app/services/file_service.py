
import logging
from pathlib import Path
from typing import List, Optional

from flask import current_app
from werkzeug.utils import secure_filename

from app.utils.exceptions import FileServiceError

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling uploaded files and job descriptions."""

    def __init__(self):
        try:
            # Flask application root directory
            self.base_dir = Path(current_app.root_path).resolve().parent

            # Read configured directories
            self.upload_folder = self._resolve_folder(
                current_app.config['UPLOAD_FOLDER']
            )

            self.job_descriptions_folder = self._resolve_folder(
                current_app.config['JOB_DESCRIPTIONS_FOLDER']
            )

            # Normalize allowed extensions
            self.allowed_extensions = {
                str(ext).lower().lstrip('.')
                for ext in current_app.config['ALLOWED_EXTENSIONS']
            }

            # Create directories if they do not exist
            self.upload_folder.mkdir(parents=True, exist_ok=True)
            self.job_descriptions_folder.mkdir(parents=True, exist_ok=True)

            logger.info("Upload folder: %s", self.upload_folder)
            logger.info(
                "Job descriptions folder: %s",
                self.job_descriptions_folder
            )

        except Exception as e:
            logger.exception("FileService initialization failed")
            raise FileServiceError(
                f"Failed to initialize file service: {e}"
            )

    def _resolve_folder(self, folder) -> Path:
        """Resolve a configured folder to an absolute path."""

        path = Path(folder).expanduser()

        if not path.is_absolute():
            path = self.base_dir / path

        return path.resolve()

    def is_allowed_file(self, filename: str) -> bool:
        """Check whether a file extension is allowed."""

        if not filename or '.' not in filename:
            return False

        extension = Path(filename).suffix.lower().lstrip('.')

        return extension in self.allowed_extensions

    def save_uploaded_file(
        self,
        file,
        filename: Optional[str] = None
    ) -> Path:
        """Save an uploaded file and return its absolute path."""

        try:
            original_filename = filename or file.filename

            if not original_filename:
                raise FileServiceError("No filename provided")

            if not self.is_allowed_file(original_filename):
                raise FileServiceError(
                    f"File type not allowed: {original_filename}"
                )

            safe_filename = secure_filename(original_filename)

            if not safe_filename:
                raise FileServiceError("Invalid filename")

            # Generate a unique filename if one already exists
            original_path = Path(safe_filename)
            stem = original_path.stem
            extension = original_path.suffix

            final_filename = safe_filename
            file_path = self.upload_folder / final_filename

            counter = 1

            while file_path.exists():
                final_filename = f"{stem}_{counter}{extension}"
                file_path = self.upload_folder / final_filename
                counter += 1

            # Save the uploaded file
            file.save(str(file_path))

            logger.info(
                "Resume saved successfully: %s",
                file_path
            )

            return file_path.resolve()

        except FileServiceError:
            raise

        except Exception as e:
            logger.exception("Error saving uploaded file")

            raise FileServiceError(
                f"Failed to save file: {e}"
            )

    def get_resume_files(self) -> List[Path]:
        """Get all resume files from the upload directory."""

        try:
            resume_files = []

            for file_path in self.upload_folder.iterdir():

                if (
                    file_path.is_file()
                    and file_path.suffix.lower().lstrip('.')
                    in self.allowed_extensions
                ):
                    resume_files.append(file_path.resolve())

            resume_files.sort(
                key=lambda path: path.name.lower()
            )

            logger.info(
                "Found %s resume files in %s",
                len(resume_files),
                self.upload_folder
            )

            return resume_files

        except Exception as e:
            logger.exception("Error getting resume files")

            raise FileServiceError(
                f"Failed to get resume files: {e}"
            )

    def get_job_description_files(self) -> List[Path]:
        """Get all job description files."""

        try:
            job_files = []

            for file_path in self.job_descriptions_folder.iterdir():

                if (
                    file_path.is_file()
                    and file_path.suffix.lower().lstrip('.')
                    in self.allowed_extensions
                ):
                    job_files.append(file_path.resolve())

            job_files.sort(
                key=lambda path: path.name.lower()
            )

            logger.info(
                "Found %s job description files",
                len(job_files)
            )

            return job_files

        except Exception as e:
            logger.exception(
                "Error getting job description files"
            )

            raise FileServiceError(
                f"Failed to get job description files: {e}"
            )

    def delete_file(self, file_path: Path) -> bool:
        """Delete a file only if it belongs to a managed directory."""

        try:
            target = Path(file_path).resolve()

            allowed_directories = [
                self.upload_folder,
                self.job_descriptions_folder
            ]

            if not any(
                target.is_relative_to(folder)
                for folder in allowed_directories
            ):
                raise FileServiceError(
                    "Cannot delete a file outside managed directories"
                )

            if target.is_file():
                target.unlink()

                logger.info("Deleted file: %s", target)
                return True

            return False

        except FileServiceError:
            raise

        except Exception as e:
            logger.exception("Error deleting file")

            raise FileServiceError(
                f"Failed to delete file: {e}"
            )

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""

        try:
            return Path(file_path).stat().st_size

        except Exception:
            logger.exception(
                "Error getting file size: %s",
                file_path
            )
            return 0
