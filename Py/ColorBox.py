import os
from __main__ import qt
from __main__ import slicer

#########################################################
#
# 
comment = """

  ColorBox is a wrapper around a set of Qt widgets and other
  structures to manage show a color picker

  This class is borrowed from Editor module. It takes a vtkMRMLColorNode on
  initialization, and allows to query back the label that was selected by the
  user, for the needs of the Reporting module.

# TODO : 
"""
#
#########################################################

class ColorBox(object):

  def __init__(self, parent=None, reportNode=None, colorNode=None):
    self.colorNode = colorNode
    self.reportNode = reportNode
    self.label = reportNode.GetFindingLabel()
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setObjectName('ReportingMRMLWidget')
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
      self.create()
      p = qt.QCursor().pos()
      self.parent.setGeometry(p.x(), p.y(), 300, 700)
      self.parent.show()
      self.parent.raise_()
    else:
      self.parent = parent
      self.create()

  def create(self):
    # add a search box
    self.searchFrame = qt.QFrame(self.parent)
    self.searchFrame.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.searchFrame)
    self.searchLabel = qt.QLabel(self.searchFrame)
    self.searchLabel.setText("Search: ")
    self.searchFrame.layout().addWidget(self.searchLabel)
    self.search = qt.QLineEdit(self.searchFrame)
    self.searchFrame.layout().addWidget(self.search)

    # model and view for color table
    self.view = qt.QTreeView()
    self.view.setObjectName('EditColorTreeView')
    self.view.setEditTriggers(qt.QAbstractItemView().NoEditTriggers)
    self.parent.layout().addWidget(self.view)
    self.populateColors()
    self.search.connect('textChanged(QString)', self.populateColors)
    self.view.connect('activated(QModelIndex)', self.selected)

  def cleanup(self):
    pass

  def show(self, reportNode, colorNode):
    self.colorNode = colorNode
    self.reportNode = reportNode
    self.populateColors()
    self.parent.show()
    self.parent.raise_()

  def addRow(self,c):
    name = self.colorNode.GetColorName(c)
    lut = self.colorNode.GetLookupTable()
    rgb = lut.GetTableValue(c)
    brush = qt.QBrush()
    self.brushes.append(brush)
    color = qt.QColor()
    color.setRgb(rgb[0]*255,rgb[1]*255,rgb[2]*255)
    brush.setColor(color)

    # index
    item = qt.QStandardItem()
    item.setText(str(c))
    self.model.setItem(self.row,0,item)
    self.items.append(item)
    # color
    item = qt.QStandardItem()
    item.setData(color,1)
    self.model.setItem(self.row,1,item)
    self.items.append(item)
    # name
    item = qt.QStandardItem()
    item.setText(self.colorNode.GetColorName(c))
    self.model.setItem(self.row,2,item)
    self.items.append(item)
    self.row += 1

  def populateColors(self):
    self.brushes = []
    self.items = []
    self.model = qt.QStandardItemModel()
    self.view.setModel(self.model)
    pattern = self.search.text
    self.row = 0

    for c in xrange(self.colorNode.GetNumberOfColors()):
      name = self.colorNode.GetColorName(c)
      if name != "(none)" and name.find(pattern) >= 0:
        self.addRow(c)

    self.view.setColumnWidth(0,75)
    self.view.setColumnWidth(1,50)
    self.view.setColumnWidth(2,150)
    self.model.setHeaderData(0,1,"Number")
    self.model.setHeaderData(1,1,"Color")
    self.model.setHeaderData(2,1,"Name")

  def selected(self, modelIndex):
    self.label = self.model.item(modelIndex.row(),0).text()
    labelNumber = int(self.label)
    if self.reportNode:
      self.reportNode.SetFindingLabel(labelNumber)
    self.parent.hide()
