import os
import django_rq
from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data ingestion...')
        
        # Check if Excel files exist
        if not os.path.exists('customer_data.xlsx'):
            self.stdout.write(
                self.style.ERROR('customer_data.xlsx not found in project root')
            )
            return
        
        if not os.path.exists('loan_data.xlsx'):
            self.stdout.write(
                self.style.ERROR('loan_data.xlsx not found in project root')
            )
            return
        
        # Queue the ingestion job
        queue = django_rq.get_queue('default')
        job = queue.enqueue(ingest_all_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Data ingestion job queued with ID: {job.id}')
        )
        
        # Wait for job completion and show results
        result = job.result
        if result:
            self.stdout.write(
                self.style.SUCCESS(f'Data ingestion completed: {result}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Job is still running or failed')
            )