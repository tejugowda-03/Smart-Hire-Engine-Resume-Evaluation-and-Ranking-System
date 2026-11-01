
@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """Upload a resume and return to the homepage with a message."""

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
            flash('Only PDF, DOC, DOCX and TXT files are allowed.', 'error')
            return redirect(url_for('main.index'))

        file_path = file_service.save_uploaded_file(file)

        logger.info("Resume uploaded successfully: %s", file_path.name)

        flash(f'Resume "{file_path.name}" uploaded successfully!', 'success')
        return redirect(url_for('main.index'))

    except FileServiceError as e:
        logger.exception("File service error")
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

    except Exception:
        logger.exception("Resume upload failed")
        flash('Resume upload failed. Please try again.', 'error')
        return redirect(url_for('main.index'))
