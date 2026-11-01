
import logging
from pathlib import Path

from flask import (
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    render_template,
    send_file
)

from app.utils.decorators import login_required
from app.utils.exceptions import FileServiceError
from app.services.file_service import FileService
from app.services.matching_service import ResumeMatchingService
from app.services.resume_parser import ResumeParserFactory
from app.models.job_description import JobDescription


logger = logging.getLogger(__name__)

# Define blueprint before declaring routes
resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Upload a resume and return to the homepage."""

    try:
        if 'file' not in request.files:
            flash('Please select a resume file.', 'error')
            return redirect(url_for('main.index'))

        file = request.files['file']

        if not file.filename:
            flash('Please select a resume file.', 'error')
            return redirect(url_for('main.index'))

        file_service = FileService()

        if not file_service.is_allowed_file(file.filename):
            flash(
                'Only PDF, DOC and DOCX files are supported.',
                'error'
            )
            return redirect(url_for('main.index'))

        extension = Path(file.filename).suffix.lower()

        if extension not in ResumeParserFactory.supported_extensions():
            flash(
                'This resume format cannot currently be processed.',
                'error'
            )
            return redirect(url_for('main.index'))

        file_path = file_service.save_uploaded_file(file)

        logger.info(
            "Resume uploaded successfully: %s",
            file_path.name
        )

        flash(
            f'Resume "{file_path.name}" uploaded successfully!',
            'success'
        )

        return redirect(url_for('main.index'))

    except FileServiceError as e:
        logger.exception("File service error")
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

    except Exception:
        logger.exception("Resume upload failed")
        flash('Resume upload failed. Please try again.', 'error')
        return redirect(url_for('main.index'))


@resume_bp.route('/process', methods=['POST'])
@login_required
def process_resumes():
    """Process and rank uploaded resumes."""

    try:
        job_description_file = request.form.get('job_description')

        if not job_description_file:
            flash('Please select a job description.', 'warning')
            return redirect(url_for('main.index'))

        file_service = FileService()

        # Find the selected job description safely
        job_file_path = (
            file_service.job_descriptions_folder
            / Path(job_description_file).name
        )

        if not job_file_path.is_file():
            flash('Job description file not found.', 'error')
            return redirect(url_for('main.index'))

        # Read job description
        job_text = job_file_path.read_text(
            encoding='utf-8',
            errors='ignore'
        )

        job_description = JobDescription(
            title=job_file_path.stem,
            description=job_text,
            file_path=job_file_path
        )

        # Get uploaded resumes
        resume_files = file_service.get_resume_files()

        if not resume_files:
            flash(
                'No resumes found. Please upload resumes first.',
                'warning'
            )
            return redirect(url_for('main.index'))

        # Parse resumes
        candidates = []

        for resume_file in resume_files:
            try:
                extension = resume_file.suffix.lower()

                if extension not in ResumeParserFactory.supported_extensions():
                    logger.warning(
                        "Unsupported resume format: %s",
                        resume_file.name
                    )
                    continue

                parser = ResumeParserFactory.get_parser(extension)

                candidate = parser.parse(resume_file)

                if candidate:
                    candidates.append(candidate)

            except Exception:
                logger.exception(
                    "Failed to parse resume: %s",
                    resume_file.name
                )

        if not candidates:
            flash(
                'No resumes could be parsed. Please check the uploaded files.',
                'warning'
            )
            return redirect(url_for('main.index'))

        # Match and rank candidates
        matching_service = ResumeMatchingService(
            top_candidates_count=10,
            similarity_threshold=0.1
        )

        ranked_candidates = matching_service.match_candidates(
            job_description,
            candidates
        )

        return render_template(
            'results.html',
            candidates=ranked_candidates,
            job_description=job_description
        )

    except Exception:
        logger.exception("Resume processing failed")
        flash(
            'Unable to process resumes. Please check the application logs.',
            'error'
        )
        return redirect(url_for('main.index'))


@resume_bp.route('/download/<path:filename>')
@login_required
def download_resume(filename):
    """Download an uploaded resume."""

    try:
        file_service = FileService()

        safe_filename = Path(filename).name
        file_path = file_service.upload_folder / safe_filename

        if not file_path.is_file():
            flash('Resume file not found.', 'error')
            return redirect(url_for('main.index'))

        return send_file(
            file_path,
            as_attachment=True,
            download_name=safe_filename
        )

    except Exception:
        logger.exception("Resume download failed")
        flash('Unable to download the resume.', 'error')
        return redirect(url_for('main.index'))
