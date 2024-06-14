import base64
import csv
import io
import os.path
import urllib

import matplotlib
import numpy as np

matplotlib.use('Agg')

import pandas as pd
from django.conf import settings
from django.shortcuts import render, redirect
from matplotlib import pyplot as plt

from .forms import FileUploadForm
from .models import FileUpload


def home(request):
    return render(request, 'home.html')


def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('analyze_data')
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})


def analyze_data(request):
    latest_file = FileUpload.objects.latest('uploaded_at')
    file_path = os.path.join(settings.MEDIA_ROOT, latest_file.file.name)
    df = pd.read_csv(file_path)  #noqa

    if df.isnull().values.any():
        # Create a table with missing values
        table_with_missing = df.head().to_html(index=False)

        # Replace missing values with the mean of the column
        df_filled = df.fillna(df.mean(numeric_only=True))
        table_filled = df_filled.head().to_html(index=False)
        summary_status = df.describe().to_html()

        context = {
            'table_with_missing': table_with_missing,
            'table_filled': table_filled,
            'has_missing_values': True,
            'summary_status': summary_status
        }
    else:
        # Display the table if there are no missing values
        table = df.head().to_html(index=False)
        summary_status = df.describe().to_html()

        context = {
            'table': table,
            'has_missing_values': False,
            'summary_status': summary_status

        }

    return render(request, 'analyze_data.html', context)


def visualize_data(request):
    latest_file = FileUpload.objects.latest('uploaded_at')
    file_path = os.path.join(settings.MEDIA_ROOT, latest_file.file.name)

    subjects = []
    scores = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        header = next(csv_reader)  # Skip the header row if the CSV has a header
        for index, row in enumerate(csv_reader):
            if index >= 5:
                break
            subjects.append(row[0])
            score = row[1]
            if score.strip() == '':  # Check if score is missing
                scores.append(np.nan)  # Replace with NaN
            else:
                scores.append(float(score))
    scores = np.array(scores)

    # Calculate mean of scores ignoring NaN values
    mean_score = np.nanmean(scores)

    # Replace NaN values with mean_score
    scores[np.isnan(scores)] = mean_score

    plt.pie(scores, labels=subjects, autopct='%.2f%%')
    plt.show()

    # Save plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    context = {'plot': uri}

    return render(request, 'visualize_data.html', context)
