# encoding: utf-8
# Draws a circle at your cursor, define the dimenions in the Dimensions palette and the Font Note
# By Wei Huang, 2016 with many thanks to Georg Seifert for assistance, and Dinamo for the idea

from GlyphsApp.plugins import *
import traceback
from AppKit import NSCursor
import os, math
import Quartz
import traceback
from AppKit import NSColor, NSBezierPath

class gaugeTool(SelectTool):
	def settings(self):
		self.name = u'Gauge Tool'
		self.keyboardShortcut = 'c'

		self.toolbarPosition = 250

		osource_image = os.path.join(os.path.dirname(__file__), 'toolbaro.pdf')
		self.oImage = NSImage.alloc().initByReferencingFile_(osource_image)
		self.oImage.setTemplate_(True)

		nsource_image = os.path.join(os.path.dirname(__file__), 'toolbarn.pdf')
		self.nImage = NSImage.alloc().initByReferencingFile_(nsource_image)
		self.nImage.setTemplate_(True)

		self.activeToolIndex = Glyphs.intDefaults["GaugeToolActiveTool"]

		self.lastScale = -1

	def foreground(self, layer):
		pass

	def mousePosition(self):
		view = self.controller.graphicView()
		mousePosition = view.getActiveLocation_(Glyphs.currentEvent())
		return mousePosition

	def foregroundInViewCoords(self, layer):
		pass

	def background(self, layer):
		self.makeCursor()
		try:
			thisGlyphName = Glyphs.font.selectedLayers[0].parent.name
			# not uppercase or lowercase
			cursorText = u"X"
			if Glyphs.glyphInfoForName( str(thisGlyphName) ).subCategory not in ["Lowercase", "Uppercase"]:
				cursorText = u"?"
			# curve
			elif self.activeToolIndex == 0:
				cursorText = u"●"
			# linear
			elif self.activeToolIndex == 1:
				cursorText = u"+"

			mousePosition = self.mousePosition()

			scale = self.getScale()
			string = NSString.stringWithString_(u"%s" % cursorText)
			attributes = NSString.drawTextAttributes_(NSColor.blackColor())
			textSize = string.sizeWithAttributes_(attributes)

			self.drawText( string, (mousePosition.x, mousePosition.y))

		except:
			print traceback.format_exc()

	def activate(self):
		self.makeCursor()

	def deactivate(self):
		pass

	def activateGaugeToolO(self):
		self.activeToolIndex = 0
		Glyphs.intDefaults["GaugeToolActiveTool"] = self.activeToolIndex
		self.makeCursor()

	def activateGaugeToolN(self):
		self.activeToolIndex = 1
		Glyphs.intDefaults["GaugeToolActiveTool"] = self.activeToolIndex
		self.makeCursor()

	def selectNextSubTool_(self, sender):
		# is called when the user presses shift + the self.keyboardShortcut to access all subtools by keyboard
		if self.activeToolIndex == 0:
			self.activateGaugeToolN()
		else:
			self.activateGaugeToolO()

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
	def makeCursor(self):
		try:
			Scale = Glyphs.font.currentTab.scale
			if abs(Scale - self.lastScale) < 0.001:
				return
			# x, y = 100, 100
			x, y, circleCursorColor = self.getCursorSize()
			if x > 0 and y > 0:
				ImageSize = NSMakeSize(math.ceil(x * Scale), math.ceil(y * Scale))
				# print math.ceil(x * Scale), math.ceil(y * Scale)
				circleCursorImage = NSImage.alloc().initWithSize_(ImageSize)
				circleCursorImage.lockFocus()
				rect = NSMakeRect(0, 0, x * Scale, y * Scale)
				# circleCursorColor = 0.5, 0.5, 0.5, 0.9
				NSColor.colorWithCalibratedRed_green_blue_alpha_( *circleCursorColor ).set()
				NSBezierPath.bezierPathWithOvalInRect_(rect).fill()
				circleCursorImage.unlockFocus()
				self.circleCursor = NSCursor.alloc().initWithImage_hotSpot_(circleCursorImage, NSMakePoint(x / 2 * Scale, y / 2 * Scale))
				try:
					self.editViewController().graphicView().setCursor_(self.circleCursor)
				except:
					pass
		except Exception as e:
			print traceback.format_exc()

	# Method to change the cursor
	def standardCursor(self):
		try:
			return self.circleCursor
		except Exception as e:
			self.makeCursor()
			self.logToConsole( "gaugeTool standardCursor: %s" % str(e) )

	# Sets the menu toolbar with multiple tools
	def toolbarMenu(self):
		try:
			theMenu = NSMenu.alloc().initWithTitle_(self.title())

			newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Gauge Tool n", self.activateGaugeToolN, "")
			newMenuItem.setTarget_(self)
			newMenuItem.setImage_(self.nImage) # it has to be an NSImage, this is optional
			theMenu.addItem_(newMenuItem)

			newMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Gauge Tool o", self.activateGaugeToolO, "") # self.setErease is a method in your plugin class
			newMenuItem.setTarget_(self)
			newMenuItem.setImage_(self.oImage) # it has to be an NSImage, this is optional
			theMenu.addItem_(newMenuItem)

			return theMenu;
		except Exception as e:
			self.logToConsole( "gaugeTool toolbarMenu: %s" % str(e))

	# Gets the dimensinos from the Font Note parameter, the first line of the note, in the following format:
	# 100, 100
	def getFontNoteXY(self):
		try:
			fontNote = Glyphs.font.note.split('\n', 1)[0]
			pos = fontNote.find(",")
			return int(fontNote[:pos]), int(fontNote[pos+1:])
		except:
			return 5, 5
			print "gaugeTool can't find any values to use...!"

	# Gets the cursor size using the dimensions palette
	def getCursorSize(self):
		try:
			thisFontMaster = Glyphs.font.selectedFontMaster
			thisFontMasterID = thisFontMaster.id
			Dimensions = Glyphs.font.userData["GSDimensionPlugin.Dimensions"][thisFontMasterID]

			thisGlyphName = Glyphs.font.selectedLayers[0].parent.name

			if Glyphs.glyphInfoForName( str(thisGlyphName) ).subCategory == "Lowercase":
				# Use the dimensions from o for lowercase
				if self.activeToolIndex == 0:
					return int(Dimensions["oV"]), int(Dimensions["oH"]), (0, 0.5, 0, 0.4)
				# Use the dimensions from n for lowercase
				elif self.activeToolIndex == 1:
					return int(Dimensions["nV"]), int(Dimensions["nd"]), (0, 0, 0.5, 0.4)

			elif Glyphs.glyphInfoForName( str(thisGlyphName) ).subCategory == "Uppercase":
				# Use the dimensions from O for uppercase
				if self.activeToolIndex == 0:
					circleCursorColor = (0, 0.5, 0, 0.4)
					return int(Dimensions["OV"]), int(Dimensions["OH"]), circleCursorColor
				# Use the dimensions from H for uppercase
				elif self.activeToolIndex == 1:
					circleCursorColor = (0, 0, 0.5, 0.4)
					return int(Dimensions["HV"]), int(Dimensions["HH"]), circleCursorColor

			else:
				try: 
					[x, y] = thisFontMaster.customParameters['gaugeDimensions'].split(",")
				except:
					x, y = self.getFontNoteXY()
				return int(x), int(y), (0.5, 0, 0, 0.4)
		except Exception as e:
			try:
				[x, y] = thisFontMaster.customParameters['gaugeDimensions'].split(",")
			except:
				x, y = self.getFontNoteXY()
			return int(x), int(y), (0.5, 0, 0, 0.4)

	def drawText( self, text, textPosition, fontColor=NSColor.whiteColor() ):
		try:
			string = NSString.stringWithString_(text)
			string.drawAtPoint_color_alignment_(textPosition, fontColor, 4)
		except:
			print traceback.format_exc()

	def getScale( self ):
		try:
			return self._scale
		except:
			return 1 # Attention, just for debugging!

	def logToConsole( self, message ):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole( "bla bla" ) for debugging.
		"""
		myLog = "%s:\n%s" % ( "Gauge Tool", message )
		print myLog
		NSLog( myLog )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__