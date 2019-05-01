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
times_utc, duchesne = load_5min_ozone_data(st,et,'Duchesne')
mtn_home = load_5min_ozone_data(st,et,'Mountain_Home')[1]
seep_ridge = load_5min_ozone_data(st,et,'Seep_Ridge')[1]
seven_sis = load_5min_ozone_data(st,et,'Seven_Sisters')[1]
sand_wash = load_5min_ozone_data(st,et,'Sand_Wash')[1]

if st[0:4]=='2014':
	horsepool = load_5min_ozone_data(st,et,'Horsepool')[1]
if st[0:4]=='2013':
	gusher = load_5min_ozone_data(st,et,'Gusher')[1]
#----------------------------------------------------

# Make plots:	
fig = plt.figure(figsize=(20,6))
ax = plt.subplot(111)

plt.plot(times_utc,duchesne, label="Duchesne")
plt.plot(times_utc,mtn_home, label="Mountain Home")
plt.plot(times_utc,seep_ridge, label="Seep Ridge")
plt.plot(times_utc,seven_sis, label="Seven Sisters")
plt.plot(times_utc,sand_wash, label="Sand Wash")
if st[0:4]=='2014':
	plt.plot(times_utc,horsepool, label="Horsepool")
if st[0:4]=='2013':
	plt.plot(times_utc,gusher, label="Gusher")

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
plt.xticks(rotation = 30, fontsize = 10)

# Labels
plt.title('5 Minute Ozone Concentrations\n'+sd_with_year)
plt.ylabel('Ozone Concentration (ppb)')
plt.xlabel('Day (UTC)')

plt.tight_layout()

# Save Figure
output_dir = '/uufs/chpc.utah.edu/common/home/u0553130/python_scripts/Summer_Research_2014/figs/ozone/'
figname = 'Ozone_5min_'+sd_with_year+'.png'
fig.savefig(output_dir+figname)

plt.show()



