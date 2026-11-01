
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory
)

from pathlib import Path
from app.services.resume_parser import ResumeParserFactory
from app.services.matching_service import ResumeMatchingService
from app.services.file_service import FileService
from app.models.job_description import JobDescription
from app.utils.decorators import login_required
from app.utils.exceptions import (
    ResumeParsingError,
    MatchingServiceError,
    FileServiceError
)
import logging

logger = logging.getLogger(__name__)

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/process', methods=['POST'])
@login_required
def process_resumes():
    """Process resumes against selected job description."""
    try:
        job_description_file = request.form.get('job_description')

        if not job_description_file:
            flash('Please select a job description', 'error')
            return redirect(url_for('main.index'))

        file_service = FileService()

        # Load job description
        job_file_path = (
            Path(file_service.job_descriptions_folder)
            / job_description_file
        )

        if not job_file_path.is_file():
            flash('Selected job description not found', 'error')
            return redirect(url_for('main.index'))

        # Parse job description
        job_description = _parse_job_description(job_file_path)

        # Get and parse resume files
        resume_files = file_service.get_resume_files()

        if not resume_files:
            flash(
                'No resume files found. Please upload some resumes first.',
                'warning'
            )
            return redirect(url_for('main.index'))

        candidates = _parse_resume_files(resume_files)

        if not candidates:
            flash('No resumes could be parsed successfully', 'error')
            return redirect(url_for('main.index'))

        # Match candidates
        matching_service = ResumeMatchingService()

        ranked_candidates = matching_service.match_candidates(
            job_description,
            candidates
        )

        logger.info(
            "Successfully processed %s candidates",
            len(ranked_candidates)
        )

        return render_template(
            'results.html',
            candidates=ranked_candidates,
            job_description=job_description
        )

    except Exception:
        logger.exception("Error processing resumes")

        flash(
            'Failed to process resumes. Please try again.',
            'error'
        )

        return redirect(url_for('main.index'))


@resume_bp.route('/download/<path:filename>')
@login_required
def download_resume(filename):
    """Safely download an uploaded resume."""

    try:
        file_service = FileService()

        # Get the absolute upload directory
        upload_folder = Path(
            file_service.upload_folder
        ).resolve()

        # Reject directory traversal attempts
        if (
            not filename
            or filename != Path(filename).name
            or '/' in filename
            or '\\' in filename
        ):
            flash('Invalid file name', 'error')
            return redirect(url_for('main.index'))

        # Check whether the file exists
        file_path = upload_folder / filename

        if not file_path.is_file():
            logger.warning(
                "Resume file not found: %s",
                file_path
            )

            flash('Resume file not found', 'error')
            return redirect(url_for('main.index'))

        # Send file as an attachment
        return send_from_directory(
            directory=str(upload_folder),
            path=filename,
            as_attachment=True,
            download_name=filename
        )

    except Exception:
        logger.exception(
            "Error downloading resume: %s",
            filename
        )

        flash(
            'Failed to download file. Please try again.',
            'error'
        )

        return redirect(url_for('main.index'))


@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Upload a new resume file."""

    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400

        file_service = FileService()

        if not file_service.is_allowed_file(file.filename):
            return jsonify({
                'error': 'File type not allowed'
            }), 400

        file_path = file_service.save_uploaded_file(file)

        logger.info(
            "Resume uploaded successfully: %s",
            file_path.name
        )

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': file_path.name
        }), 200

    except FileServiceError as e:
        logger.exception("File service error")

        return jsonify({
            'error': str(e)
        }), 400

    except Exception:
        logger.exception("Resume upload failed")

        return jsonify({
            'error': 'Upload failed'
        }), 500


def _parse_job_description(file_path: Path) -> JobDescription:
    """Parse job description file."""

    try:
        if file_path.suffix.lower() == '.txt':

            with open(
                file_path,
                'r',
                encoding='utf-8'
            ) as f:
                content = f.read()

        else:
            parser = ResumeParserFactory.get_parser(
                file_path.suffix
            )

            candidate = parser.parse(file_path)

            content = candidate.resume_text

        return JobDescription(
            title=file_path.stem,
            description=content,
            file_path=file_path
        )

    except Exception:
        logger.exception(
            "Error parsing job description: %s",
            file_path
        )
        raise


def _parse_resume_files(resume_files: list) -> list:
    """Parse multiple resume files."""

    candidates = []

    for resume_file in resume_files:

        try:
            parser = ResumeParserFactory.get_parser(
                resume_file.suffix
            )

            candidate = parser.parse(resume_file)

            candidates.append(candidate)

        except Exception:
            logger.exception(
                "Failed to parse resume: %s",
                resume_file
            )
            continue

    return candidates
