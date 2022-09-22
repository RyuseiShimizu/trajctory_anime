#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import argparse


def my_removesuffix(s, suffix):
    return s[:-len(suffix)] if s.endswith(suffix) else s


def get_filename(dir):
    suffix = '.csv'
    num_dir = dir.rfind('/') + 1
    file_name = dir[num_dir:]
    file_name = my_removesuffix(file_name, suffix)
    print("file_name: "+file_name)
    return file_name


def pose_to_df(input):
    df = pd.read_csv(input)
    df = df[["pose.x",
             "pose.y",
             "pose.z",
             ]]
    df = df.rename(columns={'pose.x': 'x',
                            'pose.y': 'y',
                            'pose.z': 'z',
                            })
    return df


def _update(frame, x, y, df, file_name, xlim, ylim):
    """グラフを更新するための関数"""
    # 現在のグラフを消去する
    plt.cla()
    # データを更新 (追加) する
    x.append(df['x'][frame])
    y.append(df['y'][frame])
    # x.append(frame)
    # y.append(math.sin(frame))
    print("\r", str(frame) + " / " + str(df['x'].size), end="")
    # 折れ線グラフを再描画する
    plt.scatter(x, y, color='blue', s=1, label="trajectory")
    plt.scatter(df['x'][frame], df['y'][frame],
                color='red', s=20, marker='x', label="curent_point")
    plt.title("traj:" + file_name + "  plot")
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.ylim(ylim[0], ylim[1])
    plt.xlim(xlim[0], xlim[1])
    plt.grid()
    plt.axes().set_aspect('equal')
    plt.legend(loc='upper right')
    plt.tight_layout()


def main():
    print('ReadME: ')
    print("python3 trajectory_animation.py <option> <play_rate> <traj_csv> <out_dir>")
    print("max play_rate is 100")
    print("<option> = show : plot_show")
    print("<option> = save : plot_save as gif")
    print("-----------------------------------------------")

    parser = argparse.ArgumentParser()
    parser.add_argument("input_1")
    parser.add_argument("input_2")
    parser.add_argument("input_3")
    parser.add_argument("input_4")
    args = parser.parse_args()

    opt = args.input_1
    play_rate = float(args.input_2)
    file_path = args.input_3
    output_path = args.input_4

    df_traj = pose_to_df(file_path)

    print('test: ')
    print(df_traj['x'][0])
    print('size: ')
    print(df_traj['x'].size)

    # -------------------------------------config paramater----------------------------------------------------------
    step_size = 10
    # ---------------------------------------------------------------------------------------------------------------

    long_scale = df_traj['x'].max() - df_traj['x'].min()
    if(long_scale < df_traj['y'].max() - df_traj['y'].min()):
        long_scale = df_traj['y'].max() - df_traj['y'].min()

    margin = long_scale * 0.1

    xlim = [df_traj['x'].min() - margin, df_traj['x'].max() + margin]
    ylim = [df_traj['y'].min() - margin, df_traj['y'].max() + margin]

    file_name1 = get_filename(file_path)

    # 描画領域
    fig = plt.figure(figsize=(10, 6))
    # 描画するデータ (最初は空っぽ)
    x = []
    y = []

    params = {
        'fig': fig,
        'func': _update,  # グラフを更新する関数
        'fargs': (x, y, df_traj, file_name1, xlim, ylim),  # 関数の引数 (フレーム番号を除く)
        'interval': 100 / play_rate,  # 更新間隔 (ミリ秒)
        # フレーム番号を生成するイテレータ
        'frames': np.arange(0, df_traj['x'].size, step_size),
        'repeat': False,  # 繰り返さない
        # 'repeat': True,  # 繰り返す
    }
    anime = animation.FuncAnimation(**params)

    if(opt == "show"):
        plt.show()

    if(opt == "save"):
        # グラフを保存する
        output_file = output_path + "/" + file_name1 + "_anime.gif"
        print('saving to ' + output_file + '...')
        anime.save(output_file, writer='pillow')

    print('')
    print('fin')


if __name__ == '__main__':
    main()
