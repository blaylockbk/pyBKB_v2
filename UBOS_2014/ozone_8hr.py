## Gets 5 minute ozone data from UBOS 2013 and 2014 studies

from ozone_functions import *

## Inputs collected from program call
st = sys.argv[1]          		# YYYYMMDDHH: 2014050618
et = sys.argv[2]           		# YYYYMMDDHH: 2014050818

# String Date Range Formats
start = datetime.strptime(st,"%Y%m%d%H")
end = datetime.strptime(et,"%Y%m%d%H")
sd = start.strftime(("%b%d%H")+"-"+end.strftime("%b%d%H"))
sd_with_year = start.strftime(("%b %d, %Y")+' - '+end.strftime("%b %d, %Y"))

## Load data: Specify the station
times_utc, duchesne = load_8hr_ozone_data(st,et,'Duchesne')
lapoint = load_8hr_ozone_data(st,et,'Lapoint')[1]
seven_sis = load_8hr_ozone_data(st,et,'Seven_Sisters')[1]
vernal = load_8hr_ozone_data(st,et,'Vernal')[1]
ouray = load_8hr_ozone_data(st,et,'Ouray')[1]
roos = load_8hr_ozone_data(st,et,'Roosevelt')[1]
horse = load_8hr_ozone_data(st,et,'Horsepool')[1]

#----------------------------------------------------

# Make plots:	
fig = plt.figure(figsize=(20,8))
ax = plt.subplot(111)

plt.plot(times_utc,duchesne, label="Duchesne")
plt.plot(times_utc,lapoint, label="Lapoint")
plt.plot(times_utc,seven_sis, label="Seven Sisters")
plt.plot(times_utc,vernal, label="Vernal")
plt.plot(times_utc,ouray, label="Ouray")
plt.plot(times_utc,roos, label="Roosevelt")
plt.plot(times_utc,horse, label="Horsepool")

## Plot EPA's 75 ppb standard
plt.axhline(75, c='r', linestyle='--')

plt.legend(loc=2)

# Format Date Ticks
months = MonthLocator()
days = DayLocator(interval=2)
days_each = DayLocator()
hours = HourLocator(byhour=[0,12])
hours_each = HourLocator()
dateFmt = DateFormatter('%b %d')
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(dateFmt)
ax.xaxis.set_minor_locator(days_each)
plt.xticks(rotation = 30, fontsize = 14)
plt.yticks(fontsize=14)
plt.ylim([0,160])

ax.tick_params('both', length=8, width=1.2, which='major')
ax.tick_params('both', length=4, width=1, which='minor')

# Labels
plt.title('8 Hour Average Ozone Concentrations\n'+sd_with_year, fontsize=21)
plt.ylabel('Ozone Concentration (ppb)', fontsize=16)
plt.xlabel('Day (UTC)',fontsize=16)

plt.tight_layout()

# Save Figure
output_dir = '/uufs/chpc.utah.edu/common/home/u0553130/python_scripts/Summer_Research_2014/figs/ozone/'
figname = 'Ozone_8hr_'+sd_with_year+'.png'
fig.savefig(output_dir+figname)

plt.show()