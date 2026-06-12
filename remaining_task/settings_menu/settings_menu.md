# STATUS: FINISHED ✅

# DESCRIPTION

Modul ini bertanggung jawab untuk:

1. Merender menu pengaturan permainan.
2. Mengizinkan pemain mengubah beberapa konfigurasi visual dan perilaku agent.
3. Mengumpulkan konfigurasi yang dipilih pemain.
4. Mengembalikan hasil konfigurasi ke manager.

# WORKFLOW

Manager memanggil modul Settings Menu.

↓

Settings Menu membuat local looping sendiri sehingga UI terkunci pada menu ini.

↓

Pemain mengubah konfigurasi yang tersedia.

↓

Pemain memilih:

- Back

↓

Konfigurasi saat ini dikumpulkan dan dikirim kembali ke manager.

↓

Local looping dihentikan.

↓

Output dikirim kembali ke manager.

# CONFIGURABLE VARIABLES

## Player Color

Merepresentasikan warna pemain.

Nilai:

player_color = (
    red,
    green,
    blue
)

Input:

- RGB Color Picker

---

## Agent Color

Merepresentasikan warna agent.

Nilai:

agent_color = (
    red,
    green,
    blue
)

Input:

- RGB Color Picker


---

## Agent Heuristic Function

Merepresentasikan fungsi heuristik yang digunakan oleh algoritma A* milik agent.

Pilihan (dalam string):

- Euclidean
- Manhattan

# OUTPUT FORMAT

state_dict = {
    "state": int,
    "settings_dict": {
        "player_color": tuple[int, int, int],
        "agent_color": tuple[int, int, int],
        "agent_heuristic": Literal["Euclidean", "Manhattan"]
    }
}

# NOTES

- Modul ini tidak menerima input konfigurasi dari manager.
- Modul ini wajib memiliki local looping sendiri agar interaksi pemain tidak memengaruhi state lain selama menu aktif.
- Modul ini selalu menghasilkan output ketika ditutup.
- Pemilihan heuristik hanya memengaruhi perilaku pathfinding agent.
- Tombol Back berfungsi sebagai tombol keluar dari Settings Menu dan kembali ke Main Menu.