# trajectory_animation
Updated (2022/09/22)

View and save vehicle trajectory

```
$ git clone <link>
$ cd trajectory_animation/
```
## Usage
---

### plot trajectory animation
Displays trajectory on point cloud
```
$ python3 scripts/trajectory_checker.py <option> <play_rate> <traj_csv>　(<PCDs>)
```

* option: "show" or "save"
* play_rate: Playback speed (max: 100, recomend: 1)
* traj_csv: Trajectory csv including time series xyz coordinate values and attitude angles (roll, pitch, yaw)
* out_dir: output directory
* PCDs: 1 or more pcd

e.g.
sample_data

![sample_data](sample_data/trajectory2_anime_zoomPCD.gif)

---

## legacy
---

### plot only trajectory
```
$ python3 scripts/trajectory_animation.py <option> <play_rate> <traj_csv> <out_dir>
```

* option: "show" or "save"
* play_rate: Playback speed (max: 100, recomend: 1)
* traj_csv: trajectory csv including xyz coordinate values in chronological order
* out_dir: output directory

---

### plot trajectory with PCD
Displays trajectory on point cloud
```
$ python3 scripts/traj_anime_with_pcd.py <option> <play_rate> <traj_csv>　(<PCDs>)
```

* option: "show" or "save"
* play_rate: Playback speed (max: 100, recomend: 1)
* traj_csv: trajectory csv including xyz coordinate values in chronological order
* out_dir: output directory
* PCDs: 1 or more pcd (recommended to use pcd filtered by voxel_glid_filter.)

---

軌跡csvのx，y，z座標のヘッダ名は，pythonコード内のpose_to_dfに合わせてください．

csvの方を変えてもpythonスクリプトの方を変えても良いです．

play_rateを100にしても遅いと感じる場合は，pythonスクリプト内のstep_sizeを大きくしてください．
