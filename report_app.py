#!/usr/bin/env python3
"""
Application to generate NIH demographic reports from REDCap data via the REDCap API. Report is displayed in app
with the option to export to CSV.
"""
import wx

from api_key_frame import APIKeyFrame
from report_window import ReportWindow

USE_DATEPICKCTRL = 1  # Needed to access date picker widget


class ReportFrame(wx.Frame):
    """
    Report app main frame
    """

    def __init__(self):
        super().__init__(parent=None, title='NIH Report')
        self.project = None

        APIKeyFrame(parent=self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.report_window = ReportWindow(self)
        self.sizer.Add(self.report_window, 1, wx.EXPAND)

        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        self.menuExport = file_menu.Append(wx.ID_SAVEAS, 'Export .csv', 'Export .csv report')
        self.menuExport.Enable(enable=False)
        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.report_window.on_export, self.menuExport)

        self.SetSizer(self.sizer)


if __name__ == '__main__':
    app = wx.App(True)
    report_frame = ReportFrame()
    app.MainLoop()
