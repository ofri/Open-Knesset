from datetime import datetime, date
import gzip

WORKING_HOURS_PER_WEEK = 80.0

def parse_presence(filename=None):
    """Parse the presence reports text file. 
       filename is the reports file to parse. defaults to 'presence.txt'
       Will throw an IOError if the file is not found, or can't be read
       Returns a tuple (member_totals, not_enough_data)
       member_totals is a dict with member ids as keys, and a list of (week_timestamp, weekly hours) for this member as values
       not_enough_data is a list of week timestamps in which we didn't have enough data to compute weekly hours
       a timestamp is a tuple (year, iso week number)
    """
    if filename==None:
        filename = 'presence.txt'
    member_totals = dict()
    totals = dict()
    total_time = 0.0
    f = gzip.open(filename,'r')
    workdays = [6,0,1,2,3]
    last_timestamp = None
    todays_timestamp = date.today().isocalendar()[:2]
    reports = []
    not_enough_data = []
    line = f.readline()
    data = line.split(',')
    time = datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
        
    for line in f:
        data = line.split(',')
        last_time = time
        time = datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')    
        time_in_day = time.hour+time.minute/60.0
        current_timestamp = time.isocalendar()[:2]
        if time.weekday() not in workdays or (time_in_day < 6.0) or (time_in_day > 22.0):
            continue
        if current_timestamp == todays_timestamp:
            break
        if current_timestamp != last_timestamp: # when we move to next timestamp (week), parse the last weeks data
            if len(reports) > 100: # only if we have enough reports from this week (~25 hours sampled)
                subtotals = dict()
                subtotal_time = 0
                for m in reports:
                    minutes = min(m[0], 15) # each report is valid for maximum of 15 minutes
                    subtotal_time += minutes
                    for i in m[1]:
                        if i in subtotals:
                            subtotals[i] += minutes
                        else:
                            subtotals[i] = minutes
                for m in subtotals:
                    if m in totals:
                        totals[m] += float(subtotals[m])
                    else:
                        totals[m] = float(subtotals[m])
                total_time += subtotal_time
            else:
                if last_timestamp!=None:
                    not_enough_data.append(last_timestamp)

            # delete the reports list
            reports = []
            
            for m in totals:
                d = last_timestamp
                if m in member_totals:
                    member_totals[m].append((d,round(float(totals[m])/total_time*WORKING_HOURS_PER_WEEK)))
                else:
                    member_totals[m] = [(d,round(float(totals[m])/total_time*WORKING_HOURS_PER_WEEK))]
            totals = {}
            total_time = 0.0
            last_timestamp = time.isocalendar()[:2]

        # for every report in the file, add it to the array as a tuple: (time, [list of member ids])
        reports.append(((time-last_time).seconds/60,[int(x) for x in data[1:] if len(x.strip())>0]))
    return (member_totals, not_enough_data)
