# STATUS: UNFINISHED

# DESCRIPTION

Modul ini bertanggung jawab untuk:

1. Merender gameplay menggunakan PyGame.
2. Menampilkan labirin, player, agent, vision, timer, dan elemen visual lainnya.
3. Membaca input keyboard dari user.
4. Mengirimkan hasil input keyboard dan status gameplay kembali ke manager.

Modul ini **TIDAK BOLEH** mengandung logika gameplay seperti:

* Pathfinding
* AI agent behavior
* Collision handling
* Timer update
* Win/Lose calculation
* Maze generation
* State transition

Seluruh data gameplay sudah diberikan oleh manager dan hanya perlu divisualisasikan.

Modul ini juga **TIDAK BOLEH** membuat game loop utama **KECUALI** untuk menampilkan layar kemenangan atau kekalahan. 

---

# MAZE FORMAT

Maze berbentuk nested list 2D:

```py
maze[row][col]
```

Setiap cell berisi dictionary:

```py
{
    "up": int,
    "down": int,
    "left": int,
    "right": int,
    "hiding": int
}
```

Nilai:

```py
0 = False
1 = True
```

Contoh:

```py
{
    "up": 1,
    "down": 0,
    "left": 1,
    "right": 0,
    "hiding": 0
}
```

---

# COORDINATE SYSTEM

Maze menggunakan koordinat:

```py
(row, col)
```

Dengan aturan:

* row kecil = posisi lebih atas
* row besar = posisi lebih bawah
* col kecil = posisi lebih kiri
* col besar = posisi lebih kanan

Konversi ke layar:

```py
screen_x = col
screen_y = row
```

---

# WALL RENDERING

Maze tidak selalu simetris.

Contoh:

```py
maze[0][0]["right"] = 1
maze[0][1]["left"] = 0
```

Apabila salah satu cell menyatakan terdapat dinding, maka dinding tetap harus dirender.

Dengan kata lain:

```py
render_wall =
(
    current_cell_has_wall
    OR
    neighbor_cell_has_wall
)
```

---

# HIDING CELL

Cell dengan:

```py
"hiding" == 1
```

merupakan hiding spot.

Visualisasikan hiding spot sebagai pintu.

Pintu harus:

* Terbuka apabila player berada tepat di luar pintu.
* Tertutup apabila player berada di dalam hiding spot.
* Tertutup apabila player tidak berada di dekat pintu.

Pilih sisi yang tidak memiliki dinding sebagai posisi pintu.

---

# ENTITY RENDERING

Player dan agent dirender sebagai lingkaran.

Warna mengikuti input:

```py
player_color
agent_color
```

---

# VISION RENDERING

Vision dirender dengan menerangkan kecerahan pada cell yang tampak.

Aturan:

* Overlay harus semi-transparan sehingga maze tetap terlihat.


---

# MOVEMENT INTERPOLATION

Player dan agent tidak boleh berpindah secara teleport.

Gunakan interpolasi posisi visual dari:

```py
previous_position
```

menuju:

```py
current_position
```

berdasarkan speed masing-masing entity.

Tujuan:

* Pergerakan terlihat halus.
* Tidak terjadi teleport antar cell.

---

# SPEED

Input:

```py
player_speed
agent_speed
```

Digunakan untuk menyatakan berapa banyak cell entitas tersebut berjalan setiap tick.

Apabila speed kurang dari 1 cell/tick, maka entitas berhenti pada sebuah lokasi di antara cell awal dan cell tujuan.

Contoh, ketika speed = 0.5 cell/tick, maka pada tick pertama, entitas berada di tengah-tengah kedua cell.

Karena entitas masih berada di tengah-tengah cell, tick selanjutnya menyelesaikan pergerakan entitas dengan move = "none" dan "pressed_toggle_movement" False.

Diperlukan sebuah flag untuk memberitahu tick selanjutnya apakah entitas masih berjalan atau tidak.

---

# WIN / LOSE DISPLAY

Manager akan mengirim status.

Apabila status menunjukkan player menang:

* Tampilkan layar kemenangan.

Apabila status menunjukkan player kalah:

* Tampilkan layar kekalahan.

Modul tidak menghitung kondisi menang atau kalah.

HANYA BUAT LOCAL LOOP DI SINI!

Tambahkan opsi "Back" untuk kembali ke main menu.


---

# INPUT

## Module Input

```py
game_dict = {
    "maze": list[list[dict[str, int]]],
    "timer": int,

    "player_pos": tuple[int, int],
    "player_speed": float,
    "player_vision": list[tuple[int, int]],
    "player_color": tuple[int, int, int],

    "agent_pos": tuple[int, int],
    "agent_speed": float,
    "agent_vision": list[tuple[int, int]],
    "agent_color": tuple[int, int, int]
}
```

---

## Keyboard Input

Gunakan PyGame.

Pergerakan:

```text
W / Up Arrow     -> up
S / Down Arrow   -> down
A / Left Arrow   -> left
D / Right Arrow  -> right
```

Toggle movement:

```text
C
```

---

# OUTPUT

```py
player_update = {
    "move": Literal[
        "up",
        "down",
        "left",
        "right",
        "none"
    ],
    "pressed_movement_toggle": bool,
    "state": int,
    "player_moving": bool,
    "agent_moving": bool,
}
```

Keterangan:

```py
3 -> gameplay berjalan
0 -> kembali ke main menu

player_moving = True -> player masih belum sampai ke cell tujuan (karena memerlukan beberapa tick untuk sampai)

player_moving = False -> player sudah sampai ke cell tujuan

agent_moving = True -> agent masih belum sampai ke cell tujuan (karena memerlukan beberapa tick untuk sampai)

agent_moving = False -> agent sudah sampai ke cell tujuan
```

---

# WORKFLOW

```text
Manager
    |
    v
Mengirim state gameplay
    |
    v
Render gameplay menggunakan PyGame
    |
    v
Baca input keyboard
    |
    v
Buat player_update
    |
    v
Kirim kembali ke Manager
```

---

# IMPLEMENTATION NOTES

Modul ini hanya bertanggung jawab untuk:

1. Rendering.
2. Keyboard input.
3. Mengembalikan player_update.

Segala bentuk logika gameplay sudah ditangani oleh manager dan controller lain.
