# encoding: utf-8
# Draws a circle at your cursor using the values in the dimensions palette, or from the fall back as defined in as a Master parameter "GaugeTool" with  the format width,height i.e.
# (
#     {
#         gaugeDimensions = "500,500";
#     }
# )
# By Wei Huang, 2016–2018 with many thanks to Georg Seifert for assistance, and Dinamo for the idea

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import traceback
import os, math
import traceback
from Foundation import NSString
from AppKit import NSCursor

try:
	from GlyphsApp import GSUppercase, GSLowercase
except: pass

def glyphCase(glyph):
	if Glyphs.buildNumber > 3000:
		if glyph.case == GSUppercase:
			return "Uppercase"
		if glyph.case == GSLowercase:
			return "Lowercase"
		return "NoCase"
	else:
		return glyph.subCategory

class gaugeTool(SelectTool):
	@objc.python_method
	def settings(self):
		self.name = u'Gauge Tool'
		self.keyboardShortcut = 'c'

		self.toolbarPosition = 250
		self._icon = None
		osource_image = os.path.join(os.path.dirname(__file__), 'toolbaro.pdf')
		self.oImage = NSImage.alloc().initByReferencingFile_(osource_image)
		self.oImage.setTemplate_(True)

		nsource_image = os.path.join(os.path.dirname(__file__), 'toolbarn.pdf')
		self.nImage = NSImage.alloc().initByReferencingFile_(nsource_image)
		self.nImage.setTemplate_(True)

		self.activeToolIndex = Glyphs.intDefaults["GaugeToolActiveTool"]

		self.lastScale = -1

	@objc.python_method
	def foreground(self, layer):
		pass

	@objc.python_method
	def mousePosition(self):
		# view = self.controller.graphicView()
		view = Glyphs.font.currentTab.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition

	@objc.python_method
	def foregroundInViewCoords(self, layer):
		pass

	@objc.python_method
	def background(self, layer):
		self.makeCursor()

	def activate(self):
		self.makeCursor()

	def deactivate(self):
		pass

	def activateGaugeToolO_(self, sender):
		self.activeToolIndex = 0
		Glyphs.intDefaults["GaugeToolActiveTool"] = self.activeToolIndex
		self.makeCursor()

	def activateGaugeToolN_(self, sender):
		self.activeToolIndex = 1
		Glyphs.intDefaults["GaugeToolActiveTool"] = self.activeToolIndex
		self.makeCursor()

	def selectNextSubTool_(self, sender):
		# is called when the user presses shift + the self.keyboardShortcut to access all subtools by keyboard
		if self.activeToolIndex == 0:
			self.activateGaugeToolN_(None)
		else:
			self.activateGaugeToolO_(None)

	def toolBarIcon(self):
		# o tool
		if self.activeToolIndex == 0:
			return self.oImage
		# n tool
		if self.activeToolIndex == 1:
			return self.nImage

	# # Disable cursor select point
	# def selectAtPoint_withModifier_(self, aPoint, modifierFlag):
	# 	pass

	# # Disable cursor marquee select
	# def selectInRect_withModifier_(self, aRect, modifierFlag):
	# 	pass

	# # Disable cursor marquee
	# def drawSelection(self):
	# 	pass

	def mouseMoved_(self, theEvent):
		pass

	# Sets the cursor as a circle cursor
	@objc.python_method
	def makeCursor(self):
		try:
			Scale = Glyphs.font.currentTab.scale
			if abs(Scale - self.lastScale) < 0.001:
				return
			# x, y = 100, 100
			x, y, circleCursorColor = self.getCursorSize()
			# print("__getCursorSize", x, y, circleCursorColor)
			if x > 0 and y > 0:
				ImageSize = NSMakeSize(math.ceil(x * Scale), math.ceil(y * Scale))
				# print(math.ceil(x * Scale), math.ceil(y * Scale))
				circleCursorImage = NSImage.alloc().initWithSize_(ImageSize)
				circleCursorImage.lockFocus()
				rect = NSMakeRect(0, 0, x * Scale, y * Scale)
				# circleCursorColor = 0.5, 0.5, 0.5, 0.9
				NSColor.colorWithCalibratedRed_green_blue_alpha_(*circleCursorColor).set()
				NSBezierPath.bezierPathWithOvalInRect_(rect).fill()

				try:
					fontSize = 18
					fontAttributes = {
						#NSFontAttributeName: NSFont.labelFontOfSize_(10.0),
						NSFontAttributeName: NSFont.systemFontOfSize_weight_(fontSize,0.0),
						NSForegroundColorAttributeName: NSColor.blackColor()
					}
					displayText = NSAttributedString.alloc().initWithString_attributes_(self.getCursorType(circleCursorColor), fontAttributes)
					textAlignment = 4 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
					#font = layer.parent.parent
					displayText.drawAtPoint_alignment_(NSMakePoint(0 + x * Scale / 2, 0 + y * Scale / 2), textAlignment)
				except:
					print(traceback.format_exc())

				circleCursorImage.unlockFocus()
				self.circleCursor = NSCursor.alloc().initWithImage_hotSpot_(circleCursorImage, NSMakePoint(x / 2 * Scale, y / 2 * Scale))
				try:
					if self.editViewController().graphicView().cursor() != self.circleCursor:
						self.editViewController().graphicView().setCursor_(self.circleCursor) 
				except:
					pass
		except Exception as e:
			print(traceback.format_exc())

	# Method to change the cursor
	@objc.python_method
	def standardCursor(self):
		try:
			return self.circleCursor
		except Exception as e:
			self.makeCursor()
			self.logToConsole("gaugeTool standardCursor: %s" % str(e))

	# Sets the menu toolbar with multiple tools
	def toolbarMenu(self):
		try:
			theMenu = NSMenu.alloc().initWithTitle_(self.title())

			newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Gauge Tool n", self.activateGaugeToolN_, "")
			newMenuItem.setTarget_(self)
			newMenuItem.setImage_(self.nImage) # it has to be an NSImage, this is optional
			theMenu.addItem_(newMenuItem)

			newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Gauge Tool o", self.activateGaugeToolO_, "") # self.setErease is a method in your plugin class
			newMenuItem.setTarget_(self)
			newMenuItem.setImage_(self.oImage) # it has to be an NSImage, this is optional
			theMenu.addItem_(newMenuItem)

			return theMenu;
		except Exception as e:
			self.logToConsole("gaugeTool toolbarMenu: %s" % str(e))

	noValueColour = (0.5, 0.5, 0.5, 0.1) # grey
	customParameterColour = (0.5, 0, 0, 0.4) # red
	roundToolColour = (0, 0.5, 0, 0.4) # green
	straightToolColour = (0, 0, 0.5, 0.4) # blue

	# Gets the cursor type, round stem or straight stem
	@objc.python_method
	def getCursorType(self, circleCursorColor):
		# glyph = Glyphs.font.selectedLayers[0].parent
		# not uppercase or lowercase
		cursorText = u"X"
		if circleCursorColor == self.noValueColour:
			cursorText = u"?"
		elif circleCursorColor == self.customParameterColour:
			cursorText = u"✳"
		# curve
		elif self.activeToolIndex == 0:
			cursorText = u"○"
		# linear
		elif self.activeToolIndex == 1:
			cursorText = u"＋"

		return cursorText

	# Gets the dimensinos from the Font Note parameter, the first line of the note, in the following format:
	# 100, 100
	@objc.python_method
	def getFontNoteXY(self):
		try:
			fontNote = Glyphs.font.note.split('\n', 1)[0]
			pos = fontNote.find(",")
			return int(fontNote[:pos]), int(fontNote[pos+1:])
		except:
			return 50, 50
			print("gaugeTool can't find any values to use...!")

	# Gets the cursor size using the dimensions palette
	@objc.python_method
	def getCursorSize(self):
		try:
			font = Glyphs.font
			thisFontMaster = font.selectedFontMaster
			thisFontMasterID = thisFontMaster.id
			Dimensions = font.userData["GSDimensionPlugin.Dimensions"][thisFontMasterID]
			glyph = font.selectedLayers[0].parent
			thisGlyphName = glyph.name
			case = glyphCase(glyph)
			if case == "Lowercase":
				# Use the dimensions from o for lowercase
				if self.activeToolIndex == 0:
					return int(Dimensions.get("oV", 50)), int(Dimensions.get("oH", 50)), self.roundToolColour
				# Use the dimensions from n for lowercase
				elif self.activeToolIndex == 1:
					return int(Dimensions.get("nV", 50)), int(Dimensions.get("nd", 50)), self.straightToolColour

			elif case == "Uppercase":
				# Use the dimensions from O for uppercase
				if self.activeToolIndex == 0:
					return int(Dimensions.get("OV", 50)), int(Dimensions.get("OH", 50)), self.roundToolColour
				# Use the dimensions from H for uppercase
				elif self.activeToolIndex == 1:
					return int(Dimensions.get("HV", 50)), int(Dimensions.get("HH", 50)), self.straightToolColour
			else:
				try:
					[x, y] = thisFontMaster.customParameters['GaugeTool'].split(",")
				except:
					try:
						[x, y] = thisFontMaster.customParameters['gaugeTool'].split(",")
					except:
						x, y = self.getFontNoteXY()	
						return x, y, self.noValueColour
				return int(x), int(y), self.customParameterColour
		except Exception as e:
			print(traceback.format_exc())
			try:
				[x, y] = thisFontMaster.customParameters['GaugeTool'].split(",")
			except:
				try:
					[x, y] = thisFontMaster.customParameters['gaugeTool'].split(",")
				except:
					x, y = self.getFontNoteXY()
					return x, y, self.noValueColour
			return int(x), int(y), self.customParameterColour

	@objc.python_method
	def drawText(self, text, textPosition, fontColor=NSColor.blackColor()):
		try:
			string = NSString.stringWithString_(text)
			string.drawAtPoint_color_alignment_(textPosition, fontColor, 4)
		except:
			print(traceback.format_exc())

	@objc.python_method
	def getScale(self):
		try:
			return self._scale
		except:
			return 1 # Attention, just for debugging!

	@objc.python_method
	def logToConsole(self, message):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole("bla bla") for debugging.
		"""
		myLog = "%s:\n%s" % ("Gauge Tool", message)
		print(myLog)
		NSLog(myLog)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
