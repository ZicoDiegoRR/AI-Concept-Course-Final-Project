# STATUS: FINISHED ✅

# DESCRIPTION

Modul ini bertanggung jawab untuk:

1. Merender menu pengaturan permainan sebelum permainan dimulai.
2. Menampilkan beberapa opsi untuk kostumisasi permainan.
3. Menampilkan aturan permainan kepada pemain.
4. Mengumpulkan konfigurasi permainan yang dipilih pemain.
5. Mengembalikan hasil konfigurasi ke manager untuk digunakan pada proses inisialisasi permainan.

# WORKFLOW

Manager memanggil modul Play Menu.

↓

Play Menu membuat local looping sendiri sehingga UI terkunci pada menu ini.

↓

Aturan permainan ditampilkan kepada pemain.

↓

Pemain mengubah parameter permainan melalui komponen UI yang tersedia.

↓

Pemain memilih salah satu opsi:

- Start Game
- Back

↓

Jika pemain memilih Back:

state_dict = {
    "state": 0,
    "game_dict": None,
    "player_dict": None,
    "agent_dict": None,
}

Output dikirim kembali ke manager dan local looping dihentikan.

↓

Jika pemain memilih Start Game:

Konfigurasi permainan yang dipilih pemain dikonversi menjadi nilai numerik yang dapat digunakan oleh sistem permainan.

state_dict = {
    "state": 3,
    "game_dict": game_dict,
    "player_dict": player_dict,
    "agent_dict": agent_dict,
}

Output dikirim kembali ke manager dan local looping dihentikan.

# CONFIGURABLE VARIABLES

## Maze Size

Variabel yang menerima input numerik secara langsung:

- row_size (nilai minimum 10)
- col_size (nilai minimum 10)

## Agent Forgiveness

Merepresentasikan nilai:

prob_decay

Pilihan:

- Never Forgives
- Holds Grudges
- Moderate
- Quickly Forgets

## Noise Propagation Through Wall

Merepresentasikan nilai:

wall_reduction

Pilihan:

- Completely Blocked
- Strongly Reduced
- Partially Reduced
- Easily Heard

## Hiding Cell Safety

Merepresentasikan nilai:

hiding_cell_reduction

Pilihan:

- Never Get Checked
- Mostly Being Ignored
- Usually Not Considered
- Feeling Suspicious

## Agent's Sensitivity to Noise

Merepresentasikan nilai:

range_raise_prob

Pilihan:

- Low
- Moderate
- High
- Very High

## Player's Vision

Merepresentasikan nilai:

player_vision_range

Pilihan:

- Short
- Normal
- Far
- Very Far

## Agent's Vision

Merepresentasikan nilai:

agent_vision_range

Pilihan:

- Short
- Normal
- Far
- Very Far

## Agent's Memory Capacity

Merepresentasikan nilai:

max_mem

Pilihan:

- Low
- Medium
- High
- Very High

# INPUT CHOICE MAPPING

## Agent Forgiveness

- Never Forgives    : prob_decay = 0.
- Holds Grudges     : prob_decay = 0.1
- Moderate          : prob_decay = 0.25
- Quickly Forgets   : prob_decay = 0.35

## Noise Propagation Through Wall

- Completely Blocked    : wall_reduction = float("inf")
- Strongly Reduced      : wall_reduction = 3
- Partially Reduced     : wall_reduction = 2
- Easily Heard          : wall_reduction = 1

## Hiding Cell Safety

- Never Get Checked     : hiding_cell_reduction = 1.
- Mostly Being Ignored  : hiding_cell_reduction = 0.75
- Usually Not Considered: hiding_cell_reduction = 0.5
- Feeling Suspicious    : hiding_cell_reduction = 0.25

## Agent's Sensitivity to Noise

- Low       : range_raise_prob = 3
- Moderate  : range_raise_prob = 5
- High      : range_raise_prob = 7
- Very High : range_raise_prob = 9

## Player's Vision

- Short     : player_vision_range = 3
- Normal    : player_vision_range = 4
- Far       : player_vision_range = 5
- Very Far  : player_vision_range = 6

## Agent's Vision

- Short     : agent_vision_range = 4
- Normal    : agent_vision_range = 6
- Far       : agent_vision_range = 8
- Very Far  : agent_vision_range = 10

## Agent's Memory Capacity

- Low       : max_mem = 30
- Medium    : max_mem = 50
- High      : max_mem = 70
- Very High : max_mem = 90

# OUTPUT FORMAT

state_dict = {
    "state": int,
    "game_dict": {
        "row_size": row_size,
        "col_size": col_size,
        "prob_decay": prob_decay,
        "wall_reduction": wall_reduction,
        "hiding_cell_reduction": hiding_cell_reduction,
        "range_raise_prob": range_raise_prob,
        "max_mem": max_mem
    },
    "player_dict": {
        "vision_range": player_vision_range,
    }, 
    "agent_dict": {
        "vision_range": agent_vision_range,
    }
}

# NOTES

- Modul ini tidak menerima input konfigurasi dari manager.
- Modul ini selalu menampilkan aturan permainan setiap kali dibuka.
- Modul ini wajib memiliki local looping sendiri agar interaksi pemain tidak memengaruhi state lain selama menu aktif.
- Seluruh nilai dropdown dikonversi menjadi nilai numerik internal sebelum dikirim ke manager.
