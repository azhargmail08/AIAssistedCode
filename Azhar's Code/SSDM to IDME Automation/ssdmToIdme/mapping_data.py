#!/usr/bin/env python3

# Mapping data from SSDM categories to IDME categories and subcategories
# Format: 
# {
#   "item_name": [
#       {
#           "old_category": "Original SSDM category",
#           "new_category": "New IDME category (full name with number)",
#           "idme_category": "IDME Category dropdown value",
#           "idme_subcategory": "IDME Sub-Category dropdown value"
#       },
#       {
#           # Additional mappings for the same item with different categories
#       }
#   ]
# }

ssdm_to_idme_mapping = {
    "BEKERJASAMA MENGECAT DINDING": [
        {
            "old_category": "8. SSDM- KERJA-KERJA MENGECAT",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "BERCAKAP DENGAN SOPAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        },
        {
            "old_category": "2. SSDM- ADAB DAN TINGKAH LAKU PELAJAR",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "BERDISIPLIN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "2. IDME - JATI DARI",
            "idme_category": "JATI DIRI",
            "idme_subcategory": "MEMPUNYAI DAYA TAHAN DIRI SECARA FIZIKAL DAN MENTAL YANG BAIK"
        },
        {
            "old_category": "2. SSDM- ADAB DAN TINGKAH LAKU PELAJAR",
            "new_category": "2. IDME - JATI DARI",
            "idme_category": "JATI DIRI",
            "idme_subcategory": "MEMPUNYAI DAYA TAHAN DIRI SECARA FIZIKAL DAN MENTAL YANG BAIK"
        }
    ],
    "BIJAK BERKOMUNIKASI UNTUK MENDAPATKAN MAKLUMAT": [
        {
            "old_category": "5. SSDM- MENYERTAI AKTIVITI DIBAWAH BIMBINGAN DAN KAUNSELING",
            "new_category": "5. IDME - KEPIMPINAN",
            "idme_category": "KEPIMPINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 5)"
        }
    ],
    "SUKA MENOLONG ORANG LAIN": [
        {
            "old_category": "8. SSDM- KERJA-KERJA MENGECAT",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        },
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ],
    "MUDAH BERINTERAKSI ATAU BERGAUL": [
        {
            "old_category": "5. SSDM- MENYERTAI AKTIVITI DIBAWAH BIMBINGAN DAN KAUNSELING",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "MOP LANTAI": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENYUSUN MEJA/PERABOT": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENYUSUN KEMAS MEJA": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENYUSUN DAN MENCANTIK KAN KAWASAN TAMAN/LANDSKAP": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENYAPU SAMPAH-SARAP DI SEKELILING KELAS": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENYAPU BILIK-BILIK KHAS": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 4)"
        }
    ],
    "MENYAPA/MEMBERI SALAM KEPADA GURU": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "MENUNJUKKAN KREATIVITI": [
        {
            "old_category": "8. SSDM- KERJA-KERJA MENGECAT",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        },
        {
            "old_category": "5. SSDM- MENYERTAI AKTIVITI DIBAWAH BIMBINGAN DAN KAUNSELING",
            "new_category": "5. IDME - KEPIMPINAN",
            "idme_category": "KEPIMPINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 5)"
        },
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MENOLONG DAN MENGAWAL KELAS SEMASA GURU TIADA": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "5. IDME - KEPIMPINAN",
            "idme_category": "KEPIMPINAN",
            "idme_subcategory": "MERANCANG, MENGURUS, MEMIMPIN DAN MENGAWAL SESUATU AKTIVITI ATAU PROGRAM DALAM DAN LUAR BILIK DARJAH"
        }
    ],
    "MENJADI FASILATATOR": [
        {
            "old_category": "5. SSDM- MENYERTAI AKTIVITI DIBAWAH BIMBINGAN DAN KAUNSELING",
            "new_category": "5. IDME - KEPIMPINAN",
            "idme_category": "KEPIMPINAN",
            "idme_subcategory": "MERANCANG, MENGURUS, MEMIMPIN DAN MENGAWAL SESUATU AKTIVITI ATAU PROGRAM DALAM DAN LUAR BILIK DARJAH"
        }
    ],
    "MENGUTIP SAMPAH-SARAP YANG ADA": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENGHORMATI PENDAPAT ORANG LAIN": [
        {
            "old_category": "5. SSDM- MENYERTAI AKTIVITI DIBAWAH BIMBINGAN DAN KAUNSELING",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENGHARGAI ORANG LAIN SERTA MENJAGA SENSITIVITI ANTARA KAUM DAN ETNIK"
        }
    ],
    "MENGHIAS BILIK": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENGEMOP BILIK": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMOTONG RUMPUT YANG PANJANG": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBUANG DEBU/HABUK DI CERMIN/MEJA/DINDING": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBERSIHKAN PAPAN HITAM": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBERSIHKAN MEJA/PERABOT YANG BERDEBU": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBANTU MENYIRAM POKOK BUNGA": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBANTU MENYAPU DAUN-DAUN KERING": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBANTU MENGEMAS SEMULA BARANG YANG DIGUNAKAN": [
        {
            "old_category": "8. SSDM- KERJA-KERJA MENGECAT",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        },
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MEMBANTU MENGANGKAT BUKU/BARANG GURU": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "MEMBANTU GURU MENGAMBIL KEHADIRAN PELAJAR": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ],
    "MEMBANTU GURU JIKA MEMERLUKAN BANTUAN": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ],
    "MEMBANTU GURU JIKA ADA MAJLIS": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ],
    "MENYELESAIKAN TUGASAN MATA PELAJARAN": [
        {
            "old_category": "1. SSDM- SUKARELA MEMBANTU GURU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MELAPOR KES TIDAK BERDISIPLIN": [
        {
            "old_category": "6. SSDM- SUKARELA MELAPOR KES SALAH LAKU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "PRIHATIN DAN MEMPUNYAI RASA TANGGUNGJAWAB UNTUK MEMAKLUMKAN KES SALAH LAKU DALAM DAN LUAR SEKOLAH KEPADA PIHAK SEKOLAH"
        }
    ],
    "MELAPOR KES PONTENG SEKOLAH/KELAS": [
        {
            "old_category": "6. SSDM- SUKARELA MELAPOR KES SALAH LAKU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "PRIHATIN DAN MEMPUNYAI RASA TANGGUNGJAWAB UNTUK MEMAKLUMKAN KES SALAH LAKU DALAM DAN LUAR SEKOLAH KEPADA PIHAK SEKOLAH"
        }
    ],
    "MELAPOR KES MEMBAWA/MENGGUNAKAN BARANG TERLARANG": [
        {
            "old_category": "6. SSDM- SUKARELA MELAPOR KES SALAH LAKU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "PRIHATIN DAN MEMPUNYAI RASA TANGGUNGJAWAB UNTUK MEMAKLUMKAN KES SALAH LAKU DALAM DAN LUAR SEKOLAH KEPADA PIHAK SEKOLAH"
        }
    ],
    "MELAPOR KES MASALAH SOSIAL YANG SERIUS": [
        {
            "old_category": "6. SSDM- SUKARELA MELAPOR KES SALAH LAKU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "PRIHATIN DAN MEMPUNYAI RASA TANGGUNGJAWAB UNTUK MEMAKLUMKAN KES SALAH LAKU DALAM DAN LUAR SEKOLAH KEPADA PIHAK SEKOLAH"
        }
    ],
    "MELAPOR KES LEWAT KE SEKOLAH": [
        {
            "old_category": "6. SSDM- SUKARELA MELAPOR KES SALAH LAKU",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "PRIHATIN DAN MEMPUNYAI RASA TANGGUNGJAWAB UNTUK MEMAKLUMKAN KES SALAH LAKU DALAM DAN LUAR SEKOLAH KEPADA PIHAK SEKOLAH"
        }
    ],
    "MELAKUKAN DENGAN PENUH SEMANGAT": [
        {
            "old_category": "8. SSDM- KERJA-KERJA MENGECAT",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 4)"
        },
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "DATANG AWAL KE SEKOLAH": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENGHADIRKAN DIRI SECARA KONSISTEN KE SEKOLAH/AKTIVIT/PROGRAM KOKURIKULUM"
        }
    ],
    "BERPAKAIAN KEMAS": [
        {
            "old_category": "SAHSIAH DI SEKOLAH",
            "new_category": "8. IDME - PENAMPILAN DIRI",
            "idme_category": "PENAMPILAN DIRI",
            "idme_subcategory": "MEMAKAI PAKAIAN SERAGAM SEKOLAH/PAKAIAN KOKURIKULUM/PAKAIAN SUKAN/PAKAIAN UNIT BERUNIFORM YANG KEMAS, SOPAN, BERSIH DAN LENGKAP MENGIKUT PERATURAN SEKOLAH"
        },
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "8. IDME - PENAMPILAN DIRI",
            "idme_category": "PENAMPILAN DIRI",
            "idme_subcategory": "MEMAKAI PAKAIAN SERAGAM SEKOLAH/PAKAIAN KOKURIKULUM/PAKAIAN SUKAN/PAKAIAN UNIT BERUNIFORM YANG KEMAS, SOPAN, BERSIH DAN LENGKAP MENGIKUT PERATURAN SEKOLAH"
        }
    ],
    "Good Behavior": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "MENOLONG MEMBUANG SAMPAH": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "1. IDME - ADAB DAN BERBUDI BAHASA",
            "idme_category": "ADAB DAN BERBUDI BAHASA",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 1)"
        }
    ],
    "MEMBERSIHKAN PAPAN PUTIH": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMOHON MAAF BILA MELAKUKAN KESALAHAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MENEPATI MASA": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MENGAJAR RAKAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MEMBANTU GURU MEMASANG DAN MENGEMAS ALAT SIARAYA": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ],
    "MEMBERSIH KELAS": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 4)"
        }
    ],
    "PENYERTAAN AKTIVITI PERINGKAT ANTARABANGSA": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 7)"
        }
    ],
    "PENYERTAAN AKTIVITI PERINGKAT KEBANGSAAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 7)"
        }
    ],
    "PENYERTAAN AKTIVITI PERINGKAT NEGERI": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 7)"
        }
    ],
    "PENYERTAAN AKTIVITI PERINGKAT DAERAH": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 7)"
        }
    ],
    "PENYERTAAN AKTIVITI PERINGKAT SEKOLAH": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 7)"
        }
    ],
    "GOTONG ROYONG MEMBERSIHKAN KAWASAN SEKOLAH": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "GOTONG ROYONG MEMBERSIHKAN KAWASAN SEKOLAH": [
        {
            "old_category": "7. SSDM- MEMBANTU MELAKSANA KERJA-KERJA LANDSKAP / TAMAN",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MEMBERSIHKAN BILIK-BILIK KHAS": [
        {
            "old_category": "3. SSDM- MEMBANTU MENGEMAS / MENYUSUN ATUR BILIK-BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENGHIAS KELAS": [
        {
            "old_category": "4. SSDM- MEMBERSIH KAWASAN / BILIK KHAS",
            "new_category": "4. IDME - KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_category": "KEBERSIHAN, KECERIAAN DAN KELESTARIAN SEKOLAH",
            "idme_subcategory": "MENJAGA KELESTARIAN, KEBERSIHAN DAN MENGGALAKKAN KECERIAAN SEKOLAH"
        }
    ],
    "MENGIKUTI PROGRAM PERINGKAT SEKOLAH SECARA BERAMAI-RAMAI": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "7. IDME - KEHADIRAN AKTIVITI",
            "idme_category": "KEHADIRAN AKTIVITI",
            "idme_subcategory": "MENGHADIRKAN DIRI SECARA KONSISTEN KE SEKOLAH/AKTIVIT/PROGRAM KOKURIKULUM"
        }
    ],
    "MENYIAPKAN LATIHAN@ KERJA SEKOLAH DALAM MASA YANG DITETAPKAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "MELENGKAPKAN TUGASAN YANG DIBERIKAN": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "6. IDME - KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_category": "KEBERTANGGUNGJAWABAN DAN KEPRIHATINAN",
            "idme_subcategory": "MENJADI PENDORONG DAN SURI TELADAN KEPADA ORANG LAIN (IDME - 6)"
        }
    ],
    "HADIR SEKOLAH": [
        {
            "old_category": "2. SSDM- MENZAHIRKAN MANA-MANA AMALAN BAIK",
            "new_category": "3. IDME - TOLONG-MENOLONG",
            "idme_category": "TOLONG-MENOLONG",
            "idme_subcategory": "MENAWARKAN DAN MEMBERI BANTUAN DALAM BENTUK TENAGA, KEPAKARAN, KEMAHIRAN ATAU KHIDMAT NASIHAT YANG BERSESUAIAN KEPADA WARGA SEKOLAH DAN ORANG LAIN"
        }
    ]
}
