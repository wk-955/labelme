# -*- coding: utf-8 -*-

import functools
import json
import math
import os
import os.path as osp
import re
import webbrowser

import imgviz
from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy import QtWidgets

from labelme import __appname__
from labelme import PY2
from labelme import QT5

from . import utils
from labelme.config import get_config
from labelme.label_file import LabelFile
from labelme.label_file import LabelFileError
from labelme.logger import logger
from labelme.shape import Shape
from labelme.widgets import BrightnessContrastDialog
from labelme.widgets import Canvas
from labelme.widgets import LabelDialog
from labelme.widgets import LabelListWidget
from labelme.widgets import LabelListWidgetItem
from labelme.widgets import ToolBar
from labelme.widgets import UniqueLabelQListWidget
from labelme.widgets import ZoomWidget

from functools import reduce

import base64
from PIL import Image

from CalAll import CalAll
from CalAuto import CalAuto


# FIXME
# - [medium] Set max zoom value to something big enough for FitWidth/Window

# TODO(unknown):
# - [high] Add polygon movement with arrow keys
# - [high] Deselect shape when clicking and already selected(?)
# - [low,maybe] Preview images on file dialogs.
# - Zoom is too "steppy".


LABEL_COLORMAP = imgviz.label_colormap(value=200)


class MainWindow(QtWidgets.QMainWindow):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = 0, 1, 2

    def __init__(
            self,
            config=None,
            filename=None,
            output=None,
            output_file=None,
            output_dir=None,
    ):
        if output is not None:
            logger.warning(
                "argument output is deprecated, use output_file instead"
            )
            if output_file is None:
                output_file = output

        # see labelme/config/default_config.yaml for valid configuration
        if config is None:
            config = get_config()
        self._config = config

        # set default shape colors
        Shape.line_color = QtGui.QColor(*self._config["shape"]["line_color"])
        Shape.fill_color = QtGui.QColor(*self._config["shape"]["fill_color"])
        Shape.select_line_color = QtGui.QColor(
            *self._config["shape"]["select_line_color"]
        )
        Shape.select_fill_color = QtGui.QColor(
            *self._config["shape"]["select_fill_color"]
        )
        Shape.vertex_fill_color = QtGui.QColor(
            *self._config["shape"]["vertex_fill_color"]
        )
        Shape.hvertex_fill_color = QtGui.QColor(
            *self._config["shape"]["hvertex_fill_color"]
        )

        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        # Whether we need to save or not.
        self.dirty = False

        self._noSelectionSlot = False

        # Main widgets and related state.
        self.labelDialog = LabelDialog(
            parent=self,
            labels=self._config["labels"],
            sort_labels=self._config["sort_labels"],
            show_text_field=self._config["show_label_text_field"],
            completion=self._config["label_completion"],
            fit_to_content=self._config["fit_to_content"],
            flags=self._config["label_flags"],
        )

        self.labelList = LabelListWidget()
        self.lastOpenDir = None

        self.flag_dock = self.flag_widget = None
        self.flag_dock = QtWidgets.QDockWidget(self.tr("显示标记"), self)
        self.flag_dock.setObjectName("标记")
        self.flag_widget = QtWidgets.QListWidget()
        if config["flags"]:
            self.loadFlags({k: False for k in config["flags"]})
        self.flag_dock.setWidget(self.flag_widget)
        self.flag_widget.itemChanged.connect(self.setDirty)

        self.labelList.itemSelectionChanged.connect(self.labelSelectionChanged)
        self.labelList.itemDoubleClicked.connect(self.editLabel)
        self.labelList.itemChanged.connect(self.labelItemChanged)
        self.labelList.itemDropped.connect(self.labelOrderChanged)
        self.shape_dock = QtWidgets.QDockWidget(
            self.tr("显示标签"), self
        )
        self.shape_dock.setObjectName("标签")
        self.shape_dock.setWidget(self.labelList)

        self.uniqLabelList = UniqueLabelQListWidget()
        self.uniqLabelList.setToolTip(
            self.tr(
                "Select label to start annotating for it. "
                "Press 'Esc' to deselect."
            )
        )
        if self._config["labels"]:
            for label in self._config["labels"]:
                item = self.uniqLabelList.createItemFromLabel(label)
                self.uniqLabelList.addItem(item)
                rgb = self._get_rgb_by_label(label)
                self.uniqLabelList.setItemLabel(item, label, rgb)
        self.label_dock = QtWidgets.QDockWidget(self.tr(u"显示标签列表"), self)
        self.label_dock.setObjectName(u"标签列表")
        self.label_dock.setWidget(self.uniqLabelList)

        self.fileSearch = QtWidgets.QLineEdit()
        self.fileSearch.setPlaceholderText(self.tr("搜索文件名"))
        self.fileSearch.textChanged.connect(self.fileSearchChanged)
        self.fileListWidget = QtWidgets.QListWidget()
        self.fileListWidget.itemSelectionChanged.connect(
            self.fileSelectionChanged
        )
        fileListLayout = QtWidgets.QVBoxLayout()
        fileListLayout.setContentsMargins(0, 0, 0, 0)
        fileListLayout.setSpacing(0)
        fileListLayout.addWidget(self.fileSearch)
        fileListLayout.addWidget(self.fileListWidget)
        self.file_dock = QtWidgets.QDockWidget(self.tr(u"显示文件列表"), self)
        self.file_dock.setObjectName(u"文件")
        fileListWidget = QtWidgets.QWidget()
        fileListWidget.setLayout(fileListLayout)
        self.file_dock.setWidget(fileListWidget)

        self.zoomWidget = ZoomWidget()
        self.setAcceptDrops(True)

        self.canvas = self.labelList.canvas = Canvas(
            epsilon=self._config["epsilon"],
            double_click=self._config["canvas"]["double_click"],
        )
        self.canvas.zoomRequest.connect(self.zoomRequest)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.canvas)
        scrollArea.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scrollArea.verticalScrollBar(),
            Qt.Horizontal: scrollArea.horizontalScrollBar(),
        }
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)

        self.setCentralWidget(scrollArea)

        features = QtWidgets.QDockWidget.DockWidgetFeatures()
        for dock in ["flag_dock", "label_dock", "shape_dock", "file_dock"]:
            if self._config[dock]["closable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetClosable
            if self._config[dock]["floatable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetFloatable
            if self._config[dock]["movable"]:
                features = features | QtWidgets.QDockWidget.DockWidgetMovable
            getattr(self, dock).setFeatures(features)
            if self._config[dock]["show"] is False:
                getattr(self, dock).setVisible(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.flag_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.label_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.shape_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.file_dock)

        # Actions
        action = functools.partial(utils.newAction, self)
        shortcuts = self._config["shortcuts"]
        quit = action(
            self.tr("退出"),
            self.close,
            shortcuts["quit"],
            "quit",
            self.tr("退出应用"),
        )
        open_ = action(
            self.tr("打开"),
            self.openFile,
            shortcuts["open"],
            "open",
            self.tr("打开图片或者label文件"),
        )
        opendir = action(
            self.tr("打开文件夹"),
            self.openDirDialog,
            shortcuts["open_dir"],
            "open",
            self.tr(u"打开文件夹"),
        )
        openNextImg = action(
            self.tr("下一张图片"),
            self.openNextImg,
            shortcuts["open_next"],
            "next",
            self.tr(u"Open next (hold Ctl+Shift to copy labels)"),
            enabled=False,
        )
        openPrevImg = action(
            self.tr("上一张图片"),
            self.openPrevImg,
            shortcuts["open_prev"],
            "prev",
            self.tr(u"Open prev (hold Ctl+Shift to copy labels)"),
            enabled=False,
        )
        save = action(
            self.tr("保存"),
            self.saveFile,
            shortcuts["save"],
            "save",
            self.tr("Save labels to file"),
            enabled=False,
        )
        saveAs = action(
            self.tr("另存为"),
            self.saveFileAs,
            shortcuts["save_as"],
            "save-as",
            self.tr("Save labels to a different file"),
            enabled=False,
        )

        deleteFile = action(
            self.tr("删除文件"),
            self.deleteFile,
            shortcuts["delete_file"],
            "delete",
            self.tr("Delete current label file"),
            enabled=False,
        )

        changeOutputDir = action(
            self.tr("改变保存路径"),
            slot=self.changeOutputDirDialog,
            shortcut=shortcuts["save_to"],
            icon="open",
            tip=self.tr(u"Change where annotations are loaded/saved"),
        )

        saveAuto = action(
            text=self.tr("自动保存"),
            slot=lambda x: self.actions.saveAuto.setChecked(x),
            icon="save",
            tip=self.tr("Save automatically"),
            checkable=True,
            enabled=True,
        )
        saveAuto.setChecked(self._config["auto_save"])

        saveWithImageData = action(
            text="保存时带图片信息",
            slot=self.enableSaveImageWithData,
            tip="Save image data in label file",
            checkable=True,
            checked=self._config["store_data"],
        )

        close = action(
            "关闭",
            self.closeFile,
            shortcuts["close"],
            "close",
            "Close current file",
        )

        toggle_keep_prev_mode = action(
            self.tr("保留上一个的标注"),
            self.toggleKeepPrevMode,
            shortcuts["toggle_keep_prev_mode"],
            None,
            self.tr('Toggle "keep pevious annotation" mode'),
            checkable=True,
        )
        toggle_keep_prev_mode.setChecked(self._config["keep_prev"])

        createMode = action(
            self.tr("创建多边形"),
            lambda: self.toggleDrawMode(False, createMode="polygon"),
            shortcuts["create_polygon"],
            "objects",
            self.tr("Start drawing polygons"),
            enabled=False,
        )
        createRectangleMode = action(
            self.tr("创建矩形"),
            lambda: self.toggleDrawMode(False, createMode="rectangle"),
            shortcuts["create_rectangle"],
            "objects",
            self.tr("Start drawing rectangles"),
            enabled=False,
        )
        createCircleMode = action(
            self.tr("创建圆形"),
            lambda: self.toggleDrawMode(False, createMode="circle"),
            shortcuts["create_circle"],
            "objects",
            self.tr("Start drawing circles"),
            enabled=False,
        )
        createLineMode = action(
            self.tr("创建线"),
            lambda: self.toggleDrawMode(False, createMode="line"),
            shortcuts["create_line"],
            "objects",
            self.tr("Start drawing lines"),
            enabled=False,
        )
        createPointMode = action(
            self.tr("创建点"),
            lambda: self.toggleDrawMode(False, createMode="point"),
            shortcuts["create_point"],
            "objects",
            self.tr("Start drawing points"),
            enabled=False,
        )
        createLineStripMode = action(
            self.tr("创建多线条"),
            lambda: self.toggleDrawMode(False, createMode="linestrip"),
            shortcuts["create_linestrip"],
            "objects",
            self.tr("Start drawing linestrip. Ctrl+LeftClick ends creation."),
            enabled=False,
        )
        editMode = action(
            self.tr("编辑多边形"),
            self.setEditMode,
            shortcuts["edit_polygon"],
            "edit",
            self.tr("Move and edit the selected polygons"),
            enabled=False,
        )

        delete = action(
            self.tr("删除多边形"),
            self.deleteSelectedShape,
            shortcuts["delete_polygon"],
            "cancel",
            self.tr("Delete the selected polygons"),
            enabled=False,
        )
        copy = action(
            self.tr("复制多边形"),
            self.copySelectedShape,
            shortcuts["duplicate_polygon"],
            "copy",
            self.tr("Create a duplicate of the selected polygons"),
            enabled=False,
        )
        undoLastPoint = action(
            self.tr("撤消上一个点"),
            self.canvas.undoLastPoint,
            shortcuts["undo_last_point"],
            "undo",
            self.tr("Undo last drawn point"),
            enabled=False,
        )
        addPointToEdge = action(
            text=self.tr("添加点到边"),
            slot=self.canvas.addPointToEdge,
            shortcut=shortcuts["add_point_to_edge"],
            icon="edit",
            tip=self.tr("Add point to the nearest edge"),
            enabled=False,
        )
        removePoint = action(
            text="删除选定点",
            slot=self.canvas.removeSelectedPoint,
            icon="edit",
            tip="Remove selected point from polygon",
            enabled=False,
        )

        undo = action(
            self.tr("撤消"),
            self.undoShapeEdit,
            shortcuts["undo"],
            "undo",
            self.tr("Undo last add and edit of shape"),
            enabled=False,
        )

        # 增加和修改
        hideAll = action(
            self.tr("隐藏所有标签"),
            functools.partial(self.togglePolygons, False),
            shortcuts["hideAll"],
            icon="eye",
            tip=self.tr("隐藏所有标签"),
            enabled=False,
        )
        showAll = action(
            self.tr("显示所有标签"),
            functools.partial(self.togglePolygons, True),
            shortcuts["showAll"],
            icon="eye",
            tip=self.tr("显示所有标签"),
            enabled=False,
        )

        show106 = action(
            self.tr('只显示106点'),
            functools.partial(self.toggleShow106, True),
            shortcuts["show106"],
            icon="eye",
            tip=self.tr("显示106点"),
            enabled=False,
        )
        show134 = action(
            self.tr('只显示134点'),
            functools.partial(self.toggleShow134, True),
            shortcuts["show134"],
            icon="eye",
            tip=self.tr("显示134点"),
            enabled=False,
        )
        show38 = action(
            self.tr('只显示40点'),
            functools.partial(self.toggleShow38, True),
            shortcuts["show38"],
            icon="eye",
            tip=self.tr("显示40点"),
            enabled=False,
        )

        showline1 = action(
            self.tr('只显示上唇(106)'),
            functools.partial(self.toggleLine, True, 1),
            icon="eye",
            tip=self.tr('只显示上唇(106)'),
            enabled=False,
        )
        showline2 = action(
            self.tr('只显示下唇(106)'),
            functools.partial(self.toggleLine, True, 2),
            icon="eye",
            tip=self.tr("只显示下唇(106)"),
            enabled=False,
        )
        showline3 = action(
            self.tr('只显示下唇(134)'),
            functools.partial(self.toggleLine, True, 3),
            icon="eye",
            tip=self.tr("只显示下唇(134)"),
            enabled=False,
        )
        showline4 = action(
            self.tr('只显示下唇(134)'),
            functools.partial(self.toggleLine, True, 4),
            icon="eye",
            tip=self.tr("只显示下唇(134)"),
            enabled=False,
        )
        showline5 = action(
            self.tr('显示所有的连线'),
            functools.partial(self.toggleLine, True, 5),
            shortcuts["showline5"],
            icon="eye",
            tip=self.tr("显示所有的连线"),
            enabled=False,
        )

        # show2 = action(
        #     self.tr('只显示2点'),
        #     functools.partial(self.RegenerateLeftPupil),
        #     shortcuts["show2"],
        #     icon="eye",
        #     tip=self.tr("显示2点"),
        #     enabled=False,
        # )
        showFaceKey = action(
            self.tr('只显示脸颊关键点'),
            functools.partial(self.toggleFaceKeyPoint, True),
            shortcuts["showFaceKey"],
            icon="eye",
            tip=self.tr("只显示脸部关键点"),
            enabled=False,
        )
        showFace = action(
            self.tr('只显示脸颊所有点'),
            functools.partial(self.toggleFace, True),
            # shortcuts["show8"],
            icon="eye",
            tip=self.tr("只显示脸部点"),
            enabled=False,
        )
        pointSort = action(
            self.tr('点位重新排序'),
            functools.partial(self.sortPoint, True),
            shortcuts["pointsort"],
            icon="eye",
            tip=self.tr("点位重新排序"),
            enabled=False,
        )
        showKeyPoint = action(
            self.tr('显示关键点(第一步)'),
            functools.partial(self.toggleKeyPoints, True),
            shortcuts["showKeyPoint"],
            icon="eye",
            tip=self.tr("显示关键点"),
            enabled=False,
        )
        showEye106 = action(
            self.tr('显示眼睛点(106)'),
            functools.partial(self.toggleEye106, True),
            shortcuts["showEye"],
            icon="eye",
            tip=self.tr("显示眼睛点(106)"),
            enabled=False,
        )
        showEye = action(
            self.tr('显示眼睛点(134)'),
            functools.partial(self.toggleEye, True),
            shortcuts["showEye"],
            icon="eye",
            tip=self.tr("显示眼睛点(134)"),
            enabled=False,
        )
        showEyebrow = action(
            self.tr('显示眉毛所有点(106和134)'),
            functools.partial(self.toggleEyebrow, True),
            shortcuts["showEyebrow"],
            icon="eye",
            tip=self.tr("只显示眉毛"),
            enabled=False,
        )
        showUpperLip = action(
            self.tr('只显示上唇'),
            functools.partial(self.toggleUpperLip, True),
            shortcuts["showUpperLip"],
            icon="eye",
            tip=self.tr("只显示上唇"),
            enabled=False,
        )
        showLowerLip = action(
            self.tr('只显示下唇'),
            functools.partial(self.toggleLowerLip, True),
            shortcuts["showLowerLip"],
            icon="eye",
            tip=self.tr("只显示下唇"),
            enabled=False,
        )
        showLip = action(
            self.tr('显示嘴唇(106和134)'),
            functools.partial(self.toggleLip, True),
            icon="eye",
            tip=self.tr("显示嘴唇(106和134)"),
            enabled=False,
        )
        showRect = action(
            self.tr('只显示遮挡框'),
            functools.partial(self.toggleRect, True),
            shortcuts["showRect"],
            icon="eye",
            tip=self.tr("只显示遮挡框"),
            enabled=False,
        )

        re_occ = action(
            self.tr('重构遮挡点'),
            functools.partial(self.ReconstructionOcclusion),
            shortcuts["ReconstructionOcclusion"],
            icon="eye",
            tip=self.tr("创建所有点"),
        )

        createFace = action(
            self.tr('生成所有脸颊点'),
            functools.partial(self.GeneratingFace),
            shortcuts["createFace"],
            icon="eye",
            tip=self.tr("生成新的脸"),
        )
        createLeftPupil = action(
            self.tr('生成新的左瞳孔'),
            functools.partial(self.RegenerateLeftPupil),
            shortcuts["createLeftPupil"],
            icon="eye",
            tip=self.tr("生成新的左瞳孔"),
        )
        createRightPupil = action(
            self.tr('生成新的右瞳孔'),
            functools.partial(self.RegenerateRightPupil),
            shortcuts["createRightPupil"],
            icon="eye",
            tip=self.tr("生成新的右瞳孔"),
        )
        createLeftupperEye = action(
            self.tr('生成新的左眼睛上位点(134)'),
            functools.partial(self.GeneratingLeftupperEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的左眼睛上位点"),
        )
        createLeftlowerEye = action(
            self.tr('生成新的左眼睛下位点(134)'),
            functools.partial(self.GeneratingLeftLowerEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的左眼睛下位点"),
        )
        createRightupperEye = action(
            self.tr('生成新的右眼睛上位点(134)'),
            functools.partial(self.GeneratingRightupperEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的右眼睛上位点"),
        )
        createRightlowerEye = action(
            self.tr('生成新的右眼睛下位点(134)'),
            functools.partial(self.GeneratingRightLowerEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的右眼睛下位点"),
        )
        createLeftEye = action(
            self.tr('生成新的左眼睛(134)'),
            functools.partial(self.GeneratingLeftEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的左眼睛"),
        )
        createRightEye = action(
            self.tr('生成新的右眼睛(134)'),
            functools.partial(self.GeneratingRightEye),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成新的右眼睛"),
        )
        createEyeMid = action(
            self.tr('生成眼睛74和77点(106)'),
            functools.partial(self.GeneratingEyeMid),
            # shortcuts["createLeftupperEye"],
            icon="eye",
            tip=self.tr("生成眼睛74和77点(106)"),
        )
        createEye = action(
            self.tr('生成新的眼睛(全部(134))'),
            functools.partial(self.GeneratingEye),
            shortcuts["createEye"],
            icon="eye",
            tip=self.tr("生成新的眼睛(全部)"),
        )
        mergePoints = action(
            self.tr('只合并关键点(106和134)'),
            functools.partial(self.MergeKeyPoints),
            shortcuts["mergePoints"],
            icon="eye",
            tip=self.tr("合并关键点"),
        )

        createEyebrow = action(
            self.tr('生成眉毛等分点(134)'),
            functools.partial(self.GeneratingEyebrowPoints),
            shortcuts["createEyebrow"],
            icon="eye",
            tip=self.tr("生成眉毛等分点(134)"),
        )
        createEyebrow106 = action(
            self.tr('生成眉毛等分点(106)'),
            functools.partial(self.GeneratingEyebrowPoints106),
            # shortcuts["createEyebrow"],
            icon="eye",
            tip=self.tr("生成眉毛等分点(106)"),
        )
        createUpperlip = action(
            self.tr('生成上嘴唇等分点(134)'),
            functools.partial(self.GeneratingUpperlipPoints),
            shortcuts["createUpperlip"],
            icon="eye",
            tip=self.tr("生成上嘴唇等分点(134)"),
        )
        createLowerlip = action(
            self.tr('生成下嘴唇等分点(134)'),
            functools.partial(self.GeneratingLowerlipPoints),
            shortcuts["createLowerlip"],
            icon="eye",
            tip=self.tr("生成下嘴唇等分点(134)"),
        )
        createKeypoints = action(
            self.tr('生成嘴唇等分点(134)'),
            functools.partial(self.GeneratingBisectors),
            shortcuts["createKeypoints"],
            icon="eye",
            tip=self.tr("生成嘴唇等分点(134)"),
        )

        mergeAndCreate = action(
            self.tr('等分134点(第三步)'),
            functools.partial(self.MegrgeAndBisect),
            shortcuts["mergeAndCreate"],
            icon="eye",
            tip=self.tr("合并关键点并创建嘴唇等分点"),
        )
        restructure = action(
            self.tr('等分106点(第二步)'),
            functools.partial(self.restructure106),
            shortcuts["restructure"],
            icon="eye",
            tip=self.tr("等分重构106点"),
        )

        createPoint = action(
            self.tr('创建所有点'),
            functools.partial(self.CreateAll),
            shortcuts["createPoint"],
            icon="eye",
            tip=self.tr("创建所有点"),
        )
        RePoint = action(
            self.tr('重置普通点'),
            functools.partial(self.ResetPoint),
            shortcuts["RePoint"],
            icon="eye",
            tip=self.tr("重置普通点"),
        )

        help = action(
            self.tr("帮助"),
            self.tutorial,
            icon="help",
            tip=self.tr("Show tutorial page"),
        )

        zoom = QtWidgets.QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            self.tr(
                "Zoom in or out of the image. Also accessible with "
                "{} and {} from the canvas."
            ).format(
                utils.fmtShortcut(
                    "{},{}".format(shortcuts["zoom_in"], shortcuts["zoom_out"])
                ),
                utils.fmtShortcut(self.tr("Ctrl+Wheel")),
            )
        )
        self.zoomWidget.setEnabled(False)

        zoomIn = action(
            self.tr("放大"),
            functools.partial(self.addZoom, 1.1),
            shortcuts["zoom_in"],
            "zoom-in",
            self.tr("Increase zoom level"),
            enabled=False,
        )
        zoomOut = action(
            self.tr("缩小"),
            functools.partial(self.addZoom, 0.9),
            shortcuts["zoom_out"],
            "zoom-out",
            self.tr("Decrease zoom level"),
            enabled=False,
        )
        zoomOrg = action(
            self.tr("原始尺寸"),
            functools.partial(self.setZoom, 100),
            shortcuts["zoom_to_original"],
            "zoom",
            self.tr("Zoom to original size"),
            enabled=False,
        )
        fitWindow = action(
            self.tr("适应窗口"),
            self.setFitWindow,
            shortcuts["fit_window"],
            "fit-window",
            self.tr("Zoom follows window size"),
            checkable=True,
            enabled=False,
        )
        fitWidth = action(
            self.tr("适应宽度"),
            self.setFitWidth,
            shortcuts["fit_width"],
            "fit-width",
            self.tr("Zoom follows window width"),
            checkable=True,
            enabled=False,
        )
        brightnessContrast = action(
            "亮度对比度",
            self.brightnessContrast,
            None,
            "color",
            "Adjust brightness and contrast",
            enabled=False,
        )
        # Group zoom controls into a list for easier toggling.
        zoomActions = (
            self.zoomWidget,
            zoomIn,
            zoomOut,
            zoomOrg,
            fitWindow,
            fitWidth,
        )
        self.zoomMode = self.FIT_WINDOW
        fitWindow.setChecked(Qt.Checked)
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }

        edit = action(
            self.tr("编辑标签"),
            self.editLabel,
            shortcuts["edit_label"],
            "edit",
            self.tr("Modify the label of the selected polygon"),
            enabled=False,
        )

        fill_drawing = action(
            self.tr("填充多边形"),
            self.canvas.setFillDrawing,
            None,
            "color",
            self.tr("Fill polygon while drawing"),
            checkable=True,
            enabled=True,
        )
        toggleLabel = action(
            self.tr('显示\隐藏标签'),
            self.enableToggleLabel,
            checkable=True,
            checked=self._config["toggle"],
        )
        toggleLine = action(
            self.tr('显示\取消连线'),
            self.enableToggleLine,
            checkable=True,
            checked=self._config["toggleLine"],
        )

        fill_drawing.trigger()

        # Lavel list context menu.
        labelMenu = QtWidgets.QMenu()
        utils.addActions(labelMenu, (edit, delete))
        self.labelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(
            self.popLabelListMenu
        )

        # Store actions for further handling.
        self.actions = utils.struct(
            toggleLabel=toggleLabel,
            saveAuto=saveAuto,
            saveWithImageData=saveWithImageData,
            changeOutputDir=changeOutputDir,
            save=save,
            saveAs=saveAs,
            open=open_,
            close=close,
            deleteFile=deleteFile,
            toggleKeepPrevMode=toggle_keep_prev_mode,
            delete=delete,
            edit=edit,
            copy=copy,
            undoLastPoint=undoLastPoint,
            undo=undo,
            addPointToEdge=addPointToEdge,
            removePoint=removePoint,
            createMode=createMode,
            editMode=editMode,
            createRectangleMode=createRectangleMode,
            createCircleMode=createCircleMode,
            createLineMode=createLineMode,
            createPointMode=createPointMode,
            createLineStripMode=createLineStripMode,
            zoom=zoom,
            zoomIn=zoomIn,
            zoomOut=zoomOut,
            zoomOrg=zoomOrg,
            fitWindow=fitWindow,
            fitWidth=fitWidth,
            brightnessContrast=brightnessContrast,
            zoomActions=zoomActions,
            openNextImg=openNextImg,
            openPrevImg=openPrevImg,
            fileMenuActions=(open_, opendir, save, saveAs, close, quit),
            tool=(),
            # XXX: need to add some actions here to activate the shortcut
            editMenu=(
                edit,
                copy,
                delete,
                None,
                undo,
                undoLastPoint,
                None,
                addPointToEdge,
                None,
                toggle_keep_prev_mode,
            ),
            # menu shown at right click
            menu=(
                createMode,
                createRectangleMode,
                createCircleMode,
                createLineMode,
                createPointMode,
                createLineStripMode,
                editMode,
                edit,
                copy,
                delete,
                undo,
                undoLastPoint,
                addPointToEdge,
                removePoint,
            ),
            onLoadActive=(
                close,
                createMode,
                createRectangleMode,
                createCircleMode,
                createLineMode,
                createPointMode,
                createLineStripMode,
                editMode,
                brightnessContrast,
            ),
            onShapesPresent=(saveAs, hideAll, showAll, show106, show134, show38, showEye106, showKeyPoint, pointSort,
                             showFace, showFaceKey,
                             showUpperLip, showLowerLip, showRect, showEyebrow, showEye, showLip,
                             showline1, showline2, showline3, showline4, showline5),
        )

        self.canvas.edgeSelected.connect(self.canvasShapeEdgeSelected)
        self.canvas.vertexSelected.connect(self.actions.removePoint.setEnabled)

        self.menus = utils.struct(
            file=self.menu(self.tr("文件")),
            edit=self.menu(self.tr("编辑")),
            view=self.menu(self.tr("视图")),
            KeyPoints=self.menu(self.tr("关键点合并")),
            Face=self.menu(self.tr("脸部")),
            Eyebrow=self.menu(self.tr("眉毛点")),
            Eye=self.menu(self.tr("眼睛点")),
            Pupil=self.menu(self.tr("瞳孔点")),
            Lips=self.menu(self.tr("嘴唇点")),
            Auto=self.menu(self.tr("创建点")),
            Line=self.menu(self.tr("连线")),
            ReOcc=self.menu(self.tr("重构遮挡点")),
            recentFiles=QtWidgets.QMenu(self.tr("打开最近的")),
            labelList=labelMenu,
        )

        utils.addActions(
            self.menus.file,
            (
                open_,
                openNextImg,
                openPrevImg,
                opendir,
                self.menus.recentFiles,
                save,
                saveAs,
                saveAuto,
                changeOutputDir,
                saveWithImageData,
                close,
                deleteFile,
                None,
                quit,
            ),
        )
        utils.addActions(self.menus.KeyPoints, (
            pointSort,
            showKeyPoint,
            restructure,
            mergeAndCreate,
            mergePoints,
        ))
        utils.addActions(self.menus.Face, (
            showFaceKey,
            showFace,
            createFace
        ))
        utils.addActions(self.menus.Eyebrow, (
            showEyebrow,
            createEyebrow106,
            createEyebrow,
        ))
        utils.addActions(self.menus.Eye, (
            showEye106,
            showEye,
            createLeftupperEye,
            createLeftlowerEye,
            createRightupperEye,
            createRightlowerEye,
            createLeftEye,
            createRightEye,
            createEyeMid,
            createEye
        ))
        utils.addActions(self.menus.Pupil, (
            show38,
            createLeftPupil,
            createRightPupil,
        ))
        utils.addActions(self.menus.Lips, (
            showUpperLip,
            showLowerLip,
            showLip,
            createUpperlip,
            createLowerlip,
            createKeypoints,
        ))
        utils.addActions(self.menus.Auto, (
            createPoint,
            RePoint
        ))
        utils.addActions(self.menus.ReOcc, (
            re_occ,
        ))
        utils.addActions(self.menus.Line, (
            showline1,
            showline2,
            showline3,
            showline4,
            showline5
        ))

        utils.addActions(
            self.menus.view,
            (
                self.flag_dock.toggleViewAction(),
                self.label_dock.toggleViewAction(),
                self.shape_dock.toggleViewAction(),
                self.file_dock.toggleViewAction(),
                None,
                fill_drawing,
                None,
                showAll,
                hideAll,
                None,
                zoomIn,
                zoomOut,
                zoomOrg,
                None,
                fitWindow,
                fitWidth,
                None,
                brightnessContrast,
                None,
                show106,
                show134,
                show38,
                showUpperLip,
                showLowerLip,
                showRect,
                None,
                toggleLabel,
                toggleLine
            ),
        )

        self.menus.file.aboutToShow.connect(self.updateFileMenu)

        # Custom context menu for the canvas widget:
        utils.addActions(self.canvas.menus[0], self.actions.menu)
        utils.addActions(
            self.canvas.menus[1],
            (
                action("&Copy here", self.copyShape),
                action("&Move here", self.moveShape),
            ),
        )

        self.tools = self.toolbar("Tools")
        # Menu buttons on Left
        self.actions.tool = (
            open_,
            opendir,
            openNextImg,
            openPrevImg,
            save,
            deleteFile,
            None,
            createMode,
            editMode,
            copy,
            delete,
            undo,
            # brightnessContrast,
            None,
            zoom,
            fitWidth,
            None,
            showKeyPoint,
            show106,
            show134,
            show38,
            showUpperLip,
            showLowerLip,
            showRect
        )

        self.statusBar().showMessage(self.tr("%s started.") % __appname__)
        self.statusBar().show()

        if output_file is not None and self._config["auto_save"]:
            logger.warn(
                "If `auto_save` argument is True, `output_file` argument "
                "is ignored and output filename is automatically "
                "set as IMAGE_BASENAME.json."
            )
        self.output_file = output_file
        self.output_dir = output_dir

        # Application state.
        self.image = QtGui.QImage()
        self.imagePath = None
        self.recentFiles = []
        self.maxRecent = 7
        self.otherData = None
        self.zoom_level = 100
        self.fit_window = False
        self.zoom_values = {}  # key=filename, value=(zoom_mode, zoom_value)
        self.brightnessContrast_values = {}
        self.scroll_values = {
            Qt.Horizontal: {},
            Qt.Vertical: {},
        }  # key=filename, value=scroll_value

        if filename is not None and osp.isdir(filename):
            self.importDirImages(filename, load=False)
        else:
            self.filename = filename

        if config["file_search"]:
            self.fileSearch.setText(config["file_search"])
            self.fileSearchChanged()

        # XXX: Could be completely declarative.
        # Restore application settings.
        self.settings = QtCore.QSettings("labelme", "labelme")
        # FIXME: QSettings.value can return None on PyQt4
        self.recentFiles = self.settings.value("recentFiles", []) or []
        size = self.settings.value("window/size", QtCore.QSize(600, 500))
        position = self.settings.value("window/position", QtCore.QPoint(0, 0))
        self.resize(size)
        self.move(position)
        # or simply:
        # self.restoreGeometry(settings['window/geometry']
        self.restoreState(
            self.settings.value("window/state", QtCore.QByteArray())
        )

        # Populate the File menu dynamically.
        self.updateFileMenu()
        # Since loading the file may take some time,
        # make sure it runs in the background.
        if self.filename is not None:
            self.queueEvent(functools.partial(self.loadFile, self.filename))

        # Callbacks:
        self.zoomWidget.valueChanged.connect(self.paintCanvas)

        self.populateModeActions()

        # self.firstStart = True
        # if self.firstStart:
        #    QWhatsThis.enterWhatsThisMode()

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName("%sToolBar" % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            utils.addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar

    # Support Functions

    def noShapes(self):
        return not len(self.labelList)

    def populateModeActions(self):
        tool, menu = self.actions.tool, self.actions.menu
        self.tools.clear()
        utils.addActions(self.tools, tool)
        self.canvas.menus[0].clear()
        utils.addActions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (
            self.actions.createMode,
            self.actions.createRectangleMode,
            self.actions.createCircleMode,
            self.actions.createLineMode,
            self.actions.createPointMode,
            self.actions.createLineStripMode,
            self.actions.editMode,
        )
        utils.addActions(self.menus.edit, actions + self.actions.editMenu)

    def setDirty(self):
        if self._config["auto_save"] or self.actions.saveAuto.isChecked():
            label_file = osp.splitext(self.imagePath)[0] + ".json"
            if self.output_dir:
                label_file_without_path = osp.basename(label_file)
                label_file = osp.join(self.output_dir, label_file_without_path)
            self.saveLabels(label_file)
            return
        self.dirty = True
        self.actions.save.setEnabled(True)
        self.actions.undo.setEnabled(self.canvas.isShapeRestorable)
        title = __appname__
        if self.filename is not None:
            title = "{} - {}*".format(title, self.filename)
        self.setWindowTitle(title)

    def setClean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.createMode.setEnabled(True)
        self.actions.createRectangleMode.setEnabled(True)
        self.actions.createCircleMode.setEnabled(True)
        self.actions.createLineMode.setEnabled(True)
        self.actions.createPointMode.setEnabled(True)
        self.actions.createLineStripMode.setEnabled(True)
        title = __appname__
        if self.filename is not None:
            title = "{} - {}".format(title, self.filename)
        self.setWindowTitle(title)

        if self.hasLabelFile():
            self.actions.deleteFile.setEnabled(True)
        else:
            self.actions.deleteFile.setEnabled(False)

    def toggleActions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

    def canvasShapeEdgeSelected(self, selected, shape):
        self.actions.addPointToEdge.setEnabled(
            selected and shape and shape.canAddPoint()
        )

    def queueEvent(self, function):
        QtCore.QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        self.statusBar().showMessage(message, delay)

    def resetState(self):
        self.labelList.clear()
        self.filename = None
        self.imagePath = None
        self.imageData = None
        self.labelFile = None
        self.otherData = None
        self.canvas.resetState()

    def currentItem(self):
        items = self.labelList.selectedItems()
        if items:
            return items[0]
        return None

    def addRecentFile(self, filename):
        if filename in self.recentFiles:
            self.recentFiles.remove(filename)
        elif len(self.recentFiles) >= self.maxRecent:
            self.recentFiles.pop()
        self.recentFiles.insert(0, filename)

    # Callbacks

    def undoShapeEdit(self):
        self.canvas.restoreShape()
        self.loadShapes(self.canvas.shapes)
        self.actions.undo.setEnabled(self.canvas.isShapeRestorable)

    def tutorial(self):
        url = "https://github.com/wkentaro/labelme/tree/master/examples/tutorial"  # NOQA
        webbrowser.open(url)

    def toggleDrawingSensitive(self, drawing=True):
        """Toggle drawing sensitive.

        In the middle of drawing, toggling between modes should be disabled.
        """
        self.actions.editMode.setEnabled(not drawing)
        self.actions.undoLastPoint.setEnabled(drawing)
        self.actions.undo.setEnabled(not drawing)
        self.actions.delete.setEnabled(not drawing)

    def toggleDrawMode(self, edit=True, createMode="polygon"):
        self.canvas.setEditing(edit)
        self.canvas.createMode = createMode
        if edit:
            self.actions.createMode.setEnabled(True)
            self.actions.createRectangleMode.setEnabled(True)
            self.actions.createCircleMode.setEnabled(True)
            self.actions.createLineMode.setEnabled(True)
            self.actions.createPointMode.setEnabled(True)
            self.actions.createLineStripMode.setEnabled(True)
        else:
            if createMode == "polygon":
                self.actions.createMode.setEnabled(False)
                self.actions.createRectangleMode.setEnabled(True)
                self.actions.createCircleMode.setEnabled(True)
                self.actions.createLineMode.setEnabled(True)
                self.actions.createPointMode.setEnabled(True)
                self.actions.createLineStripMode.setEnabled(True)
            elif createMode == "rectangle":
                self.actions.createMode.setEnabled(True)
                self.actions.createRectangleMode.setEnabled(False)
                self.actions.createCircleMode.setEnabled(True)
                self.actions.createLineMode.setEnabled(True)
                self.actions.createPointMode.setEnabled(True)
                self.actions.createLineStripMode.setEnabled(True)
            elif createMode == "line":
                self.actions.createMode.setEnabled(True)
                self.actions.createRectangleMode.setEnabled(True)
                self.actions.createCircleMode.setEnabled(True)
                self.actions.createLineMode.setEnabled(False)
                self.actions.createPointMode.setEnabled(True)
                self.actions.createLineStripMode.setEnabled(True)
            elif createMode == "point":
                self.actions.createMode.setEnabled(True)
                self.actions.createRectangleMode.setEnabled(True)
                self.actions.createCircleMode.setEnabled(True)
                self.actions.createLineMode.setEnabled(True)
                self.actions.createPointMode.setEnabled(False)
                self.actions.createLineStripMode.setEnabled(True)
            elif createMode == "circle":
                self.actions.createMode.setEnabled(True)
                self.actions.createRectangleMode.setEnabled(True)
                self.actions.createCircleMode.setEnabled(False)
                self.actions.createLineMode.setEnabled(True)
                self.actions.createPointMode.setEnabled(True)
                self.actions.createLineStripMode.setEnabled(True)
            elif createMode == "linestrip":
                self.actions.createMode.setEnabled(True)
                self.actions.createRectangleMode.setEnabled(True)
                self.actions.createCircleMode.setEnabled(True)
                self.actions.createLineMode.setEnabled(True)
                self.actions.createPointMode.setEnabled(True)
                self.actions.createLineStripMode.setEnabled(False)
            else:
                raise ValueError("Unsupported createMode: %s" % createMode)
        self.actions.editMode.setEnabled(not edit)

    def setEditMode(self):
        self.toggleDrawMode(True)

    def updateFileMenu(self):
        current = self.filename

        def exists(filename):
            return osp.exists(str(filename))

        menu = self.menus.recentFiles
        menu.clear()
        files = [f for f in self.recentFiles if f != current and exists(f)]
        for i, f in enumerate(files):
            icon = utils.newIcon("labels")
            action = QtWidgets.QAction(
                icon, "&%d %s" % (i + 1, QtCore.QFileInfo(f).fileName()), self
            )
            action.triggered.connect(functools.partial(self.loadRecent, f))
            menu.addAction(action)

    def popLabelListMenu(self, point):
        self.menus.labelList.exec_(self.labelList.mapToGlobal(point))

    def validateLabel(self, label):
        # no validation
        if self._config["validate_label"] is None:
            return True

        for i in range(self.uniqLabelList.count()):
            label_i = self.uniqLabelList.item(i).data(Qt.UserRole)
            if self._config["validate_label"] in ["exact"]:
                if label_i == label:
                    return True
        return False

    def editLabel(self, item=None):
        if item and not isinstance(item, LabelListWidgetItem):
            raise TypeError("item must be LabelListWidgetItem type")

        if not self.canvas.editing():
            return
        if not item:
            item = self.currentItem()
        if item is None:
            return
        shape = item.shape()
        if shape is None:
            return
        text, flags, group_id = self.labelDialog.popUp(
            text=shape.label, flags=shape.flags, group_id=shape.group_id,
        )
        if text is None:
            return
        if not self.validateLabel(text):
            self.errorMessage(
                self.tr("Invalid label"),
                self.tr("Invalid label '{}' with validation type '{}'").format(
                    text, self._config["validate_label"]
                ),
            )
            return
        shape.label = text
        shape.flags = flags
        shape.group_id = group_id
        if shape.group_id is None:
            item.setText(shape.label)
        else:
            item.setText("{} ({})".format(shape.label, shape.group_id))
        self.setDirty()
        if not self.uniqLabelList.findItemsByLabel(shape.label):
            item = QtWidgets.QListWidgetItem()
            item.setData(Qt.UserRole, shape.label)
            self.uniqLabelList.addItem(item)

    def fileSearchChanged(self):
        self.importDirImages(
            self.lastOpenDir, pattern=self.fileSearch.text(), load=False,
        )

    def fileSelectionChanged(self):
        items = self.fileListWidget.selectedItems()
        if not items:
            return
        item = items[0]

        if not self.mayContinue():
            return

        currIndex = self.imageList.index(str(item.text()))
        if currIndex < len(self.imageList):
            filename = self.imageList[currIndex]
            if filename:
                self.loadFile(filename)

    # React to canvas signals.
    def shapeSelectionChanged(self, selected_shapes):
        self._noSelectionSlot = True
        for shape in self.canvas.selectedShapes:
            shape.selected = False
        self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True
            item = self.labelList.findItemByShape(shape)
            self.labelList.selectItem(item)
            self.labelList.scrollToItem(item)
        self._noSelectionSlot = False
        n_selected = len(selected_shapes)
        self.actions.delete.setEnabled(n_selected)
        self.actions.copy.setEnabled(n_selected)
        self.actions.edit.setEnabled(n_selected == 1)

    def addLabel(self, shape):
        if shape.group_id is None:
            text = shape.label
        else:
            text = "{} ({})".format(shape.label, shape.group_id)
        label_list_item = LabelListWidgetItem(text, shape)
        self.labelList.addItem(label_list_item)
        if not self.uniqLabelList.findItemsByLabel(shape.label):
            item = self.uniqLabelList.createItemFromLabel(shape.label)
            self.uniqLabelList.addItem(item)
            rgb = self._get_rgb_by_label(shape.label)
            self.uniqLabelList.setItemLabel(item, shape.label, rgb)
        self.labelDialog.addLabelHistory(shape.label)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)

        rgb = self._get_rgb_by_label(shape.label)

        r, g, b = rgb
        # print(rgb)
        # r, g, b = 100, 100, 100
        label_list_item.setText(
            '{} <font color="#{:02x}{:02x}{:02x}">●</font>'.format(
                text, r, g, b
            )
        )
        shape.line_color = QtGui.QColor(r, g, b)
        shape.vertex_fill_color = QtGui.QColor(r, g, b)
        shape.hvertex_fill_color = QtGui.QColor(255, 255, 255)
        shape.fill_color = QtGui.QColor(r, g, b, 128)
        shape.select_line_color = QtGui.QColor(255, 255, 255)
        shape.select_fill_color = QtGui.QColor(r, g, b, 155)

    def _get_rgb_by_label(self, label):
        if self._config["shape_color"] == "auto":
            item = self.uniqLabelList.findItemsByLabel(label)[0]
            label_id = self.uniqLabelList.indexFromItem(item).row() + 1
            label_id += self._config["shift_auto_shape_color"]
            return LABEL_COLORMAP[label_id % len(LABEL_COLORMAP)]
        elif (
                self._config["shape_color"] == "manual"
                and self._config["label_colors"]
                and label in self._config["label_colors"]
        ):
            return self._config["label_colors"][label]
        elif self._config["default_shape_color"]:
            return self._config["default_shape_color"]

    def remLabels(self, shapes):
        for shape in shapes:
            item = self.labelList.findItemByShape(shape)
            self.labelList.removeItem(item)

# 载点
    def loadShapes(self, shapes, replace=True):
        self._noSelectionSlot = True
        for shape in shapes:
            self.addLabel(shape)
        self.labelList.clearSelection()
        self._noSelectionSlot = False
        self.canvas.loadShapes(shapes, replace=replace)

    def loadLabels(self,):
        # shapes = self.labelFile.shapes,
        new_shapes = self.labelFile.shapes
        # new_shapes += self.addLine(new_shapes)
        # print(self._config["toggleLine"])
        if self._config["toggleLine"]:
            if 'line' not in new_shapes and len(new_shapes) > 250:
                new_shapes = new_shapes + self.addLine(new_shapes)
        new_shapes = self.tran(new_shapes)
        # print(len(new_shapes))
        s = []
        total = []
        total_num = len(new_shapes)
        togg = self._config["toggle"]

        for shape in new_shapes:
            label = shape["label"]
            points = shape["points"]
            shape_type = shape["shape_type"]
            flags = shape["flags"]
            group_id = shape["group_id"]
            other_data = shape["other_data"]

            if 'visibilityArray' in other_data:
                visibilityArray = other_data["visibilityArray"]
            else:
                visibilityArray = None

            shape = Shape(
                label=label, shape_type=shape_type, group_id=group_id, visibilityArray=visibilityArray,
                toggle=togg, total=total, total_num=total_num,
            )
            for x, y in points:
                shape.addPoint(QtCore.QPointF(x, y))
            shape.close()

            default_flags = {}
            # if self._config["label_flags"]:
            #     for pattern, keys in self._config["label_flags"].items():
            #         if re.match(pattern, label):
            #             for key in keys:
            #                 default_flags[key] = False
            shape.flags = default_flags
            shape.flags.update(flags)
            shape.other_data = other_data
            s.append(shape)
        self.loadShapes(s)

    def addLine(self, shapes):
        extra_shapes = []
        long106 = [
            shapes[:33],
            shapes[33:38] + shapes[67:63:-1],
            shapes[42:37:-1] + shapes[68:72],
            shapes[52:54]+[shapes[72]]+shapes[54:57]+[shapes[73]]+[shapes[57]],
            shapes[61:59:-1]+[shapes[75]]+shapes[59:57:-1]+[shapes[63]]+[shapes[76]]+[shapes[62]],
            shapes[84:91], shapes[100:95:-1],
            shapes[103:100:-1], shapes[91:96]
        ]
        for long in long106:
            points = []
            for shape in long:
                points.append(shape["points"][0])
            sh = {
                "label": '999{}'.format(long106.index(long)),
                "points": points,
                "group_id": "stMobile106",
                "shape_type": "linestrip",
                "flags": {},
                "other_data": {}
            }
            extra_shapes.append(sh)

        long134 = [
            shapes[106:106 + 11] + shapes[106 + 21:106 + 10:-1],
            shapes[106 + 22:106 + 33] + shapes[106 + 43:106 + 32:-1],
            shapes[106 + 44:106 + 51] + shapes[106 + 56:106 + 50:-1],
            shapes[106 + 57:106 + 64] + shapes[106 + 69:106 + 63:-1],
            # shapes[106 + 70:106 + 87] + shapes[106 + 103:106 + 87:-1],
            # shapes[106 + 104:106 + 119] + shapes[106 + 133:106 + 118:-1]
            shapes[106 + 70:106 + 87],
            shapes[106 + 103:106 + 87:-1],
            shapes[106 + 104:106 + 119],
            shapes[106 + 133:106 + 118:-1]
        ]
        for long in long134:
            points = []
            for shape in long:
                points.append(shape["points"][0])
            sh = {
                "label": '999{}'.format(long134.index(long)),
                "points": points,
                "group_id": "extraFacePoints",
                "shape_type": "linestrip",
                "flags": {},
                "other_data": {}
            }
            extra_shapes.append(sh)
        return extra_shapes

    def tran(self, shapes):
        stMobile106 = []
        extraFacePoints = []
        eyeballContour = []
        eyeballCenter = []
        occlusions = []
        iris_occlusions = []
        occ = []
        irr = []
        other = []

        for shape in shapes:
            if shape["group_id"] == 'stMobile106' and shape["shape_type"] == 'point':
                stMobile106.append(shape)
            elif shape["group_id"] == 'extraFacePoints' and shape["shape_type"] == 'point':
                extraFacePoints.append(shape)
            elif shape["group_id"] == 'eyeballContour' and shape["shape_type"] == 'point':
                eyeballContour.append(shape)
            elif shape["group_id"] == 'eyeballCenter' and shape["shape_type"] == 'point':
                eyeballCenter.append(shape)
            elif shape["group_id"] == 'z' and shape["shape_type"] == 'rectangle':
                occlusions.append(shape["points"])
                occ.append(shape)
            elif shape["group_id"].isdigit() and shape["shape_type"] == 'rectangle':
                iris_occlusions.append(shape["points"])
                irr.append(shape)
            else:
                other.append(shape)

        stMobile106 = sorted(stMobile106, key=lambda keys: int(keys["label"]))
        extraFacePoints = sorted(extraFacePoints, key=lambda keys: int(keys["label"]))
        eyeballContour = sorted(eyeballContour, key=lambda keys: int(keys["label"]))
        eyeballCenter = sorted(eyeballCenter, key=lambda keys: int(keys["label"]))

        if occlusions:
            for occlusion in occlusions:
                x = [occlusion[0][0], occlusion[1][0]]
                y = [occlusion[0][1], occlusion[1][1]]
                for i in stMobile106:
                    if min(x) < i["points"][0][0] < max(x) and min(y) < i["points"][0][1] < max(y):
                        stMobile106[stMobile106.index(i)]["other_data"]["visibilityArray"] = 0.0
                for i in extraFacePoints:
                    if min(x) < i["points"][0][0] < max(x) and min(y) < i["points"][0][1] < max(y):
                        extraFacePoints[extraFacePoints.index(i)]["other_data"]["visibilityArray"] = 0.0
                for i in eyeballCenter:
                    if min(x) < i["points"][0][0] < max(x) and min(y) < i["points"][0][1] < max(y):
                        eyeballCenter[eyeballCenter.index(i)]["other_data"]["visibilityArray"] = 0.0

        if iris_occlusions:
            for occlusion in iris_occlusions:
                x = [occlusion[0][0], occlusion[1][0]]
                y = [occlusion[0][1], occlusion[1][1]]
                for i in eyeballContour:
                    if min(x) < i["points"][0][0] < max(x) and min(y) < i["points"][0][1] < max(y):
                        eyeballContour[eyeballContour.index(i)]["other_data"]["visibilityArray"] = 0.0
        new_content = stMobile106 + extraFacePoints + eyeballContour + eyeballCenter + occ + irr + other
        return new_content


    def loadFlags(self, flags):
        self.flag_widget.clear()
        for key, flag in flags.items():
            item = QtWidgets.QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if flag else Qt.Unchecked)
            self.flag_widget.addItem(item)

    def saveLabels(self, filename):
        lf = LabelFile()

        def format_shape(s):
            data = s.other_data.copy()
            data.update(
                dict(
                    label=s.label.encode("utf-8") if PY2 else s.label,
                    points=[(p.x(), p.y()) for p in s.points],
                    group_id=s.group_id,
                    shape_type=s.shape_type,
                    flags=s.flags,
                )
            )
            return data

        shapes = [format_shape(item.shape()) for item in self.labelList if '999' not in format_shape(item.shape())["label"]]

        flags = {}
        for i in range(self.flag_widget.count()):
            item = self.flag_widget.item(i)
            key = item.text()
            flag = item.checkState() == Qt.Checked
            flags[key] = flag
        try:
            imagePath = osp.relpath(self.imagePath, osp.dirname(filename))
            imageData = self.imageData if self._config["store_data"] else None
            if osp.dirname(filename) and not osp.exists(osp.dirname(filename)):
                os.makedirs(osp.dirname(filename))
            lf.save(
                filename=filename,
                shapes=shapes,
                imagePath=imagePath,
                imageData=imageData,
                imageHeight=self.image.height(),
                imageWidth=self.image.width(),
                otherData=self.otherData,
                flags=flags,
            )
            self.labelFile = lf
            items = self.fileListWidget.findItems(
                self.imagePath, Qt.MatchExactly
            )
            if len(items) > 0:
                if len(items) != 1:
                    raise RuntimeError("There are duplicate files.")
                items[0].setCheckState(Qt.Checked)
            # disable allows next and previous image to proceed
            # self.filename = filename
            return True
        except LabelFileError as e:
            self.errorMessage(
                self.tr("Error saving label data"), self.tr("<b>%s</b>") % e
            )
            return False

    def copySelectedShape(self):
        added_shapes = self.canvas.copySelectedShapes()
        self.labelList.clearSelection()
        for shape in added_shapes:
            self.addLabel(shape)
        self.setDirty()

    def labelSelectionChanged(self):
        if self._noSelectionSlot:
            return
        if self.canvas.editing():
            selected_shapes = []
            for item in self.labelList.selectedItems():
                selected_shapes.append(item.shape())
            if selected_shapes:
                self.canvas.selectShapes(selected_shapes)
            else:
                self.canvas.deSelectShape()

# 打勾
    def labelItemChanged(self, item):
        shape = item.shape()
        self.canvas.setShapeVisible(shape, item.checkState() == Qt.Checked)

    def labelOrderChanged(self):
        self.setDirty()
        self.canvas.loadShapes([item.shape() for item in self.labelList])

    # Callback functions:

    def newShape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        items = self.uniqLabelList.selectedItems()
        text = None
        if items:
            text = items[0].data(Qt.UserRole)
        flags = {}
        group_id = None
        if self._config["display_label_popup"] or not text:
            previous_text = self.labelDialog.edit.text()
            text, flags, group_id = self.labelDialog.popUp(text)
            if not text:
                self.labelDialog.edit.setText(previous_text)

        if text and not self.validateLabel(text):
            self.errorMessage(
                self.tr("Invalid label"),
                self.tr("Invalid label '{}' with validation type '{}'").format(
                    text, self._config["validate_label"]
                ),
            )
            text = ""
        if text:
            self.labelList.clearSelection()
            shape = self.canvas.setLastLabel(text, flags)
            shape.group_id = group_id
            self.addLabel(shape)
            self.actions.editMode.setEnabled(True)
            self.actions.undoLastPoint.setEnabled(False)
            self.actions.undo.setEnabled(True)
            self.setDirty()
        else:
            self.canvas.undoLastLine()
            self.canvas.shapesBackups.pop()

    def scrollRequest(self, delta, orientation):
        units = -delta * 0.1  # natural scroll
        bar = self.scrollBars[orientation]
        value = bar.value() + bar.singleStep() * units
        self.setScroll(orientation, value)

    def setScroll(self, orientation, value):
        self.scrollBars[orientation].setValue(value)
        self.scroll_values[orientation][self.filename] = value

    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)
        self.zoom_values[self.filename] = (self.zoomMode, value)

    def addZoom(self, increment=1.1):
        self.setZoom(self.zoomWidget.value() * increment)

    def zoomRequest(self, delta, pos):
        canvas_width_old = self.canvas.width()
        units = 1.1
        if delta < 0:
            units = 0.9
        self.addZoom(units)

        canvas_width_new = self.canvas.width()
        if canvas_width_old != canvas_width_new:
            canvas_scale_factor = canvas_width_new / canvas_width_old

            x_shift = round(pos.x() * canvas_scale_factor) - pos.x()
            y_shift = round(pos.y() * canvas_scale_factor) - pos.y()

            self.setScroll(
                Qt.Horizontal,
                self.scrollBars[Qt.Horizontal].value() + x_shift,
            )
            self.setScroll(
                Qt.Vertical, self.scrollBars[Qt.Vertical].value() + y_shift,
            )

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def onNewBrightnessContrast(self, qimage):
        self.canvas.loadPixmap(
            QtGui.QPixmap.fromImage(qimage), clear_shapes=False
        )

    def brightnessContrast(self, value):
        dialog = BrightnessContrastDialog(
            utils.img_data_to_pil(self.imageData),
            self.onNewBrightnessContrast,
            parent=self,
        )
        brightness, contrast = self.brightnessContrast_values.get(
            self.filename, (None, None)
        )
        if brightness is not None:
            dialog.slider_brightness.setValue(brightness)
        if contrast is not None:
            dialog.slider_contrast.setValue(contrast)
        dialog.exec_()

        brightness = dialog.slider_brightness.value()
        contrast = dialog.slider_contrast.value()
        self.brightnessContrast_values[self.filename] = (brightness, contrast)

    def togglePolygons(self, value):

        for item in self.labelList:
            item.setCheckState(Qt.Checked if value else Qt.Unchecked)


    # 增加可见函数
    def toggleShow106(self, value):
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")[1]
            if a == 'stMobile106' and '999' not in str(item):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleShow134(self, value):
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")[1]
            if a == 'extraFacePoints' and '999' not in str(item):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleShow38(self, value):
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")[1]
            if a == 'eyeballContour' or a == 'eyeballCenter':
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleRect(self, value):
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")[1]
            if a == 'z' or a == '1':
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def loadFile(self, filename=None, ):
        """Load the specified file, or the last opened file if None."""
        # changing fileListWidget loads file
        if filename in self.imageList and (
                self.fileListWidget.currentRow() != self.imageList.index(filename)
        ):
            self.fileListWidget.setCurrentRow(self.imageList.index(filename))
            self.fileListWidget.repaint()
            return

        self.resetState()
        self.canvas.setEnabled(False)
        if filename is None:
            filename = self.settings.value("filename", "")
        filename = str(filename)
        if not QtCore.QFile.exists(filename):
            self.errorMessage(
                self.tr("Error opening file"),
                self.tr("No such file: <b>%s</b>") % filename,
            )
            return False
        # assumes same name, but json extension
        self.status(self.tr("Loading %s...") % osp.basename(str(filename)))
        label_file = osp.splitext(filename)[0] + ".json"
        if self.output_dir:
            label_file_without_path = osp.basename(label_file)
            label_file = osp.join(self.output_dir, label_file_without_path)
        if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
                label_file
        ):
            try:
                self.labelFile = LabelFile(label_file)
            except LabelFileError as e:
                self.errorMessage(
                    self.tr("Error opening file"),
                    self.tr(
                        "<p><b>%s</b></p>"
                        "<p>Make sure <i>%s</i> is a valid label file."
                    )
                    % (e, label_file),
                )
                self.status(self.tr("Error reading %s") % label_file)
                return False
            self.imageData = self.labelFile.imageData
            self.imagePath = osp.join(
                osp.dirname(label_file), self.labelFile.imagePath,
            )
            self.otherData = self.labelFile.otherData
        else:
            self.imageData = LabelFile.load_image_file(filename)
            if self.imageData:
                self.imagePath = filename
            self.labelFile = None
        image = QtGui.QImage.fromData(self.imageData)

        if image.isNull():
            formats = [
                "*.{}".format(fmt.data().decode())
                for fmt in QtGui.QImageReader.supportedImageFormats()
            ]
            self.errorMessage(
                self.tr("Error opening file"),
                self.tr(
                    "<p>Make sure <i>{0}</i> is a valid image file.<br/>"
                    "Supported image formats: {1}</p>"
                ).format(filename, ",".join(formats)),
            )
            self.status(self.tr("Error reading %s") % filename)
            return False
        self.image = image
        self.filename = filename
        if self._config["keep_prev"]:
            prev_shapes = self.canvas.shapes
        self.canvas.loadPixmap(QtGui.QPixmap.fromImage(image))
        flags = {k: False for k in self._config["flags"] or []}
        if self.labelFile:
            self.loadLabels()
            if self.labelFile.flags is not None:
                flags.update(self.labelFile.flags)
        self.loadFlags(flags)
        if self._config["keep_prev"] and self.noShapes():
            self.loadShapes(prev_shapes, replace=False)
            self.setDirty()
        else:
            self.setClean()
        self.canvas.setEnabled(True)
        # set zoom values
        is_initial_load = not self.zoom_values
        if self.filename in self.zoom_values:
            self.zoomMode = self.zoom_values[self.filename][0]
            self.setZoom(self.zoom_values[self.filename][1])
        elif is_initial_load or not self._config["keep_prev_scale"]:
            self.adjustScale(initial=True)
        # set scroll values
        for orientation in self.scroll_values:
            if self.filename in self.scroll_values[orientation]:
                self.setScroll(
                    orientation, self.scroll_values[orientation][self.filename]
                )
        # set brightness constrast values
        dialog = BrightnessContrastDialog(
            utils.img_data_to_pil(self.imageData),
            self.onNewBrightnessContrast,
            parent=self,
        )
        brightness, contrast = self.brightnessContrast_values.get(
            self.filename, (None, None)
        )
        if self._config["keep_prev_brightness"] and self.recentFiles:
            brightness, _ = self.brightnessContrast_values.get(
                self.recentFiles[0], (None, None)
            )
        if self._config["keep_prev_contrast"] and self.recentFiles:
            _, contrast = self.brightnessContrast_values.get(
                self.recentFiles[0], (None, None)
            )
        if brightness is not None:
            dialog.slider_brightness.setValue(brightness)
        if contrast is not None:
            dialog.slider_contrast.setValue(contrast)
        self.brightnessContrast_values[self.filename] = (brightness, contrast)
        if brightness is not None or contrast is not None:
            dialog.onNewValue(None)
        self.paintCanvas()
        self.addRecentFile(self.filename)
        self.toggleActions(True)
        self.status(self.tr("Loaded %s") % osp.basename(str(filename)))
        return True

    def resizeEvent(self, event):
        if (
                self.canvas
                and not self.image.isNull()
                and self.zoomMode != self.MANUAL_ZOOM
        ):
            self.adjustScale()
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def adjustScale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        value = int(100 * value)
        self.zoomWidget.setValue(value)
        self.zoom_values[self.filename] = (self.zoomMode, value)

    def scaleFitWindow(self):
        """Figure out the size of the pixmap to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def enableSaveImageWithData(self, enabled):
        self._config["store_data"] = enabled
        self.actions.saveWithImageData.setChecked(enabled)

    def closeEvent(self, event):
        if not self.mayContinue():
            event.ignore()
        self.settings.setValue(
            "filename", self.filename if self.filename else ""
        )
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        self.settings.setValue("window/state", self.saveState())
        self.settings.setValue("recentFiles", self.recentFiles)
        # ask the use for where to save the labels
        # self.settings.setValue('window/geometry', self.saveGeometry())

    def dragEnterEvent(self, event):
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]
        if event.mimeData().hasUrls():
            items = [i.toLocalFile() for i in event.mimeData().urls()]
            if any([i.lower().endswith(tuple(extensions)) for i in items]):
                event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not self.mayContinue():
            event.ignore()
            return
        items = [i.toLocalFile() for i in event.mimeData().urls()]
        self.importDroppedImageFiles(items)

    # User Dialogs #

    def loadRecent(self, filename):
        if self.mayContinue():
            self.loadFile(filename)

    def openPrevImg(self, _value=False):
        keep_prev = self._config["keep_prev"]
        if Qt.KeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self._config["keep_prev"] = True

        if not self.mayContinue():
            return

        if len(self.imageList) <= 0:
            return

        if self.filename is None:
            return

        currIndex = self.imageList.index(self.filename)
        if currIndex - 1 >= 0:
            filename = self.imageList[currIndex - 1]
            if filename:
                self.loadFile(filename)

        self._config["keep_prev"] = keep_prev

    def openNextImg(self, _value=False, load=True):
        keep_prev = self._config["keep_prev"]
        if Qt.KeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self._config["keep_prev"] = True

        if not self.mayContinue():
            return

        if len(self.imageList) <= 0:
            return

        filename = None
        if self.filename is None:
            filename = self.imageList[0]
        else:
            currIndex = self.imageList.index(self.filename)
            if currIndex + 1 < len(self.imageList):
                filename = self.imageList[currIndex + 1]
            else:
                filename = self.imageList[-1]
        self.filename = filename

        if self.filename and load:
            self.loadFile(self.filename)

        self._config["keep_prev"] = keep_prev

    def openFile(self, _value=False):
        if not self.mayContinue():
            return
        path = osp.dirname(str(self.filename)) if self.filename else "."
        formats = [
            "*.{}".format(fmt.data().decode())
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]
        filters = self.tr("Image & Label files (%s)") % " ".join(
            formats + ["*%s" % LabelFile.suffix]
        )
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.tr("%s - Choose Image or Label file") % __appname__,
            path,
            filters,
        )
        if QT5:
            filename, _ = filename
        filename = str(filename)
        if filename:
            self.loadFile(filename)

    def changeOutputDirDialog(self, _value=False):
        default_output_dir = self.output_dir
        if default_output_dir is None and self.filename:
            default_output_dir = osp.dirname(self.filename)
        if default_output_dir is None:
            default_output_dir = self.currentPath()

        output_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.tr("%s - Save/Load Annotations in Directory") % __appname__,
            default_output_dir,
            QtWidgets.QFileDialog.ShowDirsOnly
            | QtWidgets.QFileDialog.DontResolveSymlinks,
        )
        output_dir = str(output_dir)

        if not output_dir:
            return

        self.output_dir = output_dir

        self.statusBar().showMessage(
            self.tr("%s . Annotations will be saved/loaded in %s")
            % ("Change Annotations Dir", self.output_dir)
        )
        self.statusBar().show()

        current_filename = self.filename
        self.importDirImages(self.lastOpenDir, load=False)

        if current_filename in self.imageList:
            # retain currently selected file
            self.fileListWidget.setCurrentRow(
                self.imageList.index(current_filename)
            )
            self.fileListWidget.repaint()

    def saveFile(self, _value=False):
        assert not self.image.isNull(), "cannot save empty image"
        if self.labelFile:
            # DL20180323 - overwrite when in directory
            self._saveFile(self.labelFile.filename)
        elif self.output_file:
            self._saveFile(self.output_file)
            self.close()
        else:
            self._saveFile(self.saveFileDialog())

    def saveFileAs(self, _value=False):
        assert not self.image.isNull(), "cannot save empty image"
        self._saveFile(self.saveFileDialog())

    def saveFileDialog(self):
        caption = self.tr("%s - Choose File") % __appname__
        filters = self.tr("Label files (*%s)") % LabelFile.suffix
        if self.output_dir:
            dlg = QtWidgets.QFileDialog(
                self, caption, self.output_dir, filters
            )
        else:
            dlg = QtWidgets.QFileDialog(
                self, caption, self.currentPath(), filters
            )
        dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, False)
        dlg.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, False)
        basename = osp.basename(osp.splitext(self.filename)[0])
        if self.output_dir:
            default_labelfile_name = osp.join(
                self.output_dir, basename + LabelFile.suffix
            )
        else:
            default_labelfile_name = osp.join(
                self.currentPath(), basename + LabelFile.suffix
            )
        filename = dlg.getSaveFileName(
            self,
            self.tr("Choose File"),
            default_labelfile_name,
            self.tr("Label files (*%s)") % LabelFile.suffix,
        )
        if isinstance(filename, tuple):
            filename, _ = filename
        return filename

    def _saveFile(self, filename):
        if filename and self.saveLabels(filename):
            self.addRecentFile(filename)
            self.setClean()

    def closeFile(self, _value=False):
        if not self.mayContinue():
            return
        self.resetState()
        self.setClean()
        self.toggleActions(False)
        self.canvas.setEnabled(False)
        self.actions.saveAs.setEnabled(False)

    def getLabelFile(self):
        if self.filename.lower().endswith(".json"):
            label_file = self.filename
        else:
            label_file = osp.splitext(self.filename)[0] + ".json"

        return label_file

    def deleteFile(self):
        mb = QtWidgets.QMessageBox
        msg = self.tr(
            "You are about to permanently delete this label file, "
            "proceed anyway?"
        )
        answer = mb.warning(self, self.tr("Attention"), msg, mb.Yes | mb.No)
        if answer != mb.Yes:
            return

        label_file = self.getLabelFile()
        if osp.exists(label_file):
            os.remove(label_file)
            logger.info("Label file is removed: {}".format(label_file))

            item = self.fileListWidget.currentItem()
            item.setCheckState(Qt.Unchecked)

            self.resetState()

    # Message Dialogs. #
    def hasLabels(self):
        if self.noShapes():
            self.errorMessage(
                "No objects labeled",
                "You must label at least one object to save the file.",
            )
            return False
        return True

    def hasLabelFile(self):
        if self.filename is None:
            return False

        label_file = self.getLabelFile()
        return osp.exists(label_file)

    def mayContinue(self):
        if not self.dirty:
            return True
        mb = QtWidgets.QMessageBox
        msg = self.tr('Save annotations to "{}" before closing?').format(
            self.filename
        )
        answer = mb.question(
            self,
            self.tr("Save annotations?"),
            msg,
            mb.Save | mb.Discard | mb.Cancel,
            mb.Save,
        )
        if answer == mb.Discard:
            return True
        elif answer == mb.Save:
            self.saveFile()
            return True
        else:  # answer == mb.Cancel
            return False

    def errorMessage(self, title, message):
        return QtWidgets.QMessageBox.critical(
            self, title, "<p><b>%s</b></p>%s" % (title, message)
        )

    def currentPath(self):
        return osp.dirname(str(self.filename)) if self.filename else "."

    def toggleKeepPrevMode(self):
        self._config["keep_prev"] = not self._config["keep_prev"]

    def deleteSelectedShape(self):
        yes, no = QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        msg = self.tr(
            "You are about to permanently delete {} polygons, "
            "proceed anyway?"
        ).format(len(self.canvas.selectedShapes))
        if yes == QtWidgets.QMessageBox.warning(
                self, self.tr("Attention"), msg, yes | no, yes
        ):
            self.remLabels(self.canvas.deleteSelected())
            self.setDirty()
            if self.noShapes():
                for action in self.actions.onShapesPresent:
                    action.setEnabled(False)
        self.saveFile()

    def copyShape(self):
        self.canvas.endMove(copy=True)
        self.labelList.clearSelection()
        for shape in self.canvas.selectedShapes:
            self.addLabel(shape)
        self.setDirty()

    def moveShape(self):
        self.canvas.endMove(copy=False)
        self.setDirty()

    def openDirDialog(self, _value=False, dirpath=None):
        if not self.mayContinue():
            return

        defaultOpenDirPath = dirpath if dirpath else "."
        if self.lastOpenDir and osp.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        else:
            defaultOpenDirPath = (
                osp.dirname(self.filename) if self.filename else "."
            )

        targetDirPath = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self,
                self.tr("%s - Open Directory") % __appname__,
                defaultOpenDirPath,
                QtWidgets.QFileDialog.ShowDirsOnly
                | QtWidgets.QFileDialog.DontResolveSymlinks,
            )
        )
        self.importDirImages(targetDirPath)

    @property
    def imageList(self):
        lst = []
        for i in range(self.fileListWidget.count()):
            item = self.fileListWidget.item(i)
            lst.append(item.text())
        return lst

    def importDroppedImageFiles(self, imageFiles):
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]

        self.filename = None
        for file in imageFiles:
            if file in self.imageList or not file.lower().endswith(
                    tuple(extensions)
            ):
                continue
            label_file = osp.splitext(file)[0] + ".json"
            if self.output_dir:
                label_file_without_path = osp.basename(label_file)
                label_file = osp.join(self.output_dir, label_file_without_path)
            item = QtWidgets.QListWidgetItem(file)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
                    label_file
            ):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.fileListWidget.addItem(item)

        if len(self.imageList) > 1:
            self.actions.openNextImg.setEnabled(True)
            self.actions.openPrevImg.setEnabled(True)

        self.openNextImg()

    def importDirImages(self, dirpath, pattern=None, load=True):
        self.actions.openNextImg.setEnabled(True)
        self.actions.openPrevImg.setEnabled(True)

        if not self.mayContinue() or not dirpath:
            return

        self.lastOpenDir = dirpath
        self.filename = None
        self.fileListWidget.clear()
        for filename in self.scanAllImages(dirpath):
            if pattern and pattern not in filename:
                continue
            label_file = osp.splitext(filename)[0] + ".json"
            if self.output_dir:
                label_file_without_path = osp.basename(label_file)
                label_file = osp.join(self.output_dir, label_file_without_path)
            item = QtWidgets.QListWidgetItem(filename)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
                    label_file
            ):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.fileListWidget.addItem(item)
        self.openNextImg(load=load)

    def scanAllImages(self, folderPath):
        extensions = [
            ".%s" % fmt.data().decode().lower()
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]

        images = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = osp.join(root, file)
                    images.append(relativePath)
        images.sort(key=lambda x: x.lower())
        return images

    def RegenerateLeftPupil(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]
        overdue_points = []
        for shape in shapes:
            if shape["group_id"] == 'eyeballCenter' and shape["label"] == "0":
                circle_center = shape["points"][0]
            if shape["group_id"] == 'eyeballContour' and shape["label"] == "4":
                circle_peripheral = shape["points"][0]
            if shape["group_id"] == 'eyeballContour' and shape["label"] in [str(x) for x in range(19)]:
                overdue_points.append(shape)

        if circle_center and circle_peripheral:
            r = round(math.hypot(circle_center[0] - circle_peripheral[0], circle_center[1] - circle_peripheral[1]))
            radians = (math.pi / 180) * round(360 / 19)
            new_points = []
            for i in range(19):
                if i < 5:
                    x = circle_center[0] + r * math.sin(radians * i)
                    y = circle_center[1] + r * math.cos(radians * i)
                    shape = {
                        "label": "{}".format(4 - i),
                        "points": [[x, y]],
                        "group_id": "eyeballContour",
                        "shape_type": "point",
                        "flags": {}
                    }
                    new_points.append(shape)
                else:
                    x = circle_center[0] + r * math.sin(radians * i)
                    y = circle_center[1] + r * math.cos(radians * i)
                    shape = {
                        "label": "{}".format(23 - i),
                        "points": [[x, y]],
                        "group_id": "eyeballContour",
                        "shape_type": "point",
                        "flags": {}
                    }
                    new_points.append(shape)
            for i in overdue_points:
                shapes.remove(i)
            shapes += new_points
            content["shapes"] = shapes
            with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=4)
            self.loadFile(self.filename)
            self.toggleShow38(True)

    def RegenerateRightPupil(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]
        overdue_points = []
        for shape in shapes:
            if shape["group_id"] == 'eyeballCenter' and shape["label"] == "1":
                circle_center = shape["points"][0]
            if shape["group_id"] == 'eyeballContour' and shape["label"] == "23":
                circle_peripheral = shape["points"][0]
            if shape["group_id"] == 'eyeballContour' and shape["label"] in [str(x) for x in range(19, 38)]:
                overdue_points.append(shape)

        if circle_center and circle_peripheral:
            r = round(math.hypot(circle_center[0] - circle_peripheral[0], circle_center[1] - circle_peripheral[1]))
            radians = (math.pi / 180) * round(360 / 19)
            new_points = []
            for i in range(19):
                if i < 15:
                    x = circle_center[0] + r * math.sin(radians * i)
                    y = circle_center[1] + r * math.cos(radians * i)
                    shape = {
                        "label": "{}".format(i + 23),
                        "points": [[x, y]],
                        "group_id": "eyeballContour",
                        "shape_type": "point",
                        "flags": {}
                    }
                    new_points.append(shape)
                else:
                    x = circle_center[0] + r * math.sin(radians * i)
                    y = circle_center[1] + r * math.cos(radians * i)
                    shape = {
                        "label": "{}".format(i + 4),
                        "points": [[x, y]],
                        "group_id": "eyeballContour",
                        "shape_type": "point",
                        "flags": {}
                    }
                    new_points.append(shape)
            for i in overdue_points:
                shapes.remove(i)
            shapes += new_points
            content["shapes"] = shapes
            with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=4)
            self.loadFile(self.filename)
            self.toggleShow38(True)

    def calculation_point(self, prev_coordinate, next_coordinate, segments, part):
        next_coordinate = next_coordinate[0]
        prev_coordinate = prev_coordinate[0]
        x = (next_coordinate[0] - prev_coordinate[0]) / (segments / part)
        y = (next_coordinate[1] - prev_coordinate[1]) / (segments / part)
        new_point = [prev_coordinate[0] + x, prev_coordinate[1] + y]
        return [new_point]

    # 关键点合并
    def MergeKeyPoints(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        # 106点重合
        shapes[96]["points"] = shapes[84]["points"]
        shapes[100]["points"] = shapes[90]["points"]

        # 左眉毛
        shapes[150]["points"] = shapes[33]["points"]
        shapes[153]["points"] = shapes[35]["points"]
        shapes[156]["points"] = shapes[37]["points"]
        shapes[159]["points"] = shapes[65]["points"]
        shapes[162]["points"] = shapes[67]["points"]

        # 右眉毛
        shapes[169]["points"] = shapes[38]["points"]
        shapes[166]["points"] = shapes[40]["points"]
        shapes[163]["points"] = shapes[42]["points"]
        shapes[175]["points"] = shapes[68]["points"]
        shapes[172]["points"] = shapes[70]["points"]

        # 眼睛
        shapes[117]["points"] = shapes[52]["points"]
        shapes[116]["points"] = shapes[55]["points"]
        shapes[138]["points"] = shapes[58]["points"]
        shapes[139]["points"] = shapes[61]["points"]

        # 上嘴唇
        shapes[193]["points"] = shapes[176]["points"]
        shapes[209]["points"] = shapes[192]["points"]

        shapes[176]["points"] = shapes[84]["points"]
        shapes[179]["points"] = shapes[85]["points"]
        shapes[182]["points"] = shapes[86]["points"]
        shapes[184]["points"] = shapes[87]["points"]
        shapes[186]["points"] = shapes[88]["points"]
        shapes[189]["points"] = shapes[89]["points"]
        shapes[192]["points"] = shapes[90]["points"]
        shapes[201]["points"] = shapes[98]["points"]

        # 下嘴唇
        shapes[217]["points"] = shapes[102]["points"]
        shapes[232]["points"] = shapes[93]["points"]

        content["shapes"] = shapes

        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.sortPoint(True)
        self.toggleShow134(True)

    # 一键合并
    def MegrgeAndBisect(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        a = []
        b = []
        c = []
        d = []
        shapes = []
        for shape in content["shapes"]:
            if shape["group_id"] == 'stMobile106':
                a.append(shape)
            elif shape["group_id"] == 'extraFacePoints':
                b.append(shape)
            elif shape["group_id"] == 'eyeballContour':
                c.append(shape)
            else:
                d.append(shape)
        shapes = sorted(a, key=lambda keys: int(keys["label"])) + sorted(b, key=lambda keys: int(keys["label"])) \
                 + sorted(c, key=lambda keys: int(keys["label"])) + d

        c = CalAll()
        c.shapes = shapes

        # 左眉毛
        shapes[44+106]["points"] = shapes[33]["points"]
        # shapes[153]["points"] = shapes[35]["points"]
        shapes[50+106]["points"] = shapes[37]["points"]
        # shapes[159]["points"] = shapes[65]["points"]
        shapes[56+106]["points"] = shapes[67]["points"]

        # 右眉毛
        shapes[63+106]["points"] = shapes[38]["points"]
        # shapes[166]["points"] = shapes[40]["points"]
        shapes[57+106]["points"] = shapes[42]["points"]
        shapes[69+106]["points"] = shapes[68]["points"]
        # shapes[172]["points"] = shapes[70]["points"]

        # 眼睛
        shapes[117]["points"] = shapes[52]["points"]
        shapes[116]["points"] = shapes[55]["points"]
        shapes[138]["points"] = shapes[58]["points"]
        shapes[139]["points"] = shapes[61]["points"]

        # 上嘴唇
        shapes[70+106]["points"] = shapes[84]["points"]
        # shapes[179]["points"] = shapes[85]["points"]
        shapes[76+106]["points"] = shapes[86]["points"]
        shapes[78+106]["points"] = shapes[87]["points"]
        shapes[80+106]["points"] = shapes[88]["points"]
        # shapes[189]["points"] = shapes[89]["points"]
        shapes[86+106]["points"] = shapes[90]["points"]
        shapes[95+106]["points"] = shapes[98]["points"]

        shapes[87 + 106]["points"] = shapes[84]["points"]
        shapes[103 + 106]["points"] = shapes[90]["points"]

        # 下嘴唇
        shapes[217]["points"] = shapes[102]["points"]
        shapes[232]["points"] = shapes[93]["points"]

        # 生成的点

        # 眉毛
        c.CalLeftUpperEyebrow()
        c.CalLeftLowerEyebrow()
        c.CalRightUpperEyebrow()
        c.CalRightLowerEyebrow()

        # 眼睛
        c.CalLeftLowerEye()
        c.CalLeftUpperEye()
        c.CalRightLowerEye()
        c.CalRightUpperEye()

        # 嘴唇
        c.CalUpperLipUpper()
        c.CalUpperLipLower()
        c.CalLowerLipUpper()
        c.CalLowerLipLower()

        # 瞳孔点
        shapes[278]["points"] = shapes[104]["points"]
        shapes[279]["points"] = shapes[105]["points"]

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        # self.loadFile(self.filename)
        self.sortPoint(True)
        self.toggleShow134(True)

    # 排序
    def sortPoint(self, value):
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        a = []
        b = []
        c = []
        d = []
        e = []
        shapes = []

        num106 = [x for x in range(106)]
        num134 = [x for x in range(134)]
        num38 = [x for x in range(38)]
        num2 = [x for x in range(2)]

        run_function = lambda x, y: x if y in x else x + [y]
        sort_shapes = reduce(run_function, [[], ] + content["shapes"])
        for shape in sort_shapes:
            if shape["group_id"] == 'stMobile106' and int(shape["label"]) in num106:
                num106.remove(int(shape["label"]))
                a.append(shape)
            elif shape["group_id"] == 'extraFacePoints' and int(shape["label"]) in num134:
                num134.remove(int(shape["label"]))
                b.append(shape)
            elif shape["group_id"] == 'eyeballContour' and int(shape["label"]) in num38:
                num38.remove(int(shape["label"]))
                c.append(shape)
            elif shape["group_id"] == 'eyeballCenter' and int(shape["label"]) in num2:
                num2.remove(int(shape["label"]))
                d.append(shape)
            else:
                if shape["group_id"] == 'stMobile106' or shape["group_id"] == 'extraFacePoints' or \
                        shape["group_id"] == 'eyeballContour' or shape["group_id"] == 'eyeballCenter':
                    pass
                else:
                    e.append(shape)
        shapes = sorted(a, key=lambda keys: int(keys["label"])) + sorted(b, key=lambda keys: int(keys["label"])) \
                 + sorted(c, key=lambda keys: int(keys["label"])) + sorted(d, key=lambda keys: int(keys["label"])) + e

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)

    # 等分106点
    def restructure106(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        a = []
        b = []
        c = []
        d = []
        shapes = []
        for shape in content["shapes"]:
            if shape["group_id"] == 'stMobile106':
                a.append(shape)
            elif shape["group_id"] == 'extraFacePoints':
                b.append(shape)
            elif shape["group_id"] == 'eyeballContour':
                c.append(shape)
            else:
                d.append(shape)
        shapes = sorted(a, key=lambda keys: int(keys["label"])) + sorted(b, key=lambda keys: int(keys["label"])) \
                 + sorted(c, key=lambda keys: int(keys["label"])) + d

        c = CalAll()
        c.shapes = shapes

        # 脸颊
        c.CalFace()

        # 眉毛
        c.Cal106LeftEyebrow()
        c.Cal106RightEyebrow()

        # 眼睛
        c.CalLeftEye()
        c.CalRightEye()
        c.CalEyeMid()

        # 嘴巴
        c.Cal106UpperLip()
        c.Cal106LowerLip()

        # # 瞳孔
        # c.Cal74And77()

        # 106点重合
        shapes[96]["points"] = shapes[84]["points"]
        shapes[100]["points"] = shapes[90]["points"]
        shapes[278]["points"] = shapes[104]["points"]
        shapes[279]["points"] = shapes[105]["points"]

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleShow106(True)

    def toggleKeyPoints(self, value):
        number = [84, 86, 87, 88, 90, 98, 102, 93, 33, 37, 67, 52, 55, 38,
                  103, 95, 94, 92, 101, 91, 85, 97, 89, 99, 85,
                  34, 35, 36, 64, 65, 66, 39, 40, 41, 69, 70, 71,
                  53, 72, 54, 57, 73, 56, 59, 75, 60, 62, 76, 63,
                  68, 42, 58, 61, 35, 65, 40, 70,
                  0, 5, 9, 11, 13, 15, 16, 17, 19, 21, 23, 27, 32, 12, 20]
        number1 = [119, 125, 127, 133, 104, 118, 71, 85, 88, 102, 110, 112,
                   94, 96, 102,
                   12, 21, 0, 9, 43, 34, 31, 22,
                   45, 49, 51, 55, 62, 58, 68, 64
                   ]

        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'stMobile106' and int(num) in number:
                item.setCheckState(Qt.Checked)
            elif group == 'extraFacePoints' and int(num) in number1:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleEyebrow(self, value):
        st106 = [x for x in range(33, 43)] + [x for x in range(64, 72)]
        ex134 = [x for x in range(44, 70)]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'stMobile106' and int(num) in st106:
                item.setCheckState(Qt.Checked)
            elif group == 'extraFacePoints' and int(num) in ex134:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleEye(self, value):
        number = [x for x in range(0, 44)]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'extraFacePoints' and int(num) in number:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleEye106(self, value):
        number = [x for x in range(52, 64)] + [72, 73, 75, 76, 74, 104, 77, 105]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'stMobile106' and int(num) in number:
                item.setCheckState(Qt.Checked)

    def toggleUpperLip(self, value):
        number = [x for x in range(70, 104)]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'extraFacePoints' and int(num) in number:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleLowerLip(self, value):
        number = [x for x in range(104, 134)] + [70, 86]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'extraFacePoints' and int(num) in number:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleLip(self, value):
        number = [x for x in range(104, 134)] + [x for x in range(70, 104)]
        number1 = [x for x in range(84, 104)]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'extraFacePoints' and int(num) in number:
                item.setCheckState(Qt.Checked)
            elif group == 'stMobile106' and int(num) in number1:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleFaceKeyPoint(self, value):
        number = [0, 5, 9, 11, 13, 15, 16, 17, 19, 21, 23, 27, 32]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'stMobile106' and int(num) in number:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def toggleFace(self, value):
        number = [x for x in range(33)]
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")
            num = a[0].replace('"', '')
            group = a[1]
            if group == 'stMobile106' and int(num) in number:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)


    # 显示线段
    def toggleLine(self, value, num):
        for item in self.labelList:
            a = re.findall('LabelListWidgetItem\((.*?)\)', str(item))[0].split("(")[1]
            if num == 1:
                if a == 'stMobile106' and ('9995' in str(item) or '9996' in str(item)):
                    item.setCheckState(Qt.Checked)
            if num == 2:
                if a == 'stMobile106' and ('9997' in str(item) or '9998' in str(item)):
                    item.setCheckState(Qt.Checked)
            if num == 3:
                if a == 'extraFacePoints' and ('9995' in str(item) or '9994' in str(item)):
                    item.setCheckState(Qt.Checked)
            if num == 4:
                if a == 'extraFacePoints' and ('9997' in str(item) or '9996' in str(item)):
                    item.setCheckState(Qt.Checked)
            if num == 5:
                if '999' in str(item):
                    item.setCheckState(Qt.Checked)


    # 脸颊
    def GeneratingFace(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]
        # 生成的点
        c = CalAll()
        c.shapes = shapes
        c.CalFace()
        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleFace(True)

    # 眉毛
    def GeneratingEyebrowPoints(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        # 生成的点
        c = CalAll()
        c.shapes = shapes

        c.CalLeftUpperEyebrow()
        c.CalLeftLowerEyebrow()
        c.CalRightUpperEyebrow()
        c.CalRightLowerEyebrow()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEyebrow(True)

    def GeneratingEyebrowPoints106(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        # 生成的点
        c = CalAll()
        c.shapes = shapes

        c.Cal106LeftEyebrow()
        c.Cal106RightEyebrow()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEyebrow(True)

    # 眼睛
    def GeneratingLeftEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalLeftLowerEye()
        c.CalLeftUpperEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingLeftupperEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalLeftUpperEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingLeftLowerEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalLeftLowerEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingRightEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalRightLowerEye()
        c.CalRightUpperEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingRightupperEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalRightUpperEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingRightLowerEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalRightLowerEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingEye(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalLeftLowerEye()
        c.CalLeftUpperEye()
        c.CalRightLowerEye()
        c.CalRightUpperEye()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye(True)

    def GeneratingEyeMid(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalEyeMid()
        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleEye106(True)

    # 嘴巴
    def GeneratingUpperlipPoints(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalUpperLipUpper()
        c.CalUpperLipLower()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleUpperLip(True)

    def GeneratingLowerlipPoints(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes
        c.CalLowerLipUpper()
        c.CalLowerLipLower()

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)
        self.toggleLowerLip(True)

    def CreateAll(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]
        c = CalAuto()
        c.shapes = shapes
        c.deal()
        content["shapes"] = c.newShapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.sortPoint(True)
        self.toggleKeyPoints(True)

    def ResetPoint(self):
        try:
            file = {
                "version": "4.5.6",
                "flags": {},
                "shapes": [],
                "imagePath": "",
                "imageData": "",
                "imageHeight": "",
                "imageWidth": ""
            }
            with open(self.filename, 'rb') as f:
                base64_data = base64.b64encode(f.read())
            image = Image.open(osp.join(self.filename))
            width = image.size[0]
            height = image.size[1]
            image.close()
            file['imageData'] = base64_data.decode('utf-8')
            file['imageHeight'] = height
            file['imageWidth'] = width
            file['imagePath'] = osp.basename(self.filename)
            new_shapes = []

            for num in range(0, 5):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 4)]],
                    "group_id": "left_eyebrow",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(5, 10):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 4)]],
                    "group_id": "right_eyebrow",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(10, 14):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 3)]],
                    "group_id": "left_eye",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(15, 19):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 3)]],
                    "group_id": "right_eye",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(20, 22):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 3 + 200)]],
                    "group_id": "nose",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(0, 6):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 2 + num * 0.01 * width), round(height / 2)]],
                    "group_id": "mouse",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            for num in range(30, 35):
                shape = {
                    "label": "{}".format(num),
                    "points": [[round(width / 3 + (num - 30) * 0.01 * width), round(height / 2) - 200]],
                    "group_id": "face",
                    "shape_type": "point",
                    "flags": {}
                }
                new_shapes.append(shape)

            file["shapes"] = new_shapes
            with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
                json.dump(file, f, ensure_ascii=False, indent=4)
            self.loadFile(self.filename)
            self.togglePolygons(True)
        except Exception as e:
            print(e)

    def GeneratingBisectors(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]

        c = CalAll()
        c.shapes = shapes

        c.CalUpperLipUpper()
        c.CalUpperLipLower()
        c.CalLowerLipUpper()
        c.CalLowerLipLower()

        content["shapes"] = shapes

        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)

    def ReconstructionOcclusion(self):
        self.saveFile()
        with open(osp.splitext(self.filename)[0] + '.json', 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
        shapes = content["shapes"]
        for shape in shapes:
            if "visibilityArray" in shape:
                shape["visibilityArray"] = 1.0

        content["shapes"] = shapes
        with open(osp.splitext(self.filename)[0] + '.json', 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        self.loadFile(self.filename)

    def enableToggleLabel(self, enabled):
        self._config["toggle"] = enabled
        self.actions.toggleLabel.setChecked(enabled)
        self.loadFile(self.filename)

    def enableToggleLine(self, enabled):
        self._config["toggleLine"] = enabled
        self.actions.toggleLabel.setChecked(enabled)
        self.loadFile(self.filename)