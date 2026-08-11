BANGUN ULANG APLIKASI SAYA DARI NOL.

Nama aplikasi:

DELUXY.Ai

Tagline:

AI ENGINEERING CAD GENERATOR

========================================================
KONSEP UTAMA
========================================================

Saya TIDAK MAU menggunakan Google Gemini.

Hapus seluruh dependency:

google-generativeai

Jangan gunakan Gemini sama sekali.

Gunakan OpenAI API sebagai AI ENGINE.

Arsitektur aplikasi:

USER
 ↓
DELUXY.Ai CHAT / PROMPT
 ↓
OPENAI GPT
 ↓
STRUCTURED CAD SPECIFICATION
 ↓
LOCAL CAD ENGINE
 ↓
CADQUERY / OPENCASCADE
 ↓
REAL 3D CAD SOLID
 ↓
3D VIEWER
 ↓
STEP / STL

PENTING:

GPT BUKAN pembuat gambar CAD.

GPT hanya bertugas:

1. memahami bahasa manusia
2. menentukan jenis komponen
3. mengambil parameter engineering
4. menjelaskan hasil
5. meminta klarifikasi jika parameter penting belum tersedia
6. memberikan rekomendasi engineering secara tekstual

Geometry CAD HARUS dibuat oleh CADQuery/OpenCascade.

========================================================
OPENAI
========================================================

Gunakan package:

openai

Gunakan OpenAI API.

API key harus dibaca dari:

st.secrets["OPENAI_API_KEY"]

atau:

os.environ.get("OPENAI_API_KEY")

JANGAN pernah hard-code API key.

Buat fungsi:

get_openai_client()

dan:

analyze_cad_request()

Gunakan model OpenAI yang tersedia melalui API.

Jangan membuat dependency ke Gemini.

========================================================
AI ENGINE
========================================================

GPT harus bertindak sebagai:

DELUXY Engineering AI Assistant.

System instruction:

"You are DELUXY.Ai Engineering CAD Assistant.

Your job is to convert natural-language engineering requests into structured CAD specifications.

You must never directly generate fake geometry.

You must return structured parameters.

You must distinguish between:
gear
shaft
stepped_shaft
cylinder
bearing
pulley
bolt
nut
flange

If the user asks for a gear, it MUST remain a gear.

Never convert a gear into a cylinder.

If an important engineering parameter is missing, identify the missing parameter.

Do not silently invent critical dimensions.

For common standard values, you may suggest reasonable defaults but clearly mark them as defaults."

========================================================
STRUCTURED OUTPUT
========================================================

AI response harus berupa structured JSON.

Format:

{
  "component_type": "gear",
  "confidence": 0.98,
  "needs_clarification": false,
  "missing_parameters": [],
  "parameters": {
      "teeth": 24,
      "module": 2.0,
      "pressure_angle": 20.0,
      "thickness": 8.0,
      "bore_diameter": 10.0
  },
  "material": "Steel",
  "units": "mm",
  "engineering_notes": [
      "Spur gear",
      "20 degree pressure angle"
  ],
  "answer": "Saya akan membuat spur gear 24 gigi..."
}

Jangan mengembalikan Markdown JSON.

Jangan mengembalikan kode.

Jangan mengembalikan gambar.

Hanya structured data.

========================================================
COMPONENT CLASSIFIER
========================================================

Walaupun GPT digunakan sebagai AI, buat juga local safety classifier.

Jika user menulis:

gear
roda gigi
spur gear
spur
gigi

maka local classifier HARUS memprioritaskan:

component_type = gear

Jika:

shaft
poros

maka:

component_type = shaft

Jika:

stepped shaft
poros bertingkat

maka:

component_type = stepped_shaft

Jika:

cylinder
silinder

maka:

component_type = cylinder

Local classifier digunakan untuk mencegah GPT salah memilih geometry.

Contoh:

User:

"Buat gear 24 gigi module 2"

Tidak boleh menjadi:

cylinder

Tidak boleh menjadi:

shaft

HARUS:

gear

========================================================
GEAR ENGINE
========================================================

Gear harus menjadi fitur utama aplikasi.

Buat SPUR GEAR PARAMETRIK.

Parameter:

teeth
module
pressure_angle
thickness
bore_diameter

Contoh:

"Buat gear 24 gigi module 2 tebal 8mm bore 10mm"

harus menghasilkan:

teeth = 24
module = 2
pressure_angle = 20
thickness = 8
bore_diameter = 10

Geometry:

pitch diameter = module × teeth

addendum = module

dedendum = 1.25 × module

Buat root circle.

Buat individual teeth.

Buat outer tooth profile.

Buat center bore.

Lakukan boolean union.

Lakukan boolean cut untuk bore.

Hasil akhir HARUS merupakan actual CAD solid.

JANGAN menggunakan cylinder sebagai pengganti gear.

JANGAN membuat gambar 2D.

JANGAN membuat PNG sebagai model.

Jika memungkinkan gunakan involute tooth profile.

Jika involute terlalu kompleks untuk versi awal, buat parametrik tooth profile yang stabil terlebih dahulu.

Namun setiap tooth HARUS merupakan bagian dari solid.

========================================================
SHAFT
========================================================

Support:

shaft

Parameter:

diameter
length
bore_diameter

Contoh:

"Buat poros diameter 20mm panjang 100mm"

hasil:

cylindrical shaft

Jika ada bore:

buat hollow shaft.

========================================================
STEPPED SHAFT
========================================================

Support:

stepped shaft

poros bertingkat

Parameter:

overall_length

section lengths

section diameters

Contoh:

"Buat poros bertingkat panjang 150mm diameter 20mm, 30mm dan 15mm."

Buat actual stepped shaft.

========================================================
CYLINDER
========================================================

Parameter:

diameter
length
bore_diameter

Buat actual cylinder solid menggunakan CadQuery.

========================================================
CAD ENGINE
========================================================

Gunakan:

CadQuery
OpenCascade

CadQuery adalah geometry engine.

GPT tidak membuat geometry.

Semua geometry harus dibuat secara deterministik berdasarkan parameter.

========================================================
3D VIEWER
========================================================

Buat interactive 3D viewer.

Gunakan Plotly atau viewer 3D lain yang kompatibel dengan Streamlit.

Viewer harus:

rotate
zoom
pan

Model harus berasal dari tessellation actual CAD solid.

Jangan gunakan gambar AI sebagai preview.

========================================================
CHAT EXPERIENCE
========================================================

UI harus terasa seperti AI engineering assistant.

Buat:

Chat input

User message

AI response

CAD generation status

3D model

Engineering parameters

Export buttons

Contoh:

USER:

"Buat gear 24 gigi module 2 bore 10mm tebal 8mm."

AI:

"Siap. Saya mendeteksi spur gear dengan:
24 gigi
module 2
pressure angle 20°
tebal 8mm
bore 10mm.

Saya akan membuat model CAD parametrik."

Kemudian:

GENERATING CAD...

Lalu model 3D muncul.

========================================================
PARAMETER EDITOR
========================================================

Setelah model dibuat, tampilkan parameter editor.

Untuk gear:

Jumlah Gigi
Module
Pressure Angle
Thickness
Bore Diameter

User dapat mengubah angka.

Tombol:

REBUILD CAD

Jika user mengubah:

24 gigi → 32 gigi

engine harus benar-benar membuat gear baru dengan 32 gigi.

========================================================
MATERIAL
========================================================

Support:

Steel
Stainless Steel
Aluminium
Brass
Copper
Titanium
Plastic

Material minimal digunakan untuk:

display
density
estimated weight

========================================================
ENGINEERING INFORMATION
========================================================

Untuk gear tampilkan:

Number of teeth
Module
Pitch diameter
Outside diameter
Root diameter
Pressure angle
Thickness
Bore diameter

Hitung:

pitch_diameter = module × teeth

outside_diameter = pitch_diameter + 2 × module

root_diameter = pitch_diameter - 2 × 1.25 × module

Berikan estimasi:

volume
mass

berdasarkan density material.

========================================================
EXPORT
========================================================

Sediakan:

DOWNLOAD STEP

DOWNLOAD STL

STEP harus berasal dari CadQuery/OpenCascade.

STL harus berasal dari actual CAD solid.

========================================================
ERROR HANDLING
========================================================

Jika OpenAI API error:

jangan crash.

Tampilkan:

"AI service unavailable."

Jika OpenAI tidak tersedia, local parser tetap dapat digunakan untuk command sederhana.

Jika CAD geometry error:

tampilkan error engineering.

Contoh:

"Bore 50mm terlalu besar untuk gear ini."

Jangan fallback menjadi cylinder.

========================================================
NO GEMINI
========================================================

Hapus:

google-generativeai

Hapus:

genai

Hapus:

GEMINI_API_KEY

Hapus semua function Gemini.

Gunakan:

OPENAI_API_KEY

========================================================
REQUIREMENTS.TXT
========================================================

Gunakan:

streamlit
numpy
openai
cadquery
plotly

Jangan gunakan:

google-generativeai

========================================================
SECURITY
========================================================

API key hanya boleh berada di:

Streamlit Secrets

atau environment variable.

Jangan tampilkan API key di UI.

Jangan print API key.

Jangan simpan API key ke source code.

========================================================
STREAMLIT
========================================================

Aplikasi harus dapat dijalankan dengan:

streamlit run app.py

========================================================
TEST WAJIB
========================================================

TEST 1:

User:

"Buat gear 24 gigi module 2 bore 10mm tebal 8mm"

Expected:

gear

24 teeth

module 2

pressure angle 20

thickness 8

bore 10

3D model harus memiliki 24 gigi.

========================================================

TEST 2:

User:

"Buat gear 32 gigi module 1.5 bore 8mm"

Expected:

gear

32 teeth

module 1.5

bore 8

3D model harus memiliki 32 gigi.

========================================================

TEST 3:

User:

"Buat poros diameter 20mm panjang 100mm"

Expected:

shaft

diameter 20

length 100

========================================================

TEST 4:

User:

"Buat poros bertingkat panjang 150mm"

Jika diameter section belum diberikan:

AI harus meminta klarifikasi.

Jangan mengarang ukuran critical.

========================================================
PRIORITAS
========================================================

Prioritas pengembangan:

1. STABIL
2. GPT API bekerja
3. Natural language bekerja
4. Gear benar
5. 3D viewer benar
6. STEP export benar
7. STL export benar
8. Parameter editor
9. Engineering calculation
10. Tambah component lain

Jangan membuat terlalu banyak fitur jika fitur utama belum stabil.

========================================================
OUTPUT
========================================================

Berikan FULL:

app.py

requirements.txt

Semua import harus lengkap.

Tidak boleh ada function yang dipanggil tetapi belum dibuat.

Tidak boleh ada placeholder seperti:

# TODO

# implement later

pass

Tidak boleh ada fake geometry.

Pastikan aplikasi dapat langsung dijalankan.

SEKALI LAGI:

DELUXY.Ai menggunakan OPENAI sebagai OTAK.

CADQUERY/OPENCASCADE sebagai TANGAN.

PLOTLY sebagai MATA.

User berbicara dengan DELUXY.Ai melalui chat.

GPT memahami permintaan.

CAD engine membuat geometry.

JANGAN GUNAKAN GEMINI SAMA SEKALI.
