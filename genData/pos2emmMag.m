function mag = pos2emmMag(pos)
    infilePath = 'E:\EPofGM\Global_geomagnetic_model\EMM2017_Windows\input.txt';
    outfilePath = 'E:\EPofGM\Global_geomagnetic_model\EMM2017_Windows\output.txt';
    %% 将位置转为EMM_file.exe输入格式
    fileID = fopen(infilePath, 'w');
    date = '2017';
    altitude_type = 'M';% 'M'——海平面高度，'E'——WGS84高度
    for i = 1:size(pos, 1)
        altitude = pos(i, 3);
        latitude = pos(i, 2);
        longitude = pos(i, 1);
        % 生成字符串并写入文件
        fprintf(fileID, '%s %s K%f %f %f\n', date, altitude_type, altitude, latitude, longitude);
    end
    fclose(fileID);
    %% 运行EMM_file.exe
    % 更改当前目录
    cd('E:\EPofGM\Global_geomagnetic_model\EMM2017_Windows');
    
    % 执行命令
    [status, cmdout] = system('emm_file f input.txt output.txt');
    
    % 检查命令是否成功执行
    if status == 0
        disp('命令成功执行');
        disp(cmdout); % 显示命令输出
    else
        disp('命令执行失败');
        disp(cmdout); % 显示错误信息
    end
    cd('E:\AnalyticContinuation\magUpConti');
    mag = readtable(outfilePath, 'VariableNamingRule', 'preserve');
    mag = mag(:,11:13);
    mag = table2array(mag);
end