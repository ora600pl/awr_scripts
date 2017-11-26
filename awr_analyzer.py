import plotly.offline as py
import plotly.graph_objs as go
import sys
import os
import re
from datetime import datetime
from plotly import tools


class StatspackAnalyzer(object):
    def __init__(self, dirname, name_pattern):
        self.dirname = dirname
        self.name_pattern = name_pattern
        self.event_classes = ["System I/O", "Other", "User I/O", "Configuration", "Cluster", "Concurrency",
                              "Administrative", "Application", "Network", "Commit"]

        self.load_profile_elems = ["DB time(s):", "DB CPU(s):", "Redo size:", "Logical reads:", "Block changes:",
                                   "Physical reads:", "Physical writes:", "User calls:", "Parses:", "Hard parses:",
                                   "W/A MB processed:", "Logons:", "Executes:", "Rollbacks:", "Transactions:"]

    def get_class_name(self, event_name_short):
        for event_name in self.event_class_name:
            if event_name.startswith(event_name_short):
                return self.event_class_name[event_name]

        return "NONE"

    def is_float(self, val):
        try:
            x = float(val.replace(",", ""))
            return True
        except:
            return False

    def plot(self):

        snap_data = {}
        snap_data_profile = {}
        snap_data_cpu = {}

        for fname in os.listdir(self.dirname):
            if fname.endswith("txt") and fname.find(self.name_pattern) >= 0:
                report_file = open(self.dirname + "/" + fname, "r").readlines()
                wait_class_section = False
                load_profile_section = False
                host_cpu_section = False
                event_class_wait_sum = {}
                for report_line in report_file:
                    try:
                        report_line_words = report_line.split()
                        report_line_long_words = re.split("\s{2,}", report_line)

                        if report_line.find("Begin Snap:") >= 0:
                            date = report_line.split()[3] + " " + report_line.split()[4]
                            date = datetime.strptime(date, "%d-%b-%y %H:%M:%S").strftime("%Y%m%d:%H:%M")
                            date = date + " (" + report_line.split()[2] + ")"
                            snap_data[date] = {}
                            snap_data_profile[date] = {}
                            snap_data_cpu[date] = {}

                        elif report_line.find("DB time:") >= 0:
                            snap_data[date]["DB time"] = float(report_line_words[2].replace(",","")) * 60

                        elif report_line.startswith("Load Profile"):
                            load_profile_section = True

                        elif report_line.startswith("Wait Classes by Total Wait Time"):
                            wait_class_section = True

                        elif report_line.find("Host CPU") >= 0:
                            host_cpu_section = True
                            wait_class_section = False
                            for class_name in self.event_classes:
                                if snap_data[date].get(class_name, -1) == -1:
                                    snap_data[date][class_name] = 0

                        elif host_cpu_section and len(report_line_long_words) > 5 and \
                                self.is_float(report_line_long_words[1]):
                            snap_data_cpu[date]["Begin"] = float(report_line_long_words[3])
                            snap_data_cpu[date]["End"] = float(report_line_long_words[4])
                            snap_data_cpu[date]["User"] = float(report_line_long_words[5])
                            snap_data_cpu[date]["System"] = float(report_line_long_words[6])
                            snap_data_cpu[date]["Idle"] = float(report_line_long_words[8])
                            snap_data_cpu[date]["WIO"] = float(report_line_long_words[7])
                            host_cpu_section = False

                        elif load_profile_section and len(report_line_long_words) > 2 and \
                                        report_line_long_words[1] in self.load_profile_elems:

                            snap_data_profile[date][report_line_long_words[1][:-1]] = \
                                float(report_line_long_words[2].replace(",",""))

                        elif report_line.startswith("Instance Efficiency Indicators"):
                            load_profile_section = False

                        elif len(report_line_words) > 2 \
                                and (report_line_words[0] + " " + report_line_words[1] in self.event_classes) \
                                and wait_class_section \
                                and report_line.startswith(report_line_words[0]):

                            snap_data[date][report_line_words[0] + " " + report_line_words[1]] = \
                                float(report_line_words[3].replace(",", ""))

                        elif len(report_line_words) > 2 \
                             and (report_line_words[0] in self.event_classes) \
                             and wait_class_section \
                             and report_line.startswith(report_line_words[0]):

                            snap_data[date][report_line_words[0]] = float(report_line_words[2].replace(",", ""))

                        elif report_line.find("Wait Event Histogram  DB/Inst:")>0 and wait_class_section:
                            wait_class_section = False

                            for class_name in self.event_classes:
                                snap_data[date][class_name] = event_class_wait_sum.get(class_name,0)

                    except BaseException as e:
                        print(e)
                        print(report_line)
                        raise

        data_x = sorted(snap_data.keys())
        data_y = {}
        data_y_profile = {}
        data_y_cpu = {}

        for i in data_x:
            for j in snap_data[i]:
                if data_y.get(j, -1) == -1:
                    data_y[j] = []
                    data_y[j].append(snap_data[i][j])
                else:
                    data_y[j].append(snap_data[i][j])

            for j in snap_data_profile[i]:
                if data_y_profile.get(j, -1) == -1:
                    data_y_profile[j] = []
                    data_y_profile[j].append(snap_data_profile[i][j])
                else:
                    data_y_profile[j].append(snap_data_profile[i][j])

            for j in snap_data_cpu[i]:
                if data_y_cpu.get(j, -1) == -1:
                    data_y_cpu[j] = []
                    data_y_cpu[j].append(snap_data_cpu[i][j])
                else:
                    data_y_cpu[j].append(snap_data_cpu[i][j])

        fig = tools.make_subplots(rows=3, cols=1, subplot_titles=("Wait Event Class & DB Time (sec)",
                                                                  "Load Profile (Per Second)",
                                                                  "Host CPU"))

        for series in data_y:
            fig.append_trace(go.Scatter(x=data_x,
                                         fill="tozeroy",
                                         y=data_y[series],
                                         name=series
                                         ), 1, 1)

        for series in data_y_profile:
            fig.append_trace(go.Scatter(x=data_x,
                                           fill="tozeroy",
                                           y=data_y_profile[series],
                                           name=series
                                           ), 2, 1)

        for series in data_y_cpu:
            fig.append_trace(go.Scatter(x=data_x,
                                           fill="tozeroy",
                                           y=data_y_cpu[series],
                                           name=series
                                           ), 3, 1)

        py.plot(fig, filename=self.name_pattern + ".html")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        sa = StatspackAnalyzer(sys.argv[1], sys.argv[2])
        sa.plot()
    else:
        print("This script by Kamil Stawiarski (@ora600pl) is to help you with visualizing data from multiple "
              "awr text reports")

        print("Usage:")
        print("python awr_analyzer.py /path/to/reports/ pattern_to_filter_reports_by_name")
        print("You have to install plotly first [pip install plotly]\n")
        print("Details can be found on this blog: blog.ora-600.pl "
              "and GitHub: https://github.com/ora600pl/statspack_scripts")
