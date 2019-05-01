clear all;
close all;
%kind of weird. look at info variable
%if first letter a capital then  variable
%lower case first letter are mre like attributes
% create ncgeodataset object
blank = '  ';
gr = ncgeodataset('/uufs/chpc.utah.edu/common/home/horel-group/archive/20150618/models/hrrr.t12z.wrfsfcf00.grib2');
info = gr.metadata;
vars=gr.variables;
attr=gr.attributes;
%to get all geopotential heights
ht_gr=gr.geovariable('Geopotential_height_isobaric');
coord_ht_gr= ht_gr.grid_interop(1,:,:,:);
%only spd one is 10 m
spd_gr=gr.geovariable('Wind_speed_height_above_ground_0_Hour_Maximum');
coord_spd_gr= spd_gr.grid_interop(1,1,:,:);
spd_g(:,:)=spd_gr.data(1,1,:,:);
spd_g=double(spd_g)';
%only  one is 10 m
u_gr=gr.geovariable('u-component_of_wind_height_above_ground');
coord_u_gr= u_gr.grid_interop(1,1,:,:);
u_g(:,:)=u_gr.data(1,1,:,:);
u_g=double(u_g)';
%only  one is 10 m
v_gr=gr.geovariable('v-component_of_wind_height_above_ground');
coord_v_gr= v_gr.grid_interop(1,1,:,:);
v_g(:,:)=v_gr.data(1,1,:,:);
v_g=double(v_g)';
%only temp one is 2 m
tmp_gr=gr.geovariable('Temperature_height_above_ground');
coord_tmp_gr= tmp_gr.grid_interop(1,1,:,:);
tmp_g(:,:)=tmp_gr.data(1,1,:,:);
tmp_g=double(tmp_g)'-273.15;

% create geovariable object
elv_gr = gr.geovariable('Geopotential_height_surface');
elv_g(:,:)=elv_gr.data(1,:,:);
coord = elv_gr.grid_interop(1,:,:);
elv_g= double(elv_g)';
elv_att = elv_gr.attributes;

lat_gr = double(coord.lat)';
lon_gr = double(coord.lon)';
daten = coord.time;
datev = datevec(daten);
dates = datestr(datev,0);

minlat=39.2;
maxlat=41;
maxlon=-108.4;
minlon=-111.4;
latlim=[minlat maxlat];
lonlim=[minlon maxlon];
bbox = [minlon minlat;maxlon maxlat];
%the state info is built into the mapping tool box
states = shaperead('usastatehi',...
        'UseGeoCoords', true, 'BoundingBox',bbox);

% plot base map using surfm
figure(1)
cmap = colormap(bone);
% use projection info supplied by matlab
ax=usamap(latlim, lonlim);
% handle labels
setm(ax,'MlabelLocation',1,'PlabelLocation',1,'MLineLocation',1,'PLineLocation',1);
surfm(lat_gr,lon_gr,elv_g)
%colorbar
hold on
%geoshow(ax, states, 'FaceColor', 'none')
t = strcat(dates,' HRRR Elevation ');
%title(t,'FontSize',10);
saveas(gcf,'hrrr_elv','png');
figure(2)
cmap = colormap(jet);
% use projection info supplied by matlab
ax=usamap(latlim, lonlim);
% handle labels
setm(ax,'MlabelLocation',1,'PlabelLocation',1,'MLineLocation',1,'PLineLocation',1);
surfm(lat_gr,lon_gr,spd_g)
colorbar
hold on
%geoshow(ax, states, 'FaceColor', 'none')
t = strcat('HRRR Wind Speed ',dates);
title(t,'FontSize',10);
saveas(gcf,'hrrr_spd','png');
figure(3)
cmap = colormap(jet);
% use projection info supplied by matlab
ax=usamap(latlim, lonlim);
% handle labels
setm(ax,'MlabelLocation',1,'PlabelLocation',1,'MLineLocation',1,'PLineLocation',1);
surfm(lat_gr,lon_gr,tmp_g)
hold on
%geoshow(ax, states, 'FaceColor', 'none')
t = strcat('HRRR Temp ',dates);
title(t,'FontSize',10);
colorbar
saveas(gcf,'hrrr_tmp','png');
figure(4)
fh = figure(4);    
set(fh,'PaperPositionMode','manual',...
'PaperPosition',[0 0 10 7.5],'PaperSize',[10 7.5],...
'PaperUnits','inches','color','white');
% use projection info supplied by matlab
ax=usamap(latlim, lonlim);
% handle labels
setm(ax,'MlabelLocation',1,'PlabelLocation',1,'MLineLocation',1,'PLineLocation',1);
contourm(lat_gr,lon_gr,elv_g,'LevelStep',500,'LineColor','k');
hold on
%cmap = colormap(jet);
%quivermc(lat_gr,lon_gr,u_g,v_g,'density',25,'reference',5,'unit','m/s',...
%    'colormap',jet,'colorbar','southoutside')
quivermc(lat_gr,lon_gr,u_g,v_g,'density',66.6,'reference',10,'unit','m/s')
hold on
%geoshow(ax, states, 'FaceColor', 'none')
t = strcat({'HRRR 10 m Wind: '},dates);
title(t,'FontSize',10);
saveas(gcf,'hrrr_wind','png');
