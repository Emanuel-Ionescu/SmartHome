import matplotlib.pyplot as plt
import matplotlib.dates
import numpy as np
import os
import datetime

color_dict = {
    "ff0000" : 1,
    "ff8000" : 2,
    "ffff00" : 3,
    "80ff00" : 4,
      "ff00" : 5,
      "ff80" : 6,
      "ffff" : 7,
      "80ff" : 8,
        "ff" : 9,
    "8000ff" : 10,
    "ff00ff" : 11,
    "ffffff" : 12,
    "46424f" : 0
}

if __name__ == "__main__":

    time_ax = []
    plots = [] ## each user has an element -> each element has a list of data for each bulb
    l_data = {}

    for usr in os.listdir("users_data"):
        if os.path.isdir("users_data/{}".format(usr)):
            f = open("users_data/{}/.usage_log_lights".format(usr), 'r')
            raw = f.read()
            f.close()

            if raw != '':
                l_data[usr] = {}

                for line in raw.splitlines():
                    time_val, bulb, color = line.split(':')

                    time_val = time_val.replace(".", " ")
                    time_val = time_val.replace("-", " ")
                    dd,mm,yy,h,m = time_val.split(" ")
                    time_val = datetime.datetime(int(yy), int(mm), int(dd), int(h), int(m), 0)
                    
                    if not bulb in l_data[usr].keys():
                        l_data[usr][bulb] = ([], [])

                    l_data[usr][bulb][0].append(time_val)
                    l_data[usr][bulb][1].append(color)

                    time_ax.append(time_val)

                plots_for_key = []
                for bulb in l_data[usr].keys():
                    x = l_data[usr][bulb][0]
                    y = [color_dict[col] for col in l_data[usr][bulb][1]]
                    plots_for_key.append((x, y, "{} - {}".format(usr, bulb)))

                plots.append(plots_for_key)

    time_ax = list(dict.fromkeys(time_ax))
    time_ax.sort()

    first_date = time_ax[0].replace(hour=0, minute=0, second=0)
    last_date = time_ax[-1].replace(hour=23, minute=59, second=59)

    if len(plots) == 1:

        for color in color_dict.keys():
            plt.axhline(color_dict[color], color='#' + color.zfill(6), ls="--", lw = 1)

        for p in plots[0]:
            plt.plot(p[0], p[1], '-o', label=p[2])

        plt.legend()
    else:
        figure, axis = plt.subplots(len(plots), sharex=True)
        index = 0
        for plot_for_key in plots:
            for p in plot_for_key:
                axis[index].plot(p[0], p[1], '-o', label=p[2].split('-')[1])
            
            for color in color_dict.keys():
                axis[index].axhline(color_dict[color], color='#' + color.zfill(6), ls="--", lw = 1)
            
            axis[index].set_facecolor("darkgray")
            axis[index].set_title(p[2].split('-')[0])
            axis[index].legend()
            index += 1

    plt.ylim(-1, 13)
    plt.xlim(first_date, last_date)
    plt.show()

