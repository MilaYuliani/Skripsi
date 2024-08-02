<?php
ob_start();

// Fungsi untuk memproses kalimat baru dengan skrip Python
if (isset($_POST['proses'])) {
    // Ambil kalimat dari input form
    $kalimat_baru = $_POST['kalimat_baru'];

    // Panggil skrip Python dengan menggunakan shell_exec
    $output = shell_exec("python ner_new.py \"$kalimat_baru\"");
    $tokens = json_decode($output, true);
}

// Fungsi untuk menghapus data dari tabel ner_testing
if (isset($_POST['hapus'])) {
    // Koneksi ke database MySQL
    $conn = mysqli_connect("localhost", "root", "", "databanjir");
    if (!$conn) {
        die("Koneksi gagal: " . mysqli_connect_error());
    }

    // Hapus data dari tabel ner_testing
    $sql_hapus = "DELETE FROM ner_testing";
    if (mysqli_query($conn, $sql_hapus)) {
        echo "";
    } else {
        echo "" . mysqli_error($conn);
    }

    mysqli_close($conn);
}

// Koneksi ke database MySQL
$conn = mysqli_connect("localhost", "root", "", "databanjir");

// Ambil hasil deteksi dari tabel ner_testing
$sql_ner = "SELECT teks_kata, type_ner FROM ner_testing";
$result_ner = mysqli_query($conn, $sql_ner);
?>

<div class="card-header">
    <div style="display: flex; align-items: center; width: 100%;">
        <form method="post" style="flex: 1; display: flex; align-items: center;">
            <div class="form-group" style="flex: 1; margin-right: 10px;">
                <label for="kalimat_baru">Masukkan Kalimat Baru:</label>
                <input type="text" class="form-control" id="kalimat_baru" name="kalimat_baru" required>
            </div>
            <button type="submit" class="btn btn-primary" name="proses" style="margin-right: 10px;">Ekstrak</button>
        </form>
        <form method="post" style="display: flex;">
            <button type="submit" class="btn btn-danger" name="hapus">Hapus</button>
        </form>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <h4>Hasil NER dari Kalimat Baru</h4>
                <table id="datatable-full" class="basic-datatables table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>Teks Kata</th>
                            <th>Type NER</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        // Menampilkan hasil NER dari kalimat baru
                        if (isset($result_ner)) {
                            while ($row = mysqli_fetch_assoc($result_ner)) {
                                // Tentukan warna berdasarkan tipe entitas
                                $color = '';
                                switch ($row['type_ner']) {
                                    case 'DISASTER':
                                        $color = '#FFCCCC'; // Warna merah lembut
                                        break;
                                    case 'LOCATION':
                                        $color = '#CCCCFF'; // Warna biru lembut
                                        break;
                                    case 'PERSON':
                                        $color = '#CCFFCC'; // Warna hijau lembut
                                        break;
                                    case 'ORGANIZATION':
                                        $color = '#FFFFCC'; // Warna kuning lembut
                                        break;
                                    case 'DAY':
                                        $color = '#FFEBCC'; // Warna oranye lembut
                                        break;
                                    case 'DATE':
                                        $color = '#CCE5FF'; // Warna biru muda
                                        break;
                                    default:
                                        $color = '#FFFFFF'; // Warna putih (default)
                                        break;
                                }
                                ?>
                                <tr>
                                    <td><?= htmlspecialchars($row['teks_kata'], ENT_QUOTES, 'UTF-8'); ?></td>
                                    <td style="background-color: <?= $color; ?>;"><?= htmlspecialchars($row['type_ner'], ENT_QUOTES, 'UTF-8'); ?></td>
                                </tr>
                                <?php
                            }
                        }
                        ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<?php
$title = "ner_testing";
$page_title = "NER Testing";
$content = ob_get_clean();
include 'layout.php'; // File layout.php yang berisi struktur template HTML
?>
