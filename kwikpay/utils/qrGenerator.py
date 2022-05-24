import qrcode
import requests
from PIL import ImageDraw, ImageFont,Image
from django.conf import settings
import os
import re
import string
# settings.configure()

class QRGenerator:
	def __init__(self, 
		tillNumber=None,
		text="QR content",
		folder=os.path.join(settings.MEDIA_ROOT, "qr"),
		templatePath=None,
		):
		self.folder=folder
		self.templatePath=templatePath
		if not self.templatePath:
			self.templatePath=self.getPath("flier.png")

		# check if needs to download the template first
		self.preprocessTemplate()

		if not self.templatePath.startswith("/"):
			self.templatePath=self.getPath(self.templatePath)

		self.tillNumber=tillNumber
		self.text=text
		# if tillNumber not provided then qr content and till number are the same
		if not self.tillNumber:
			self.tillNumber=self.text

		if not self.text:
			self.text=self.tillNumber
		
		self.fontPath=os.path.join(settings.STATIC_ROOT, "fonts/ubuntu_light.ttf")
		self.flier=Image.open(self.templatePath)
		self.imagePath=None

	def preprocessTemplate(self):
		if self.templatePath and self.templatePath.startswith("http"):
			# download the image first and then proceed
			filename=self.cleanURL(self.templatePath);
			templatePath=self.getPath(f"downloads/{filename}")
			# check if it exists to avoid downloading it again
			if not os.path.exists(templatePath):
				f = open(templatePath,'wb')
				r=requests.get(self.templatePath)
				f.write(r.content)
				f.close()
			# assing the new template here
			self.templatePath=templatePath
		
	def getPath(self, file):
		return os.path.join(self.folder, file)

	def cleanURL(self, url):
		pattern = r"[{}]".format(string.punctuation) # create the pattern
		return re.sub(pattern, "", url) 

	def generateQR(self, text="Hy Man"):
		qr = qrcode.QRCode(
		    version=1,
		    error_correction=qrcode.constants.ERROR_CORRECT_L,
		    box_size=10,
		    border=4,
		)
		qr.add_data(text)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white")
		return img


	def generateImageFromText(
			self,
			text="123456789", 
			dim=(1000, 400), 
			backgroundColor="white",
			size=None
		):
		if not size:
			size=int(0.35*dim[1])
		# add extra space on the text
		font = ImageFont.truetype(self.fontPath, size=size)
		# make a blank image
		img = Image.new('RGBA', dim, backgroundColor)
		# get a drawing context
		draw = ImageDraw.Draw(img)

		textPosXY=(0, int(0.28*dim[1]))
		draw.text(textPosXY, text, fill=(0,0,0,0), font=font)
		# draw.text(textPosXY, text, (0,0,0), font=font) # this will draw text with Blackcolor and 16 size
		return img

	def merge(self, image=None, posXY=(0,0)):
		self.flier.paste(image,posXY)
		# now add the TILL number
		return self.flier

	def save(self, image=None, filename="demo_photo", extension=None):
		if not extension:
			extension=self.templatePath.split(".")[-1]

		if not image:
			image=self.flier

		imageFilePath=self.getPath(f"generated/{filename}.{extension}")
		image.save(imageFilePath, extension.upper())
		self.imagePath=f"{settings.MEDIA_URL}qr/generated/{filename}.{extension}"
		return self.imagePath

	def kwikpay(self):
		#Generate the required two images
		qrCodeImage = self.generateQR(text=self.text)\
						.resize((400, 400))

		textImage=self.generateImageFromText(text=" ".join([i for i in self.tillNumber]))\
					.resize((1000, 400))

		# add qrcode to the flier
		flierSize=self.flier.size
		qrCodeImageX=int(flierSize[0]*(140/1748))
		qrCodeImageY=int(flierSize[1]*(1385/2480))
		self.merge(qrCodeImage,(qrCodeImageX,qrCodeImageY))
		# now add the TILL number Image
		# first find its position
		qrCodeImageSize=qrCodeImage.size
		textImageX=qrCodeImageX+qrCodeImageSize[0]+20; #add padding of 20 on the x axis
		textImageY=qrCodeImageY 
		self.merge(textImage,(textImageX,textImageY))
		self.save(
			filename=self.tillNumber
			)
		return self.flier

	def addText(self, 
		text=None,
		fontSize=30, 
		posXY=(0,0), 
		fill=(255,255,255,255),
	):		# get an image
		base = Image.open(self.templatePath).convert("RGBA")
		# make a blank image for the text, initialized to transparent text color
		txt = Image.new("RGBA", base.size, (255,255,255,0))
		# get a font
		fnt = ImageFont.truetype(self.fontPath, fontSize)
		# get a drawing context
		d = ImageDraw.Draw(txt)
		# draw text, full opacity
		d.text(posXY, text, font=fnt, fill=fill)
		out = Image.alpha_composite(base, txt)
		return out
# from PIL import Image, ImageDraw, ImageFont
# # get an image
# base = Image.open(self.templatePath).convert("RGBA")

# # make a blank image for the text, initialized to transparent text color
# txt = Image.new("RGBA", base.size, (255,255,255,0))

# # get a font
# fnt = ImageFont.truetype(self.fontPath, 40)
# # get a drawing context
# d = ImageDraw.Draw(txt)

# # draw text, half opacity
# d.text((10,10), "Hello", font=fnt, fill=(255,255,255,128))
# # draw text, full opacity
# d.text((10,60), "World", font=fnt, fill=(255,255,255,255))

# out = Image.alpha_composite(base, txt)

# out.show()


