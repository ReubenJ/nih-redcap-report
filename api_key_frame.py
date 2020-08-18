"""
Class for handling the input of the REDCap API key/url and connecting to REDCap
"""
import wx
import redcap


class APIKeyFrame(wx.Frame):
    """
    Creates a frame to enter your API key and REDCap API URL
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent, title='API Key/URL')
        self.parent = parent
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(self.panel, label='Paste your api key and REDCap url below:')
        self.api_key_text = wx.TextCtrl(self.panel, value='', size=wx.Size(300, 10))
        self.redcap_url_text = wx.TextCtrl(self.panel, value="https://redcap.ahc.umn.edu/api/")

        self.error_str = wx.StaticText(self.panel, label='')
        self.error_str.Hide()
        self.error_str.SetForegroundColour(wx.RED)

        connect_btn = wx.Button(self.panel, label='Connect')
        connect_btn.Bind(wx.EVT_BUTTON, self.connect)
        connect_btn.SetDefault()
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.sizer.Add(text, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.sizer.Add(self.api_key_text, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.redcap_url_text, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.error_str, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.sizer.Add(connect_btn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Show()

    def on_close(self, evt):
        """
        Closes parent if the API window is closed without connecting
        :param evt:
        """
        self.parent.Destroy()

    def connect(self, evt):
        """
        Establishes a connection with the REDCap API and stores a reference to the project
        object in the parent window.
        :param evt: Event which triggered the connection
        """
        api_key = self.api_key_text.GetValue()
        redcap_url = self.redcap_url_text.GetValue()
        try:
            self.parent.project = redcap.Project(redcap_url, api_key)
            self.parent.report_window.fill_options()
            self.parent.report_window.Enable()
            self.parent.sizer.Fit(self.parent)
            w, h = self.parent.report_window.GetSize()
            max = wx.Display().GetClientArea()
            self.parent.SetSize(min(w + 100, max.Width), min(h + 100, max.Height))

            # Enable scrolling after content is filled
            # w, h = self.parent.report_window.sizer.GetMinSize()
            # self.parent.report_window.SetVirtualSize((w, h))
            fontsz = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT).GetPixelSize()
            self.parent.report_window.SetScrollRate(fontsz.x, fontsz.y)
            self.parent.report_window.EnableScrolling(True, True)

            # Fire a size event to fix disappearing widgets on scroll
            wx.PostEvent(self.parent.GetEventHandler(), wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId()))

            self.parent.Show()
            self.Destroy()

        except redcap.RedcapError as e:
            self.error_str.SetLabelText(str(e))
            self.error_str.Show()
            self.sizer.Fit(self)
