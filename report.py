import wx
import redcap
import wx.adv

USE_DATEPICKCTRL = 1

RACES = []  # ['American Indian/Alaska Native', 'Asian', 'Native Hawaiian/Pacific Islander', 'Black or African American',
# 'White', 'More Than One Race', 'Unknown or Not Reported', 'Totals by Gender/Ethnicity']
ETHNICITIES = []
GENDERS = []


class APIKeyFrame(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(parent=parent, title='API Key')
        self.parent = parent
        self.api_key = None
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(self.panel, label='Paste your api key and REDCap url below:')
        self.api_key_text = wx.TextCtrl(self.panel, value='35C5648FC6507875553AFF69D2768E3B', size=wx.Size(300, 10))
        self.redcap_url_text = wx.TextCtrl(self.panel, value="https://redcap.ahc.umn.edu/api/")
        self.error_str = wx.StaticText(self.panel, label='')
        self.error_str.Hide()
        self.error_str.SetForegroundColour(wx.RED)
        connect_btn = wx.Button(self.panel, label='Connect')

        connect_btn.Bind(wx.EVT_BUTTON, self.connect)
        connect_btn.SetDefault()

        self.sizer.Add(text, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.sizer.Add(self.api_key_text, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.redcap_url_text, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.error_str, 1, wx.ALL | wx.ALIGN_LEFT, 5)
        self.sizer.Add(connect_btn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Show()

    def connect(self, evt):
        self.parent.api_key = self.api_key_text.GetValue()
        self.parent.redcap_url = self.redcap_url_text.GetValue()
        try:
            self.parent.project = redcap.Project(self.parent.redcap_url, self.parent.api_key)
            self.parent.fill_options()
            self.parent.Raise()
            self.parent.panel.Enable()
            self.Destroy()
        except redcap.RedcapError as e:
            self.error_str.SetLabelText(str(e))
            self.error_str.Show()
            self.sizer.Fit(self)


class ReportFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='NIH Report')
        self.api_key = None
        self.project = None

        self.panel = wx.Panel(self, wx.ID_ANY)
        # self.input_panel = wx.Panel(self.panel, wx.ID_ANY, style=wx.RAISED_BORDER)
        self.panel.Disable()  # disable interaction with main window
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_sizer = wx.BoxSizer()
        self.output_sizer = wx.GridBagSizer(11, 11)

        title = wx.StaticText(self.panel, label='Cumulative Enrollment Report')
        self.bold = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.small_bold = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        title.SetFont(self.bold)
        self.start_label = wx.StaticText(self.panel, label='From')
        self.start_date = wx.adv.DatePickerCtrl(self.panel)
        self.end_label = wx.StaticText(self.panel, label='to')
        self.end_date = wx.adv.DatePickerCtrl(self.panel)
        self.grant_list = wx.ListBox(self.panel, style=wx.LB_MULTIPLE)
        self.protocol_list = wx.ListBox(self.panel, style=wx.LB_MULTIPLE)
        # self.output = wx.StaticText(self.panel, label='0')
        update = wx.Button(self.panel, label='Update')

        self.sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.input_sizer.Add(self.grant_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.protocol_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.start_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.start_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.end_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.end_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(update, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.input_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        # self.sizer.Add(self.panel, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # self.input_panel.SetSizer(self.input_sizer)
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Show()  # put main window in background

        frame = APIKeyFrame(parent=self)

    def print_api_key(self):
        print(self.api_key)

    def fill_options(self):
        cat = wx.StaticText(self.panel, label='Ethnic Categories')
        # cat.SetFont(self.small_bold)
        self.output_sizer.Add(cat, pos=(0, 1),
                              span=wx.GBSpan(1, 9), flag=wx.ALIGN_CENTER)
        self.grant_list.InsertItems([g.replace(' ', '').split(',')[1] for g in self.project.export_metadata(
            fields=['grant'])[0]['select_choices_or_calculations'].split('|')], 0)
        self.protocol_list.InsertItems([p.replace(' ', '').split(',')[1] for p in self.project.export_metadata(
            fields=['protocol'])[0]['select_choices_or_calculations'].split('|')], 0)

        global RACES
        RACES = [r.replace(' ', '').split(',')[1] for r in self.project.export_metadata(
            fields=['race'])[0]['select_choices_or_calculations'].split('|')]
        self.fill_races()

        global ETHNICITIES
        ETHNICITIES = [e.split(', ')[1].strip() for e in self.project.export_metadata(
            fields=['ethnicity'])[0]['select_choices_or_calculations'].split('|')]
        self.fill_ethnicities()

        global GENDERS
        GENDERS = [e.split(', ')[1].strip() for e in self.project.export_metadata(
            fields=['gender'])[0]['select_choices_or_calculations'].split('|')]
        self.fill_genders()
        self.fill_numbers()
        self.output_sizer.Add(wx.StaticText(self.panel, label='<- Total Enrolled'), pos=(11, 11),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        self.sizer.Add(self.output_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.AddSpacer(20)
        self.sizer.Fit(self)

    def fill_races(self):
        i_race = 0
        i_pos = 0
        while i_race < len(RACES):
            if RACES[i_race] != 'Black':
                self.output_sizer.Add(wx.StaticText(self.panel, label=RACES[i_race]),
                                      pos=(4 + i_pos, 0), flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
                i_pos += 1
            i_race += 1

        self.output_sizer.Add(wx.StaticText(self.panel, label='Totals by Gender/Ethnicity'), pos=(4 + i_pos, 0),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        self.sizer.Fit(self)

    def fill_ethnicities(self):
        for i in range(len(ETHNICITIES)):
            self.output_sizer.Add(wx.StaticText(self.panel, label=ETHNICITIES[i]),
                                  pos=(2, (i*3)+1), flag=wx.ALL | wx.ALIGN_CENTER, border=5, span=wx.GBSpan(1, 3))
        self.sizer.Fit(self)

    def fill_genders(self):
        for i in range(3):
            for j in range(len(GENDERS)):
                self.output_sizer.Add(wx.StaticText(self.panel, label=GENDERS[j]),
                                      pos=(3, (i * 3) + 1 + j), flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        self.output_sizer.Add(wx.StaticText(self.panel, label='Totals By Race'),
                              pos=(3, 10), flag=wx.ALL | wx.ALIGN_CENTER, border=5)
        self.output_sizer.Add(wx.StaticLine(self.panel, size=(2, 50), style=wx.LI_VERTICAL),
                              pos=(3, 11), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

    def fill_numbers(self):
        for i in range(10):
            self.fill_column(i, '0')

    def fill_column(self, col, content):
        for i in range(8):
            self.output_sizer.Add(wx.StaticText(self.panel, label='0'), pos=(i+4, col+1),
                                  flag=wx.ALIGN_CENTER, border=5)

if __name__ == '__main__':
    app = wx.App()
    frame = ReportFrame()
    app.MainLoop()
