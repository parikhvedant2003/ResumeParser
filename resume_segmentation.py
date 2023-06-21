class segmentation:
    # These are the keywords which are used to segment the PDF file into desired segments
    objective = (
        'career goal', 'objective', 'career objective', 'employment objective', 'professional objective', 'career summary', 'professional summary', 'summary of qualifications', 'summary', 'digital'
    )
    work_and_employment = (
        'career profile', 'employment history', 'work history', 'work experience', 'experience', 'professional experience', 'professional background', 'additional experience', 'career related experience', 'related experience', 'programming experience', 'freelance', 'freelance experience', 'army experience', 'military experience', 'military background'
    )
    education_and_training = (
        'academic background', 'academic experience', 'programs', 'courses', 'related courses', 'education', 'qualifications', 'educational background', 'educational qualifications', 'educational training', 'education and training', 'training', 'academic training', 'professional training', 'course project experience', 'related course projects', 'internship experience', 'internships', 'apprenticeships', 'college activities', 'certifications', 'special training'
    )
    skills_header = (
        'credentials', 'areas of experience', 'areas of expertise', 'areas of knowledge', 'skills', 'other skills', 'other abilities', 'career related skills', 'professional skills', 'specialized skills', 'technical skills', 'computer skills', 'personal skills', 'computer knowledge', 'technologies', 'technical experience', 'proficiencies', 'languages', 'language competencies and skills', 'programming languages', 'competencies'
    )
    misc = (
        'activities and honors', 'activities', 'affiliations', 'professional affiliations', 'associations', 'professional associations', 'memberships', 'professional memberships', 'athletic involvement', 'community involvement', 'refere', 'civic activities', 'extra-Curricular activities', 'professional activities', 'volunteer work', 'volunteer experience', 'additional information', 'interests'
    )
    accomplishments = (
        'achievement', 'licenses', 'presentations', 'conference presentations', 'conventions', 'dissertations', 'exhibits', 'papers', 'publications', 'professional publications', 'research', 'research grants', 'project', 'research projects', 'personal projects', 'current research interests', 'thesis', 'theses'
    )

    # It is deciding that the one resume line should be in which segment
    def find_segment_indices(resume_lines, resume_segments, resume_indices):
        for i, line in enumerate(resume_lines):
            if line[0].islower():
                continue
            header = line.lower()
            if [o for o in segmentation.objective if header.startswith(o)]:
                try:
                    resume_segments['objective'][header]
                except:
                    resume_indices.append(i)
                    header = [o for o in segmentation.objective if header.startswith(o)][0]
                    resume_segments['objective'][header] = i
            elif [w for w in segmentation.work_and_employment if header.startswith(w)]:
                try:
                    resume_segments['work_and_employment'][header]
                except:
                    resume_indices.append(i)
                    header = [w for w in segmentation.work_and_employment if header.startswith(w)][0]
                    resume_segments['work_and_employment'][header] = i
            elif [e for e in segmentation.education_and_training if header.startswith(e)]:
                try:
                    resume_segments['education_and_training'][header]
                except:
                    resume_indices.append(i)
                    header = [e for e in segmentation.education_and_training if header.startswith(e)][0]
                    resume_segments['education_and_training'][header] = i
            elif [s for s in segmentation.skills_header if header.startswith(s)]:
                try:
                    resume_segments['skills'][header]
                except:
                    resume_indices.append(i)
                    header = [s for s in segmentation.skills_header if header.startswith(s)][0]
                    resume_segments['skills'][header] = i
            elif [m for m in segmentation.misc if header.startswith(m)]:
                try:
                    resume_segments['misc'][header]
                except:
                    resume_indices.append(i)
                    header = [m for m in segmentation.misc if header.startswith(m)][0]
                    resume_segments['misc'][header] = i
            elif [a for a in segmentation.accomplishments if header.startswith(a)]:
                try:
                    resume_segments['accomplishments'][header]
                except:
                    resume_indices.append(i)
                    header = [a for a in segmentation.accomplishments if header.startswith(a)][0]
                    resume_segments['accomplishments'][header] = i

    # This is performing segmentation using segment indices
    def slice_segments(resume_lines, resume_segments, resume_indices):
        resume_segments['contact_info'] = resume_lines[:resume_indices[0]]
        for section, value in resume_segments.items():
            if section == 'contact_info':
                continue
            for sub_section, start_idx in value.items():
                end_idx = len(resume_lines)
                if (resume_indices.index(start_idx) + 1) != len(resume_indices):
                    end_idx = resume_indices[resume_indices.index(start_idx) + 1]
                resume_segments[section][sub_section] = resume_lines[start_idx:end_idx]

    def segment(resume_lines):
        resume_segments = {
            'objective': {},
            'work_and_employment': {},
            'education_and_training': {},
            'skills': {},
            'accomplishments': {},
            'misc': {}
        }
        resume_indices = []
        segmentation.find_segment_indices(resume_lines, resume_segments, resume_indices)
        if len(resume_indices) != 0:
            segmentation.slice_segments(resume_lines, resume_segments, resume_indices)
        else:
            resume_segments['contact_info'] = []
        return resume_segments