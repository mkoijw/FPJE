clear
close
% 生成200m高度磁图 经度116-117 纬度14-15
%% 生成网格坐标
grid_num = 1000;% 精度0.001°
MagMap_h = 0.2;% 磁图高度0.2km
MagMap_pos = zeros(grid_num^2,2);
for i = 1:grid_num
    for j = 1:grid_num
        MagMap_pos((i-1)*grid_num + j,:) = [116+i*(1/grid_num), 14+j*(1/grid_num)];
    end
end
MagMap_pos = [MagMap_pos,ones(grid_num^2,1)*MagMap_h];
%% 调用wmm emm生成磁图
MagMap_emmB = pos2emmMag(MagMap_pos);
MagMap_wmmB = pos2wmmMag(MagMap_pos);

MagMap_detaB = MagMap_emmB - MagMap_wmmB;
MagMap = [MagMap_pos,MagMap_detaB];
save("MagMap.mat","MagMap");
%% 随机生成初始磁偶极子
num_points = 5000;
lim_range = [116-1,117+1;
             14-1,15+1;
             -10,-100-50];

% 经度范围：116°到117°
longitude = lim_range(1,1) + (rand(num_points, 1) * (lim_range(1,2) - lim_range(1,1)));

% 纬度范围：14°到15°
latitude = lim_range(2,1) + (rand(num_points, 1) * (lim_range(2,2) - lim_range(2,1)));

% 高度范围：-10km到-100km
height = lim_range(3,1) + (rand(num_points, 1) * (lim_range(3,2) - (lim_range(3,1))));

% 将经度、纬度和高度合并成一个矩阵
coordinates = [longitude, latitude, height];
coordinates_ecef = lla2ecef([coordinates(:,2),coordinates(:,1),coordinates(:,3).*1000]);

writematrix(coordinates_ecef, 'Initial_dipole_position.csv');