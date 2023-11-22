#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import open3d as o3d
from matplotlib.animation import PillowWriter

def echo_useage():
    print("-----------------------------------------------")
    print('ReadME: ')
    print("python3 traj_anime_with_pcd.py <option> <play_rate> <traj_csv> (<PCDs>)")
    print("max play_rate is 100")
    print("<option> = show : plot_show")
    print("<option> = save : plot_save as gif")
    print("<PCDs> recommend filtered for resolution 5m")
    print("-----------------------------------------------")


def my_removesuffix(s, suffix):
    return s[:-len(suffix)] if s.endswith(suffix) else s


def get_filename(dir):
    suffix = '.csv'
    num_dir = dir.rfind('/') + 1
    file_name = dir[num_dir:]
    file_name = my_removesuffix(file_name, suffix)
    print("file_name: "+file_name)
    return file_name


def is_integer_num(n):
    if isinstance(n, int):
        return True
    if isinstance(n, float):
        return n.is_integer()
    return False

    
def load_pcd(pcd_files=False, voxel_size=0.1):
    if pcd_files:
        print('---------------')
        print('pcd_loading...')
        combined_pcd = o3d.geometry.PointCloud()  # 結合するための空のPointCloudを初期化
        for pcd_file in pcd_files:
            pcd = o3d.io.read_point_cloud(pcd_file)
            combined_pcd += pcd  # PointCloudの結合
        print('input_voxel_size: ' + str(voxel_size) + '[m]')
        if(voxel_size > 0):
            if(voxel_size < 0.1):
                voxel_size = 0.1
            print('voxel_size: ' + str(voxel_size) + '[m]')
            print('apply voxel grid filter...')
            combined_pcd_filtered = combined_pcd.voxel_down_sample(voxel_size)
        else:
            combined_pcd_filtered = combined_pcd
        points = np.asarray(combined_pcd_filtered.points)
        pc_data = pd.DataFrame({'x': points[:, 0], 'y': points[:, 1]})
        print('---------------')
    else:
        pc_data = []
    return pc_data


def pose_to_df(input):
    df = pd.read_csv(input)
    df = df[["time",
             "pose_x",
             "pose_y",
             "pose_z",
             "pose_roll",
             "pose_pitch",
             "pose_yaw"
             ]]
    df = df.rename(columns={'time': 'TimeStamp',
                            'pose_x': 'x',
                            'pose_y': 'y',
                            'pose_z': 'z',
                            'pose_roll': 'roll',
                            'pose_pitch': 'pitch',
                            'pose_yaw': 'yaw'
                            })
    return df


def calc_vel(df, frame):
    if(frame > 0):
        pre_time = df['TimeStamp'][frame-1]
        pre_x = df['x'][frame-1]
        pre_y = df['y'][frame-1]
        current_time = df['TimeStamp'][frame]
        current_x = df['x'][frame]
        current_y = df['y'][frame]
        diff_time = current_time - pre_time
        diff_x = current_x - pre_x
        diff_y = current_y - pre_y
        diff_2d = math.sqrt(pow(diff_x, 2) + pow(diff_y, 2))
        velocity = diff_2d / diff_time
        velocity = 3.6 * velocity
    else:
        velocity = 0
    return velocity

def zoomed_plot(ax, x, y, zoom_size, df, zoomed_pc, frame):

    xlim_zoom = [df['x'][frame] - zoom_size, df['x'][frame] + zoom_size]
    ylim_zoom = [df['y'][frame] - zoom_size, df['y'][frame] + zoom_size]

    # 折れ線グラフを再描画する
    zoomed_pc = zoomed_pc[(zoomed_pc['x'] >= xlim_zoom[0]) & (zoomed_pc['x'] <= xlim_zoom[1]) & (zoomed_pc['y'] >= ylim_zoom[0]) & (zoomed_pc['y'] <= ylim_zoom[1])]
    if len(zoomed_pc) != 0:
        ax.scatter(zoomed_pc["x"], zoomed_pc["y"],
                    color='k', marker='o', s=0.01, alpha=0.5)
    ax.scatter(x, y, color='blue', s=1, label="trajectory")
    ax.scatter(df['x'][frame], df['y'][frame],
                color='red', s=20, marker='x', label="curent_point")
    ax.quiver(df['x'][frame], df['y'][frame], np.cos(df['yaw'][frame]), np.sin(df['yaw'][frame]), color='black', scale=50, headwidth=4)

    ax.set_title("Zoomed plot (" + str(zoom_size*2) + "[m] x " + str(zoom_size*2) + "[m])")
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_ylim(ylim_zoom[0], ylim_zoom[1])
    ax.set_xlim(xlim_zoom[0], xlim_zoom[1])
    ax.grid()
    ax.set_aspect('equal')
    ax.legend(loc='upper right')


def _update(frame, axs, x, y, df, file_name, xlim, ylim, zoom_size, pc, zoomed_pc):
    """グラフを更新するための関数"""
    
    ax_traj = axs[0]
    if(len(axs)==2):
        ax_zoom = axs[1]
        ax_zoom.cla()

    # 現在のグラフを消去する
    ax_traj.cla()
    # データを更新 (追加) する
    x.append(df['x'][frame])
    y.append(df['y'][frame])

    # 折れ線グラフを再描画する
    if len(pc) != 0:
        ax_traj.scatter(pc["x"], pc["y"],
                    color='k', marker='o', s=0.01, alpha=0.5)
    ax_traj.scatter(x, y, color='blue', s=1, label="trajectory")
    ax_traj.scatter(df['x'][frame], df['y'][frame],
                color='red', s=20, marker='x', label="curent_point")
    ax_traj.quiver(df['x'][frame], df['y'][frame], np.cos(df['yaw'][frame]), np.sin(df['yaw'][frame]), color='black', scale=50, headwidth=4)
    
    ax_traj.set_title("traj:" + file_name + "  plot")
    ax_traj.set_xlabel('x [m]')
    ax_traj.set_ylabel('y [m]')
    ax_traj.set_ylim(ylim[0], ylim[1])
    ax_traj.set_xlim(xlim[0], xlim[1])
    ax_traj.grid()
    ax_traj.set_aspect('equal')
    ax_traj.legend(loc='upper right')

    current_time = df['TimeStamp'][frame]
    current_time_local = current_time - df['TimeStamp'][0]
    # ax_traj.text(xlim[1], ylim[1], str(format(current_time, '.2f')) + " sec")
    ax_traj.text(xlim[1], ylim[1] + 0.1 * (ylim[1] - ylim[0]), str(format(current_time, '.2f')) + " [sec]", ha="right", va="top")
    velocity = calc_vel(df, frame)
    # ax_traj.text(xlim[1], ylim[0], " velocity: " + str(format(velocity, '.2f')) + " [km/h]")
    ax_traj.text(xlim[1], ylim[1] + 0.05 * (ylim[1] - ylim[0]), " velocity: " + str(format(velocity, '.2f')) + " [km/h]", ha="right", va="top")
    # ax_traj.tight_layout()

    if(len(axs)==2):
        zoomed_plot(ax_zoom, x, y, zoom_size, df, zoomed_pc, frame)

    print("\r", str(frame) + " / " + str(df['x'].size), end="")


def main():
    argv = sys.argv
    argc = len(argv)

    if (argc < 4):
        echo_useage()
        return()

    opt = argv[1]
    play_rate = float(argv[2])
    file_path = argv[3]
    # output_path = argv[4]
    pcd_files = []

    for i in range(4, argc):
        pcd_files.append(argv[i])

    df_traj = pose_to_df(file_path)

    long_scale = df_traj['x'].max() - df_traj['x'].min()
    if(long_scale < df_traj['y'].max() - df_traj['y'].min()):
        long_scale = df_traj['y'].max() - df_traj['y'].min()

    margin = long_scale * 0.1

    xlim = [df_traj['x'].min() - margin, df_traj['x'].max() + margin]
    ylim = [df_traj['y'].min() - margin, df_traj['y'].max() + margin]

    leaf_size = long_scale * 0.003
    pc = load_pcd(pcd_files, leaf_size)

    # -------------------------------------config paramater----------------------------------------------------------
    step_time = 10
    zoom_size = 60
    zoom_flag = True
    print('step_time: ' + str(step_time))
    print("Zoom size: (" + str(zoom_size*2) + "[m] x " + str(zoom_size*2) + "[m])")
    # ---------------------------------------------------------------------------------------------------------------

    file_name1 = get_filename(file_path)

    zoom_scale = zoom_size*2
    leaf_size = zoom_scale * 0.003
    zoomed_pc = load_pcd(pcd_files, leaf_size)

    # 描画領域
    fig = plt.figure(figsize=(16, 9), dpi=120)
    if(zoom_flag & (len(zoomed_pc) != 0)):
        ax_traj = fig.add_subplot(1, 2, 1)
        ax_ellip = fig.add_subplot(1, 2, 2)
        axs = [ax_traj, ax_ellip]
    else:
        ax_traj = fig.add_subplot(111)
        axs = [ax_traj]
    # 描画するデータ (最初は空っぽ)
    x = []
    y = []

    # pointcloud = {pc, zoomed_pc}

    params = {
        'fig': fig,
        'func': _update,  # グラフを更新する関数
        # 関数の引数 (フレーム番号を除く)
        'fargs': (axs, x, y, df_traj, file_name1, xlim, ylim, zoom_size, pc, zoomed_pc),
        'interval': 100 / play_rate,  # 更新間隔 (ミリ秒)
        # フレーム番号を生成するイテレータ
        'frames': np.arange(0, df_traj['x'].size, step_time),
        'repeat': False,  # 繰り返さない
        # 'repeat': True,  # 繰り返す
    }
    anime = animation.FuncAnimation(**params)

    if(opt == "show"):
        plt.show()

    output_dir = os.path.dirname(file_path)

    if(opt == "save"):
        # グラフを保存する
        output_file = output_dir + "/" + file_name1 + "_anime_zoomPCD.mp4"
        # output_file = output_dir + "/" + file_name1 + "_anime_zoomPCD.gif"
        print('saving to ' + output_file + '...')
        frame_rate = play_rate*10
        anime.save(output_file)
        # anime.save(output_file, writer=PillowWriter(fps=frame_rate))

    print('')
    print('fin')


if __name__ == '__main__':
    main()
