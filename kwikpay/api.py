from __future__ import absolute_import
from rest_framework import viewsets, permissions
#rest framework
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
# general django
from django.http import HttpResponse, JsonResponse
from .utils.qrGenerator import QRGenerator 

def generateQR(request):
    text=request.GET.get("text", None)
    tillNumber=request.GET.get("tillNumber", None)
    
    if not text and not tillNumber:
        text="Hello World"

    g=QRGenerator(text=text, tillNumber=tillNumber)
    g.kwikpay()
    image=request.build_absolute_uri(g.imagePath)
    return JsonResponse({"image": image})

def weddingCard(request):
	"""
	data={
		x: [x coordinate],
		y: [y coordinate],
		fontSize:[FontSize],
		text:[Text to be printed],
		filename:[helloworld],
		extension:[png/jpeg],
		templatePath:[absolute path or http],
	}
	"""
	# the name to be printed
	def get(name, default=None):
		"""
			check for both data and POST requests
		"""
		return request.POST.get(name) or request.GET.get(name, default)

	templatePath=get("templatePath", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Wikipedia_meme_vector_version.svg/440px-Wikipedia_meme_vector_version.svg.png")
	self=QRGenerator(
		templatePath=templatePath
	)

	posX=get("x", self.flier.size[0]*0.37)
	posY=get("y", self.flier.size[1]*0.4)

	posXY=(int(posX), int(posY))
	fill=(0,0,0,255)
	fontSize=int(get("fontSize", "22"))
	text=get("text", get("name"))
	filename=get("filename", 'helloworld')
	extension=get('extension', 'png')

	textImage=self.addText(
			# text="Paschal Giki", 
			text=text,
			fontSize=fontSize,
			posXY=posXY,
			fill=fill,
		)
	self.save(textImage, filename=filename, extension=extension)
	image=request.build_absolute_uri(self.imagePath)
	return JsonResponse({"image": image})