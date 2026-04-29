from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import Student, Course, ResultRecord
from django.db.models import Avg
from reportlab.pdfgen import canvas

temp_data = []


def home(request):
    return render(request, 'results/home.html')


# ---------------- CSV PREVIEW ----------------
def upload_csv(request):
    return render(request, 'results/upload.html')


def preview_csv(request):
    global temp_data
    temp_data = []

    file = request.FILES['file'].read().decode('utf-8').splitlines()
    reader = csv.reader(file)

    preview = []

    for row in reader:
        if len(row) != 3:
            preview.append({'name': '', 'course': '', 'marks': '', 'error': True})
            continue

        name, course, marks = row
        error = False

        if not name or not course or not marks:
            error = True
        elif not marks.isdigit():
            error = True
        else:
            marks = int(marks)
            if marks > 100 or marks < 0:
                error = True

        preview.append({
            'name': name,
            'course': course,
            'marks': marks,
            'error': error
        })

        if not error:
            temp_data.append([name, course, marks])

    return render(request, 'results/preview.html', {'data': preview})


# ---------------- SAVE ----------------
def save_csv(request):
    records = []

    for row in temp_data:
        name, course_name, marks = row

        student, _ = Student.objects.get_or_create(name=name)
        course, _ = Course.objects.get_or_create(title=course_name)

        records.append(ResultRecord(
            student=student,
            course=course,
            marks=marks
        ))

    ResultRecord.objects.bulk_create(records)

    return HttpResponse("Data Saved Successfully!")


# ---------------- ANALYTICS ----------------
def analytics(request):
    results = ResultRecord.objects.all()

    course_avg = ResultRecord.objects.values('course__title').annotate(avg=Avg('marks'))
    avg_dict = {item['course__title']: item['avg'] for item in course_avg}

    data = []

    for r in results:
        avg = avg_dict[r.course.title]

        status = "Above Average" if r.marks >= avg else "Below Average"

        if r.marks >= avg + 10:
            rank = "Topper"
        elif r.marks >= avg:
            rank = "Average"
        else:
            rank = "Weak"

        data.append({
            'name': r.student.name,
            'course': r.course.title,
            'marks': r.marks,
            'avg': round(avg, 2),
            'status': status,
            'rank': rank
        })

    return render(request, 'results/analytics.html', {'data': data})


# ---------------- PDF ----------------
def generate_pdf(request):
    total = ResultRecord.objects.count()
    passed = ResultRecord.objects.filter(marks__gte=40).count()
    failed = total - passed

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, "Performance Report")
    p.drawString(100, 780, f"Total Students: {total}")
    p.drawString(100, 760, f"Passed: {passed}")
    p.drawString(100, 740, f"Failed: {failed}")

    p.save()
    return response