# STATUS: UNFINISHED

# DESCRIPTION

Modul ini bertanggung jawab untuk:

1. Merender seluruh visual permainan selama gameplay berlangsung.
2. Menyembunyikan area yang tidak dapat dilihat pemain.
3. Menampilkan minimap berdasarkan area yang telah dieksplorasi pemain.
4. Menampilkan status pergerakan pemain.
5. Menampilkan waktu bertahan hidup yang tersisa.
6. Menampilkan peringatan visual ketika agent mendeteksi pemain.
7. Menampilkan peringatan visual ketika suara pemain terdengar oleh agent.

# WORKFLOW

Manager mengirimkan state permainan terbaru.

↓

Modul Visual Effect menerima data gameplay.

↓

Modul memperbarui seluruh elemen visual.

↓

Visual baru ditampilkan ke layar.

↓

Proses ini diulang setiap frame selama permainan berlangsung.

# INPUT

visual_dict = {
    "player_vision": list[tuple[int, int]],
    "player_known_map": list[list[bool]],
    "agent_see_player": bool,
    "agent_hear_player": bool,
    "remaining_time": int,
    "player_walking": bool,
}

# FIELD OF VIEW SYSTEM

Seluruh elemen permainan hanya boleh dirender apabila berada di dalam area penglihatan pemain.

Termasuk:

- Cell
- Wall
- Hiding Spot
- Agent
- Player

Jika suatu cell tidak berada di dalam:

`player_vision`

maka cell tersebut tidak boleh dirender.

Jika suatu wall berada pada cell yang tidak terlihat, wall tersebut juga tidak boleh dirender.

Dengan kata lain:

```
Visible Cell
→ Render

Invisible Cell
→ Do Not Render
```

# MINIMAP

Minimap selalu ditampilkan selama permainan berlangsung.

Awalnya seluruh minimap tertutup kabut (fog).

Cell hanya dibuka apabila pemain pernah melihat cell tersebut sebelumnya.

Data yang digunakan:

`known_map`

Aturan:

```
Known Cell
→ Tampilkan pada minimap

Unknown Cell
→ Tampilkan sebagai fog
```

# MOVEMENT INDICATOR

Indikator status pergerakan pemain selalu ditampilkan.

Kemungkinan nilai:

```Walking atau Sneaking```

Sumber data:

`player_walking`

Contoh tampilan:

```
Movement: Walking

atau

Movement: Sneaking
```

# SURVIVAL TIMER

Waktu bertahan hidup selalu ditampilkan.

Sumber data:

`remaining_time`

Contoh tampilan:

```Time Remaining: 87```

# AGENT VISUAL WARNING

Ketika agent melihat pemain:

`agent_see_player == True`

maka tampilkan subtitle:

"You feel like someone is watching you."

Subtitle ditampilkan selama lima detik.

# AGENT AUDIO WARNING

Ketika suara pemain terdengar oleh agent:

`agent_hear_player == True`

maka tampilkan subtitle:

"You feel like your footsteps are too loud."

Subtitle ditampilkan selama lima detik.

# RENDER PRIORITY

Prioritas render dari tertinggi ke terendah:

1. Warning Subtitle
2. Survival Timer
3. Movement Indicator
4. Gameplay Objects
5. Maze Walls
6. Maze Cells
7. Minimap

# NOTES

- Modul ini tidak mengubah state permainan.
- Modul ini hanya bertanggung jawab terhadap visualisasi.
- Modul ini tidak melakukan perhitungan AI.
- Modul ini tidak melakukan pathfinding.
- Modul ini tidak melakukan collision checking.
- Seluruh data gameplay berasal dari manager.
- Modul ini harus dapat diperbarui setiap frame tanpa mengubah data asli yang diterima.
