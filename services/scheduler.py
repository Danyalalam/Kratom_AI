from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging
from config import get_settings
import pymongo
import importlib

logger = logging.getLogger(__name__)
settings = get_settings()

class SchedulerService:
    def __init__(self):
        # Use pymongo for the job store
        mongo_client = pymongo.MongoClient(settings.MONGODB_URL)
        self.jobstore = MongoDBJobStore(
            database='kratom_ai',
            collection='scheduled_jobs',
            client=mongo_client
        )
        
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': self.jobstore
            },
            job_defaults={
                'coalesce': True,  # Combine multiple missed executions into one
                'max_instances': 1,  # Only run one instance of each job
                'misfire_grace_time': 3600  # Allow 1 hour grace time for misfired jobs
            },
            timezone='UTC'
        )
        
        logger.info("Scheduler service initialized")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down")

    def _resolve_function(self, func_ref: str):
        """Resolve a string function reference to an actual function"""
        try:
            if isinstance(func_ref, str):
                module_name, func_name = func_ref.split(':')
                module = importlib.import_module(module_name)
                return getattr(module, func_name)
            return func_ref
        except Exception as e:
            logger.error(f"Error resolving function {func_ref}: {str(e)}")
            raise

    async def schedule_email(self, job_id: str, func, args=None, run_date=None):
        """Schedule an email job"""
        if run_date is None:
            run_date = datetime.utcnow() + timedelta(days=7)
        
        try:
            # Resolve the function if it's a string reference
            resolved_func = self._resolve_function(func)
            
            self.scheduler.add_job(
                func=resolved_func,
                trigger=DateTrigger(run_date=run_date),
                args=args or [],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=3600  # Allow 1 hour grace time for misfired jobs
            )
            logger.info(f"Scheduled email job {job_id} for {run_date}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule email job {job_id}: {str(e)}")
            return False

    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            return False