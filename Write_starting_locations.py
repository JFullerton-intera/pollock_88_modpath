import pandas as pd
import os
import numpy as np

def PointsInCircum(x,y, r,n=8):
    a = [[np.cos(2*np.pi/n*i)*r,np.sin(2*np.pi/n*i)*r] for i in range(0,n+1)]
    x0 = np.array([i[0] for i in a])
    y0 = np.array([i[1] for i in a])
    return x0+x, y0+y

def find_row_col(dis,globx,globy):
    nrow,ncol,delr,delc = dis.nrow,dis.ncol,dis.delr.array,dis.delc.array
    Lx,Ly = delc.sum(), delr.sum()

    rows, cols = [], []
    locxs, locys = [], []
    for i in range(len(globx)):
        gx,gy = globx[i], globy[i]
        row = np.searchsorted(delr.cumsum(),gy,side='right')

        col = np.searchsorted(delc.cumsum(),gx,side='left')

        Lx_temp = delc[:col].sum()
        Ly_temp = delr[:row].sum()

        locx = (gx-Lx_temp)/delc[0]
        locy = 1+((Ly_temp-gy))/delr[0]

        # print(gx,row)
        # print(gy, col)
        # print(Lx_temp,Ly_temp)
        # print(locx,locy)
        # exit()
        rows.append(row)
        cols.append(col)
        locxs.append(locx)
        locys.append(locy)
    return rows,cols,locxs,locys

def create_pt_df(dis,strt_time,n=8):
    locx, locy = [], []
    pg,gp_num = [], []
    locr, locc = [], []
    loclay = []
    gp_n = 1
    rt = []

    nrow,ncol,delr,delc = dis.nrow,dis.ncol,dis.delr.array,dis.delc.array
    Lx,Ly = delc.sum(), delr.sum()
    # for something in rows # old way
    # x, y = PointsInCircum(.5, .5, .5, n)

    globx, globy = PointsInCircum(Lx/2,Ly/2,150,n)

    rows, cols, locxs, locys = find_row_col(dis,globx,globy)


    # print(x,y)
    # exit()
    # for i in range(len(rows)):
    for j in range(n):
        locx.append(locxs[j])
        locy.append(locys[j])
        pg.append(f'GP{gp_n+1:02}')
        locr.append(rows[j]+1)
        locc.append(cols[j]+1)
        loclay.append(1)
        gp_num.append(gp_n)

        rt.append(strt_time[0])
    gp_n += 1
    #ParticleID, GroupNumber, Grid, Layer, Row, Column, LocalX, LocalY, LocalZ, ReleaseTime, Label
    data = {'ParticleID':np.arange(1,len(pg)+1),'GroupNumber':gp_num,'Grid':np.ones(len(locr)).astype(int),'Layer':loclay,
            'Row':locr,'Column':locc,'LocalX':locx,'LocalY':locy,'LocalZ':.5*np.ones(len(locx)),
            'ReleaseTime':rt,'Label':pg}
    # for key in data.keys():
        # print(key, len(data[key]))

    df = pd.DataFrame(data)
    df['Row'] = df['Row'].astype(int)
    df['Column'] = df['Column'].astype(int)
    df['LocalX'] = round(df['LocalX'],4)
    df['LocalY'] = round(df['LocalY'],4)

    df = df[['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']]

    return df



def write_file(file_nam,dis,strt_time,n,input_style=1):
    df = create_pt_df(dis,strt_time,n)
    columns = ['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']
    grps = df['GroupNumber'].unique().tolist()
    # print(grps)

    file = open(file_nam,'w')
    file.write(f'1\n{len(grps)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        file.write(grp_nam+'\n')
        file.write(f'{len(tempDF)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        for z in range(len(tempDF)):
            for j in columns:
                file.write(f'{tempDF.iloc[z][j]}  ')
            file.write('\n')