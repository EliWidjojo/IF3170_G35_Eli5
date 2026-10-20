# IF3170_G35_Eli5

## Deskripsi Singkat
Program ini menyelesaikan permasalahan optimasi penempatan dan penataan paket tiga dimensi (3D Container Packing Problem) dengan cara memaksimalkan value dan meminimalkan cost. Optimasi dilakukan menggunakan algoritma local search, yaitu:     
1. Hill Climbing Steepest Ascent
2. Hill Climbing with Sideways Move
3. Stochastic Hill Climbing
4. Random Restart Hill Climbing
5. Simulated Annealing
6. Genetic Algorithm

Output berupa visualisasi tiga dimensi tata letak awal dan akhir state, serta plot grafik.

## Setup
Dependency: matplotlib     
Untuk install matplotlib, gunakan command:
```
pip install matplotlib
```

## Run Program
Melakukan local search
1. Pada folder root, gunakan command:
   ```
   python src/main.py
   ```
2. Pilih jenis algoritma yang ingin digunakan
3. Pilih ingin read atau load file

Regenerate paket
1. Pada folder root, gunakan command:
   ```
   python src/generate_packages.py
   ```
2. Masukkan input berapa jumlah paket yang ingin dibuat

## Pembagian Tugas
| No | Nama | NIM | Tugas |
| :---: | :--- | :---: | :--- |
| 1 | Eliana Natalie Widjojo | 13524116 | Membuat objective dan helper function, membuat algoritma GA, debugging, menulis laporan |
| 2 | Safira Berlianti | 13524128 | Membuat states, algoritma HC, debugging, menulis laporan |
| 3 | Varistha Devi | 13524135 | Membuat main dan display, membuat algoritma SA, debugging, menulis laporan |
