# -*- coding: utf-8 -*-
# @Author  : LG

from ISAT.widgets.plugin_base import PluginBase
from PyQt5 import QtCore, QtGui, QtWidgets
from skimage.draw import draw
import numpy as np
import cv2
import os


class MaskExportPlugin(PluginBase):
    def __init__(self):
        super().__init__()

    def init_plugin(self, mainwindow):
        self.mainwindow = mainwindow
        self.init_ui()

        self.pixmap:QtGui.QPixmap = None

    def enable_plugin(self):
        self.mainwindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dock)
        self.dock.show()
        self.update_image_mask()
        self.enabled = True

    def disable_plugin(self):
        self.mainwindow.removeDockWidget(self.dock)
        self.enabled = False

    def get_plugin_author(self) -> str:
        return "yatengLG"

    def get_plugin_version(self) -> str:
        return "1.0.0"

    def get_plugin_description(self) -> str:
        return "Export mask."

    def after_image_open_event(self):
        self.update_image_mask()

    def after_annotation_changed_event(self):
        self.update_image_mask()

    def after_annotations_saved_event(self):
        if self.pixmap is None:
            return

        try:
            filepath = self.mainwindow.files_list[self.mainwindow.current_index]
            save_path = os.path.join(self.mainwindow.label_root, filepath.split('.')[0] + '_mask.png')
            self.pixmap.save(save_path)
        except Exception as e:
            print(e)

    def init_ui(self):
        self.dock = QtWidgets.QDockWidget(self.mainwindow)
        self.dock.setWindowTitle('Mask Export Plugin')
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.invert_checkbox = QtWidgets.QCheckBox()
        self.invert_checkbox.setText('Invert')
        self.invert_checkbox.setMaximumHeight(36)
        self.invert_checkbox.stateChanged.connect(self.update_image_mask)
        main_layout.addWidget(self.invert_checkbox)

        self.image_mask = QtWidgets.QLabel()
        self.image_mask.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_mask.setMinimumHeight(200)
        self.image_mask.setStyleSheet("""background-color: #6F737A;""")
        main_layout.addWidget(self.image_mask)

        widget = QtWidgets.QWidget()
        widget.setMaximumHeight(36)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        main_layout.addWidget(widget)

        self.dilate_iterations = QtWidgets.QSlider()
        self.dilate_iterations.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.dilate_iterations.setTracking(True)
        self.dilate_iterations.setTickPosition(QtWidgets.QSlider.TickPosition.TicksAbove)
        self.dilate_iterations.setMinimum(-5)
        self.dilate_iterations.setMaximum(5)
        self.dilate_iterations.setPageStep(1)
        self.dilate_iterations.setValue(0)
        self.dilate_iterations.valueChanged.connect(self.update_image_mask)
        self.dilate_label = QtWidgets.QLabel(f'Dilate: {self.dilate_iterations.value()}')
        layout.addWidget(self.dilate_label)
        layout.addWidget(self.dilate_iterations)

        self.dock.setWidget(main_widget)
        self.mainwindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dock)

        if not self.enabled:
            self.disable_plugin()

    def update_image_mask(self):
        self.dilate_label.setText('Dilate: {:>2d}'.format(self.dilate_iterations.value()))

        if self.mainwindow.scene.image_item is None:
            return
        width = self.mainwindow.scene.image_item.pixmap().width()
        height = self.mainwindow.scene.image_item.pixmap().height()

        img = np.zeros(shape=(height, width), dtype=np.uint8)

        polygons = sorted(self.mainwindow.polygons, key=lambda obj:obj.zValue())
        for polygon in polygons:
            segmentation = []
            for point in polygon.points:
                point = point + polygon.pos()
                segmentation.append((round(point.y(), 2), round(point.x(), 2)))

            if polygon.category == "__background__":
                self.fill_polygon(segmentation, img, color=0)
            else:
                self.fill_polygon(segmentation, img, color=255)

        if self.dilate_iterations.value() != 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 矩形核
            if self.dilate_iterations.value() > 0:
                img = cv2.dilate(img, kernel, iterations=self.dilate_iterations.value())
            else:
                img = cv2.erode(img, kernel, iterations=-self.dilate_iterations.value())

        if self.invert_checkbox.isChecked():
            img = np.invert(img)

        # to pixmap
        qimg = QtGui.QImage(img.data, width, height, width * 1, QtGui.QImage.Format.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.pixmap = pixmap

        scale_factor = min(self.image_mask.width() / pixmap.width(),
                           self.image_mask.height() / pixmap.height(),
                           )
        pixmap = pixmap.scaled(
            pixmap.width() * scale_factor,
            pixmap.height() * scale_factor,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.FastTransformation
        )

        self.image_mask.setPixmap(pixmap)

    @staticmethod
    def fill_polygon(segmentation, img: np.ndarray, color: int):
        xs = [x for x, y in segmentation]
        ys = [y for x, y in segmentation]
        rr, cc = draw.polygon(xs, ys, img.shape)
        img[rr, cc] = color