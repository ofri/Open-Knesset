from django.core.management.base import NoArgsCommand
from django.http import HttpRequest
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from laws.views import BillCsvView

class Command(NoArgsCommand):
	help = "Updates bills.csv file in media"

	def handle_noargs(self,**options):
		# create objects for request
		viewObj = BillCsvView()
		viewReq = HttpRequest()
		viewReq.META['SERVER_NAME'] = 'localhost'
		viewReq.META['SERVER_PORT'] = 8000

		# execute request
		viewRes = viewObj.dispatch(viewReq)

		# write result to media file
		outputFile = ContentFile(viewRes.content)
		filewithpath = BillCsvView.filename

		# remove existing file
		if default_storage.exists(filewithpath):
			default_storage.delete(filewithpath)

		# store the file
		default_storage.save(filewithpath,outputFile)

