import pandas as pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import UploadRecord
from .serializers import UploadRecordSerializer

from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    Accept CSV file, calculate summary, store record,
    keep only last 5 uploads, return summary.
    """
    csv_file = request.FILES.get('file')
    if not csv_file:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        return Response({"error": f"Invalid CSV: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
    for col in required_cols:
        if col not in df.columns:
            return Response({"error": f"Missing required column: {col}"}, status=status.HTTP_400_BAD_REQUEST)

    total_count = len(df)

    avg_flowrate = df['Flowrate'].mean()
    avg_pressure = df['Pressure'].mean()
    avg_temperature = df['Temperature'].mean()

    type_counts = df['Type'].value_counts().to_dict()

    # create record in DB
    record = UploadRecord.objects.create(
        filename=csv_file.name,
        total_count=total_count,
        avg_flowrate=avg_flowrate,
        avg_pressure=avg_pressure,
        avg_temperature=avg_temperature,
        type_distribution=type_counts,
    )

    # keep only last 5 uploads
    all_ids = list(UploadRecord.objects.order_by('-uploaded_at').values_list('id', flat=True))
    if len(all_ids) > 5:
        to_delete = all_ids[5:]
        UploadRecord.objects.filter(id__in=to_delete).delete()

    data = {
        "summary": {
            "total_count": total_count,
            "avg_flowrate": avg_flowrate,
            "avg_pressure": avg_pressure,
            "avg_temperature": avg_temperature,
            "type_distribution": type_counts,
        },
        "record_id": record.id,
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def last_uploads(request):
    """
    Return the last 5 uploads for history view.
    """
    records = UploadRecord.objects.order_by('-uploaded_at')[:5]
    serializer = UploadRecordSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request, record_id):
    """
    Generate a simple PDF report for a given upload record.
    """
    try:
        record = UploadRecord.objects.get(id=record_id)
    except UploadRecord.DoesNotExist:
        raise Http404("Record not found")

    # create HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{record_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Chemical Equipment Report")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Filename: {record.filename}")
    y -= 20
    p.drawString(50, y, f"Uploaded at: {record.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    p.drawString(50, y, f"Total equipment: {record.total_count}")
    y -= 20
    p.drawString(50, y, f"Average flowrate: {record.avg_flowrate:.2f}")
    y -= 20
    p.drawString(50, y, f"Average pressure: {record.avg_pressure:.2f}")
    y -= 20
    p.drawString(50, y, f"Average temperature: {record.avg_temperature:.2f}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Equipment Type Distribution:")
    y -= 20

    p.setFont("Helvetica", 12)
    for eq_type, count in record.type_distribution.items():
        p.drawString(60, y, f"- {eq_type}: {count}")
        y -= 18
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)

    p.showPage()
    p.save()
    return response

