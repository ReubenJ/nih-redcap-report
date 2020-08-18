"""
Window to display input options and output measures for NIH demographics report
"""
import csv

import wx
import wx.adv


RACES = ['American Indian/Alaska Native', 'Asian', 'Native Hawaiian or Other Pacific Islander',
         'Black or African American', 'White', 'More Than One Race', 'Unknown']
ETHNICITIES = ['Not Hispanic or Latino', 'Hispanic or Latino', 'Unknown']
GENDERS = ['Female', 'Male', 'Unknown']


class ReportWindow(wx.ScrolledWindow):
    """
    Creates a window for choosing the report options, viewing the demographic measures, and exporting the report.
    """

    def __init__(self, parent, *args, **kw):
        super().__init__(parent, -1, style=wx.TAB_TRAVERSAL, *args, **kw)
        self.parent = parent
        # wx.ScrolledWindow.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        self.participants = None  # To be filled on update with input options

        # self = wx.Panel(self)
        self.Disable()  # disable interaction with main window

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_sizer = wx.BoxSizer()
        self.output_sizer = wx.GridBagSizer(11, 11)

        self.error = wx.StaticText(self)
        self.error.Hide()
        self.error.SetForegroundColour(wx.RED)

        title = wx.StaticText(self, label='Cumulative Enrollment Report')
        title.SetFont(wx.Font().Bold())

        start_label = wx.StaticText(self, label='From')
        self.start_date = wx.adv.DatePickerCtrl(self)
        end_label = wx.StaticText(self, label='to')
        self.end_date = wx.adv.DatePickerCtrl(self)
        self.grant_list = wx.ListBox(self, style=wx.LB_MULTIPLE)
        self.protocol_list = wx.ListBox(self, style=wx.LB_MULTIPLE)
        update = wx.Button(self, label='Update')
        update.SetDefault()
        reset_button = wx.Button(self, label='Reset Options')
        self.export_button = wx.Button(self, label='Export to CSV')
        self.export_button.Disable()

        update.Bind(wx.EVT_BUTTON, self.update)
        reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export)

        self.input_sizer.Add(self.grant_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.protocol_list, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(start_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.start_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(end_label, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(self.end_date, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(update, 0, wx.ALL | wx.CENTER, 5)
        self.input_sizer.Add(reset_button, 0, wx.ALL | wx.CENTER, 5)
        # self.input_sizer.Fit(self)

        self.sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.Add(self.input_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.Add(self.error, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.Add(wx.StaticLine(self, -1), flag=wx.ALL | wx.EXPAND, border=5)
        self.sizer.Add(self.output_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.export_button, 0, wx.RIGHT | wx.ALIGN_RIGHT, 50)
        self.sizer.AddSpacer(20)

        self.SetSizer(self.sizer)
        # self.sizer.Fit(self)
        # self.Fit()

    def show_error(self, text='Error'):
        """
        Shows the error text widget with the given text
        :param text: Text to show
        """
        self.error.SetLabel(text)
        self.error.Show()
        # self.Fit()

    def on_export(self, evt):
        """
        Opens file dialog to choose where to save, writes csv if save is chosen.
        :param evt: Event which triggered export
        """
        with wx.FileDialog(self, "Filename to save", defaultFile='report_' +
                                                                 self.start_date.GetValue().FormatISODate() +
                                                                 '_to_' +
                                                                 self.end_date.GetValue().FormatISODate() + '.csv',
                           defaultDir=wx.StandardPaths.GetDocumentsDir(wx.StandardPaths.Get()),
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                pathname = dlg.GetPath()
                try:
                    with open(pathname, 'w', newline='') as file:
                        self.do_save_file(file)
                except IOError:
                    self.show_error("Can't save file.")

    def do_save_file(self, file):
        """
        Check for participants, if none show error and do nothing, otherwise write data to csv file.
        :param file: file to write to
        """
        if not self.participants:
            self.show_error("Can't export when there is no data")
        else:
            self.write_to_file(file)

    def write_to_file(self, file):
        """
        Calculate demographic measures and write to file in csv format.
        :param file: file to write to
        """
        report_writer = csv.writer(file, delimiter=',',
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # Headers
        report_writer.writerow(
            ['Grants:'] + [self.grant_list.GetItems()[i] for i in self.grant_list.GetSelections()])
        report_writer.writerow(['Protocols:'] + [self.protocol_list.GetItems()[i]
                                                 for i in self.protocol_list.GetSelections()])
        row = ['']
        for eth in range(len(ETHNICITIES)):
            for gen in range(len(GENDERS)):
                row.append(ETHNICITIES[eth] + '/' + GENDERS[gen])
        report_writer.writerow(row)

        # Table and row sums
        for race in range(len(RACES)):
            row = [RACES[race]]
            race_tot = 0
            for eth in range(len(ETHNICITIES)):
                for gen in range(len(GENDERS)):
                    count = self.get_count_with_filter(self.participants, RACES[race], GENDERS[gen],
                                                       ETHNICITIES[eth])
                    race_tot += count
                    row.append(count)
            row.append(race_tot)
            report_writer.writerow(row)

        # Column sums
        row = ['Totals by Gender and Ethnicity']
        for eth in range(len(ETHNICITIES)):
            for gen in range(len(GENDERS)):
                gen_tot = 0
                for race in range(len(RACES)):
                    count = self.get_count_with_filter(self.participants, RACES[race], GENDERS[gen],
                                                       ETHNICITIES[eth])
                    gen_tot += count
                row.append(gen_tot)
        row.append(len(self.participants))
        row.append('<- Total enrollments')
        report_writer.writerow(row)

    def fill_options(self):
        """
        Fill grant/protocol list widgets with options.
        """
        self.grant_list.InsertItems([g.split(',')[1].strip() for g in self.parent.project.export_metadata(
            fields=['grant'])[0]['select_choices_or_calculations'].split('|')], 0)
        self.protocol_list.InsertItems([p.split(',')[1].strip() for p in self.parent.project.export_metadata(
            fields=['protocol'])[0]['select_choices_or_calculations'].split('|')], 0)
        self.fill_output()
        # self.sizer.Fit(self)

    def fill_output(self):
        """
        Fill output table with title, col/row labels and 0s
        """
        cat = wx.StaticText(self, label='Ethnic Categories')
        self.output_sizer.Add(cat, pos=(0, 1),
                              span=wx.GBSpan(1, 16), flag=wx.ALIGN_CENTER)
        self.output_sizer.Add(wx.StaticLine(self, -1),
                              pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5, span=wx.GBSpan(1, 16))

        self.fill_races()
        self.fill_ethnicities()
        self.fill_genders()
        self.fill_zeros()

        self.output_sizer.Add(wx.StaticText(self, label='<- Total Enrolled'), pos=(12, 15),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        # self.output_sizer.Fit(self)

    def fill_races(self):
        """
        Fill row labels
        """
        i_race = 0
        i_pos = 0
        while i_race < len(RACES):
            if RACES[i_race] != 'Black':
                self.output_sizer.Add(wx.StaticText(self, label=RACES[i_race]),
                                      pos=(4 + i_pos, 0), flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
                i_pos += 1
            i_race += 1

        self.output_sizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL),
                              pos=(4 + i_pos, 0), flag=wx.EXPAND)

        self.output_sizer.Add(wx.StaticText(self, label='Totals by Gender/Ethnicity'), pos=(5 + i_pos, 0),
                              flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
        # self.sizer.Fit(self)

    def fill_ethnicities(self):
        """
        Fill column group labels
        """
        for i in range(len(ETHNICITIES)):
            self.output_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL),
                                  pos=(3, (i * 4) + 1), flag=wx.EXPAND, border=0,
                                  span=wx.GBSpan(10, 1))
            self.output_sizer.Add(wx.StaticText(self, label=ETHNICITIES[i]),
                                  pos=(2, (i * 4) + 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5, span=wx.GBSpan(1, 3))
        self.output_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL),
                              pos=(3, (len(ETHNICITIES) * 4) + 1), flag=wx.ALL | wx.EXPAND, border=5,
                              span=wx.GBSpan(10, 1))
        # self.sizer.Fit(self)

    def fill_genders(self):
        """
        Fill column labels
        """
        for i in range(len(ETHNICITIES)):
            for j in range(len(GENDERS)):
                self.output_sizer.Add(wx.StaticText(self, label=GENDERS[j]),
                                      pos=(3, (i * 4) + 2 + j), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

        self.output_sizer.Add(wx.StaticText(self, label='Totals By Race'),
                              pos=(3, 14), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

    def fill_zeros(self):
        """
        Fill output table with 0s
        """
        for i in range(len(ETHNICITIES) + 1):
            if i == len(ETHNICITIES):
                self.fill_column((i * 4) + 2, '0')
            else:
                for j in range(len(GENDERS)):
                    self.fill_column((i * 4) + 2 + j, '0')

    def fill_column(self, col, content):
        """
        Fill Given column with content
        :param col: column to fill
        :param content: content to fill with
        """
        for i in range(8):
            offset = 0
            if i == 7:
                offset = 1  # Offset one at the end of the column to skip the divider row
            self.output_sizer.Add(wx.StaticText(self, label=content), pos=(i + 4 + offset, col),
                                  flag=wx.ALIGN_CENTER, border=5)

    def update(self, evt):
        """
        Update output based on input choices
        :param evt: event which triggered the update
        """
        self.participants = None
        self.error.Hide()

        if self.start_date.GetValue() > self.end_date.GetValue():
            self.show_error('Start date must be earlier than end date.')
            self.toggle_export_controls(enable=False)
            return

        enrollments = self.parent.project.export_records(raw_or_label='label',
                                                              fields=['enrollment', 'grant', 'protocol'])
        grant_selection = [self.grant_list.GetItems()[i] for i in self.grant_list.GetSelections()]
        protocol_selection = [self.protocol_list.GetItems()[i] for i in self.protocol_list.GetSelections()]
        ids = self.filter_enrollments(enrollments, protocol_selection, grant_selection)
        if ids:
            self.participants = self.parent.project.export_records(records=ids, raw_or_label='label',
                                                                   fields=['gender', 'ethnicity', 'race'])
            self.fill_output_table(participants=self.participants)
            self.toggle_export_controls(enable=True)
        else:
            self.toggle_export_controls(enable=False)
            self.fill_output_table(string='0')


    def toggle_export_controls(self, enable=True):
        """
        Enable/disable export button and menu item.
        :param enable: whether to enable or disable the widgets
        """
        self.export_button.Enable(enable=enable)
        self.parent.menuExport.Enable(enable=enable)

    def filter_enrollments(self, enrollments, protocol_sel, grant_sel):
        """
        Filter all grant/protocol pairs to match the input options pr_sel, gr_sel

        :param enrollments: grant/protocol pairs from REDCap
        :param protocol_sel: protocol selection list from input options
        :param grant_sel: grant selection list from input options
        :return: list of record ids which match the selection
        """
        ids = []
        for e in enrollments:
            if e.get('grant') and e.get('protocol') and e.get('enrollment'):
                if e.get('grant') in grant_sel and e.get('protocol') in protocol_sel:
                    enrollment = wx.DateTime()
                    enrollment.ParseISODate(e['enrollment'])
                    if self.start_date.GetValue() <= enrollment <= self.end_date.GetValue():
                        ids.append(e.get('record_id'))
        return ids

    def fill_output_table(self, participants=None, string=None):
        """
        Fill output table in application with demographic measures corresponding to the chosen options
        :param participants: participants with enrollments that matched the input options
        :param string: optional string with which to fill each cell in the table
        """
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
        """
        Count participants which match the given criterion
        :param participants: list of participants who match the input options
        :param race: race to filter by
        :param gender: gender to filter by
        :param ethnicity: ethnicity to filter by
        :return: number of participants which match the filter
        """
        count = 0
        for p in participants:
            if p['race'] == race and p['gender'] == gender and p['ethnicity'] == ethnicity:
                count += 1

        return count

    def on_reset(self, evt):
        """
        Clear inputs
        :param evt: event which triggered the clear
        """
        self.grant_list.SetSelection(-1)
        self.protocol_list.SetSelection(-1)
        self.start_date.SetValue(wx.DateTime.Now())
        self.end_date.SetValue(wx.DateTime.Now())
