import wx
import redcap
import wx.adv

USE_DATEPICKCTRL = 1

RACES = []  # ['American Indian/Alaska Native', 'Asian', 'Native Hawaiian/Pacific Islander',
# 'Black or African American',
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
        self.enrollments = []

        self.panel = wx.Panel(self, wx.ID_ANY)
        # self.input_panel = wx.Panel(self.panel, wx.ID_ANY, style=wx.RAISED_BORDER)
        self.panel.Disable()  # disable interaction with main window
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_sizer = wx.BoxSizer()
        self.output_sizer = wx.GridBagSizer(11, 11)

        title = wx.StaticText(self.panel, label='Cumulative Enrollment Report')
        self.error = wx.StaticText(self.panel)
        self.error.Hide()
        self.error.SetForegroundColour(wx.RED)
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
        update.SetDefault()
        clear = wx.Button(self.panel, label='Reset')

        update.Bind(wx.EVT_BUTTON, self.update)
        clear.Bind(wx.EVT_BUTTON, self.clear)

        self.sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.input_sizer.Add(self.grant_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.protocol_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.start_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.start_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.end_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.end_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(update, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(clear, 0, wx.ALL | wx.CENTER, 5)
        self.sizer.Add(self.input_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.Add(self.error, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.Add(wx.StaticLine(self.panel, -1),
                       flag=wx.ALL | wx.EXPAND, border=5)
        # self.sizer.Add(self.panel, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # self.input_panel.SetSizer(self.input_sizer)
        self.panel.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Show()  # put main window in background

        frame = APIKeyFrame(parent=self)

    def fill_options(self):
        self.grant_list.InsertItems([g.replace(' ', '').split(',')[1] for g in self.project.export_metadata(
            fields=['grant'])[0]['select_choices_or_calculations'].split('|')], 0)
        self.protocol_list.InsertItems([p.replace(' ', '').split(',')[1] for p in self.project.export_metadata(
            fields=['protocol'])[0]['select_choices_or_calculations'].split('|')], 0)
        self.fill_output()
        self.sizer.Add(self.output_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.AddSpacer(20)
        self.sizer.Fit(self)

    def fill_output(self):
        cat = wx.StaticText(self.panel, label='Ethnic Categories')
        self.output_sizer.Add(cat, pos=(0, 1),
                              span=wx.GBSpan(1, 16), flag=wx.ALIGN_CENTER)
        self.output_sizer.Add(wx.StaticLine(self.panel, -1),
                              pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5, span=wx.GBSpan(1, 16))

        global RACES
        RACES = [r.split(', ')[1].strip() for r in self.project.export_metadata(
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
        self.fill_zeros()
        # self.print_grid_bag(self.output_sizer)
        self.output_sizer.Add(wx.StaticText(self.panel, label='<- Total Enrolled'), pos=(12, 15),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)

    def fill_races(self):
        i_race = 0
        i_pos = 0
        while i_race < len(RACES):
            if RACES[i_race] != 'Black':
                self.output_sizer.Add(wx.StaticText(self.panel, label=RACES[i_race]),
                                      pos=(4 + i_pos, 0), flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
                i_pos += 1
            i_race += 1

        self.output_sizer.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL),
                              pos=(4 + i_pos, 0), flag=wx.EXPAND)

        self.output_sizer.Add(wx.StaticText(self.panel, label='Totals by Gender/Ethnicity'), pos=(5 + i_pos, 0),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        self.sizer.Fit(self)

    def fill_ethnicities(self):
        for i in range(len(ETHNICITIES)):
            self.output_sizer.Add(wx.StaticLine(self.panel, style=wx.LI_VERTICAL),
                                  pos=(3, (i * 4) + 1), flag=wx.EXPAND, border=0,
                                  span=wx.GBSpan(10, 1))
            self.output_sizer.Add(wx.StaticText(self.panel, label=ETHNICITIES[i]),
                                  pos=(2, (i * 4) + 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5, span=wx.GBSpan(1, 3))
        self.output_sizer.Add(wx.StaticLine(self.panel, style=wx.LI_VERTICAL),
                              pos=(3, (len(ETHNICITIES) * 4) + 1), flag=wx.ALL | wx.EXPAND, border=5,
                              span=wx.GBSpan(10, 1))
        self.sizer.Fit(self)

    def fill_genders(self):
        for i in range(len(ETHNICITIES)):
            for j in range(len(GENDERS)):
                self.output_sizer.Add(wx.StaticText(self.panel, label=GENDERS[j]),
                                      pos=(3, (i * 4) + 2 + j), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

        self.output_sizer.Add(wx.StaticText(self.panel, label='Totals By Race'),
                              pos=(3, 14), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

    def fill_zeros(self):
        for i in range(len(ETHNICITIES)+1):
            if i == len(ETHNICITIES):
                self.fill_column((i * 4) + 2, '0')
            else:
                for j in range(len(GENDERS)):
                    self.fill_column((i * 4) + 2 + j, '0')

    def fill_column(self, col, content):
        for i in range(8):
            offset = 0
            if i == 7:
                offset = 1
            self.output_sizer.Add(wx.StaticText(self.panel, label=content), pos=(i + 4 + offset, col),
                                  flag=wx.ALIGN_CENTER, border=5)

    def update(self, evt):
        self.error.Hide()
        if self.start_date.GetValue() > self.end_date.GetValue():
            self.error.SetLabelText('Start date must be earlier than end date.')
            self.error.SetForegroundColour(wx.RED)
            self.error.Show()
            self.sizer.Fit(self)
            return

        self.enrollments = self.project.export_records(raw_or_label='label', fields=['enrollment', 'grant', 'protocol'])
        grant_selection = [self.grant_list.GetItems()[i] for i in self.grant_list.GetSelections()]
        protocol_selection = [self.protocol_list.GetItems()[i] for i in self.protocol_list.GetSelections()]
        ids = self.filter_enrollments(protocol_selection, grant_selection)
        if ids:
            participants = self.project.export_records(records=ids, raw_or_label='label', fields=['gender', 'ethnicity', 'race'])
            self.fill_table(participants=participants)
        else:
            self.fill_table(string='0')

        self.sizer.Fit(self)

    def filter_enrollments(self, pr_sel, gr_sel):
        ids = []
        for e in self.enrollments:
            if e.get('grant') and e.get('protocol') and e.get('enrollment'):
                if e.get('grant') in gr_sel and e.get('protocol') in pr_sel:
                    enrollment = wx.DateTime()
                    enrollment.ParseISODate(e['enrollment'])
                    if self.start_date.GetValue() < enrollment < self.end_date.GetValue():
                        ids.append(e.get('record_id'))
        print(ids)
        return ids

    def fill_table(self, participants=None, string=None):
        race_totals = {}
        for eth in range(len(ETHNICITIES)):
            for gen in range(len(GENDERS)):
                offset = 0
                gen_tot = 0
                for race in range(len(RACES)):
                    if RACES[race] == 'Black':
                        offset = -1
                        continue
                    count = 0
                    if not string:
                        count = self.get_count_with_filter(participants, RACES[race], GENDERS[gen], ETHNICITIES[eth])
                    gen_tot += count
                    race_totals[RACES[race]] = race_totals.get(RACES[race], 0) + count
                    race_total_text = self.output_sizer.FindItemAtPosition((race + 4 + offset, 14))
                    if race_total_text:
                        if not string:
                            race_total_text.GetWindow().SetLabelText(str(race_totals[RACES[race]]))
                        else:
                            race_total_text.GetWindow().SetLabelText(string)

                    text = self.output_sizer.FindItemAtPosition((race + 4 + offset, (eth * 4) + gen + 2))
                    if text:
                        if not string:
                            text.GetWindow().SetLabelText(str(count))
                        else:
                            text.GetWindow().SetLabelText(string)
                text = self.output_sizer.FindItemAtPosition((len(RACES) + 1 + 4 + offset, (eth * 4) + gen + 2))
                if text:
                    if not string:
                        text.GetWindow().SetLabelText(str(gen_tot))
                    else:
                        text.GetWindow().SetLabelText(string)
        text = self.output_sizer.FindItemAtPosition((12, 14))
        if text:
            if not string:
                text.GetWindow().SetLabelText(str(len(participants)))
            else:
                text.GetWindow().SetLabelText(string)


    def get_count_with_filter(self, participants, race, gender, ethnicity):
        count = 0
        for p in participants:
            if p['race'] == race and p['gender'] == gender and p['ethnicity'] == ethnicity:
                count += 1

        return count

    def clear(self, evt):
        self.grant_list.SetSelection(-1)
        self.protocol_list.SetSelection(-1)
        self.start_date.SetValue(wx.DateTime.Now())
        self.end_date.SetValue(wx.DateTime.Now())

    def get_number_of_grants_protocols(self):
        count = 0
        for r in self.enrollments:
            if r['redcap_repeat_instrument']:
                count += 1

        return count

    def print_grid_bag(self, sizer):
        for row in range(sizer.GetEffectiveRowsCount()):
            for col in range(sizer.GetEffectiveColsCount()):
                item = sizer.FindItemAtPosition((row, col))
                if item:
                    print("X", end=' ')
                else:
                    print("_", end=' ')
            print()


if __name__ == '__main__':
    app = wx.App()
    frame = ReportFrame()
    app.MainLoop()
